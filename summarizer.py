from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from typing import Dict, List
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    def summarize_article(self, article: Dict) -> str:
        """
        Summarize a medical article using GPT-4.
        
        Args:
            article (Dict): Article metadata including title and abstract
            
        Returns:
            str: Summarized article
        """
        try:
            # Prepare the text for summarization
            text = f"Title: {article['title']}\n\nAbstract: {article['abstract']}"
            
            # Split text into chunks
            docs = self.text_splitter.create_documents([text])
            
            # Create custom prompt template
            prompt_template = """Please provide a one-sentence summary of this medical research article's key findings.
            Focus on the main conclusion and clinical implications.
            Keep it concise, scientific, and avoid unnecessary details.
            
            Article:
            {text}
            
            One-sentence summary:"""
            
            prompt = PromptTemplate(
                input_variables=["text"],
                template=prompt_template
            )
            
            # Create and run the summarization chain
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="stuff",
                prompt=prompt
            )
            
            summary = chain.run(docs)
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return "Error generating summary. Please try again later."

    def format_telegram_message(self, articles: List[Dict], query: str) -> str:
        """
        Format multiple articles into a literature review style message.
        
        Args:
            articles (List[Dict]): List of articles with their summaries
            query (str): Original search query
            
        Returns:
            str: Formatted message for Telegram
        """
        try:
            message = f"📚 *Literature Review: {query}*\n\n"
            
            for i, article in enumerate(articles, 1):
                authors = ", ".join(article['authors'][:3])
                if len(article['authors']) > 3:
                    authors += " et al."
                
                message += (
                    f"{i}. *{article['title']}*\n"
                    f"   {authors} ({article['publication_date']}) - {article['journal']}\n"
                    f"   Key finding: {article.get('summary', 'No summary available')}\n"
                    f"   [Read Paper]({article['url']})\n\n"
                )
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return "Error formatting message. Please try again later." 