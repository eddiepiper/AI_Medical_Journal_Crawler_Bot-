from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from typing import Dict, List, Tuple
import logging
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import nest_asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable nested event loops
nest_asyncio.apply()

class ArticleSummarizer:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.3,
            openai_api_key=self.openai_api_key
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )

    async def fetch_article_content(self, url: str) -> str:
        """
        Fetch and extract content from a medical journal article URL.
        
        Args:
            url (str): URL of the medical journal article
            
        Returns:
            str: Extracted content from the article
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract main content (adjust selectors based on the journal website structure)
                        content = []
                        
                        # Try to find abstract
                        abstract = soup.find('div', {'class': ['abstract', 'article-abstract']})
                        if abstract:
                            content.append(abstract.get_text())
                            
                        # Try to find main text
                        main_text = soup.find('div', {'class': ['article-body', 'main-content']})
                        if main_text:
                            content.append(main_text.get_text())
                            
                        return ' '.join(content)
                    return ""
        except Exception as e:
            logger.error(f"Error fetching article content: {str(e)}")
            return ""

    async def analyze_articles_with_content(self, articles: List[Dict], question: str) -> Tuple[str, List[Dict]]:
        """
        Analyze articles by fetching their content and answering the question.
        
        Args:
            articles (List[Dict]): List of articles with URLs
            question (str): User's question
            
        Returns:
            Tuple[str, List[Dict]]: Answer and enriched articles
        """
        try:
            # Fetch content for all articles concurrently
            tasks = [self.fetch_article_content(article['url']) for article in articles]
            contents = await asyncio.gather(*tasks)
            
            # Enrich articles with fetched content
            enriched_articles = []
            for article, content in zip(articles, contents):
                if content:
                    article['full_content'] = content
                    enriched_articles.append(article)
            
            # Prepare context from enriched articles
            context = "\n\n".join([
                f"Article {i+1}:\nTitle: {article['title']}\n"
                f"Authors: {', '.join(article['authors'])}\n"
                f"Abstract: {article['abstract']}\n"
                f"Full Content: {article.get('full_content', 'Not available')}\n"
                f"Published: {article['publication_date']}"
                for i, article in enumerate(enriched_articles)
            ])
            
            # Create prompt for detailed analysis
            prompt_template = """Based on the following medical research articles, please provide a comprehensive answer to this question:

Question: {question}

Articles:
{text}

Please structure your response as follows:
1. Direct Answer: Provide a clear, concise answer to the question
2. Key Findings: List the main points from the articles that support your answer
3. Clinical Implications: Discuss practical applications or implications for healthcare
4. Evidence Quality: Comment on the strength of evidence from the articles
5. Limitations: Note any important limitations or gaps in the current research

Use specific citations when referencing findings (e.g., "According to Article 1...").
Focus on providing actionable insights for medical professionals.

Response:"""
            
            prompt = PromptTemplate(
                input_variables=["text", "question"],
                template=prompt_template
            )
            
            # Create and run the chain
            docs = self.text_splitter.create_documents([context])
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="stuff",
                prompt=prompt
            )
            
            # Get the answer
            answer = chain.run(input_documents=docs, question=question)
            
            return answer.strip(), enriched_articles
        except Exception as e:
            logger.error(f"Error analyzing articles: {str(e)}")
            return "Error analyzing articles. Please try again later.", []

    async def format_telegram_message_async(self, articles: List[Dict], query: str) -> str:
        """
        Format multiple articles into a literature review style message (async version).
        
        Args:
            articles (List[Dict]): List of articles with their summaries
            query (str): Question or search query
            
        Returns:
            str: Formatted message for Telegram
        """
        try:
            # Generate answer if it's a question
            if "?" in query:
                answer, enriched_articles = await self.analyze_articles_with_content(articles, query)
                
                message = (
                    f"📚 *Analysis: {query}*\n\n"
                    f"{answer}\n\n"
                    "🔍 *Referenced Articles:*\n\n"
                )
                
                # Use enriched articles if available
                articles_to_format = enriched_articles if enriched_articles else articles
                
            else:
                message = f"📚 *Literature Review: {query}*\n\n"
                articles_to_format = articles
            
            # Add article references
            for i, article in enumerate(articles_to_format, 1):
                authors = ", ".join(article['authors'][:3])
                if len(article['authors']) > 3:
                    authors += " et al."
                
                message += (
                    f"{i}. *{article['title']}*\n"
                    f"   {authors} ({article['publication_date']}) - {article['journal']}\n"
                    f"   [Read Full Paper]({article['url']})\n\n"
                )
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return "Error formatting message. Please try again later."

    def format_telegram_message(self, articles: List[Dict], query: str) -> str:
        """
        Format multiple articles into a literature review style message.
        
        Args:
            articles (List[Dict]): List of articles with their summaries
            query (str): Question or search query
            
        Returns:
            str: Formatted message for Telegram
        """
        try:
            # Create a new event loop for this method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async version and get the result
            message = loop.run_until_complete(
                self.format_telegram_message_async(articles, query)
            )
            
            # Clean up
            loop.close()
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return "Error formatting message. Please try again later." 