from Bio import Entrez
from typing import List, Dict, Optional
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
from vector_store import VectorStore
import re
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedCrawler:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('PUBMED_EMAIL', 'your-email@example.com')
        self.api_key = os.getenv('PUBMED_API_KEY')
        self.vector_store = VectorStore()
        
        Entrez.email = self.email
        if self.api_key:
            Entrez.api_key = self.api_key

    def _extract_abstract(self, article_data: Dict) -> str:
        """
        Extract abstract from article data, handling different XML structures.
        
        Args:
            article_data (Dict): Article data from PubMed
            
        Returns:
            str: Extracted abstract text
        """
        if 'Abstract' not in article_data:
            return ""
            
        abstract_data = article_data['Abstract']
        
        # Handle different abstract structures
        if isinstance(abstract_data, dict):
            abstract_text = ""
            
            # Try to get AbstractText
            if 'AbstractText' in abstract_data:
                abstract_text = abstract_data['AbstractText']
                
                # Handle different types of AbstractText
                if isinstance(abstract_text, str):
                    return abstract_text
                elif isinstance(abstract_text, list):
                    # Handle multiple sections
                    sections = []
                    for text in abstract_text:
                        if isinstance(text, dict):
                            # If it has a Label, include it
                            if 'Label' in text:
                                label = text['Label']
                                content = text.get('#text', '')  # Get the actual text content
                                sections.append(f"{label}: {content}")
                            else:
                                # Try different ways to get the text content
                                content = text.get('#text', text.get('_', ''))
                                if content:
                                    sections.append(content)
                        else:
                            sections.append(str(text))
                    return ' '.join(sections)
                elif isinstance(abstract_text, dict):
                    # Single section with potential label
                    if 'Label' in abstract_text:
                        label = abstract_text['Label']
                        content = abstract_text.get('#text', '')
                        return f"{label}: {content}"
                    else:
                        return abstract_text.get('#text', '')
            
            # If no AbstractText or it's empty, try CopyrightInformation
            if not abstract_text and 'CopyrightInformation' in abstract_data:
                return abstract_data['CopyrightInformation']
                
        elif isinstance(abstract_data, str):
            return abstract_data
            
        return ""

    def _extract_keywords(self, article_data):
        """Extract keywords from article data."""
        keywords = []
        
        # Extract MeSH headings
        if 'MeshHeadingList' in article_data:
            for mesh in article_data['MeshHeadingList']:
                descriptor = str(mesh['DescriptorName'])
                qualifiers = []
                if 'QualifierName' in mesh:
                    for qualifier in mesh['QualifierName']:
                        qualifiers.append(str(qualifier))
                
                if qualifiers:
                    keywords.append(f"{descriptor} ({', '.join(qualifiers)})")
                else:
                    keywords.append(descriptor)
        
        # Extract keyword list
        if 'KeywordList' in article_data:
            for keyword_list in article_data['KeywordList']:
                for keyword in keyword_list:
                    keywords.append(str(keyword))
        
        # Remove duplicates and sort
        keywords = sorted(list(set(keywords)))
        return keywords

    def search_articles(self, query: str, max_results: int = 10, use_cache: bool = True) -> List[Dict]:
        """
        Search for articles on PubMed.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            use_cache (bool): Whether to check cache before querying PubMed
            
        Returns:
            List[Dict]: List of articles with their metadata
        """
        try:
            # First check cache if enabled
            if use_cache:
                cached_results = self.vector_store.search(query, k=max_results)
                if cached_results:
                    logger.info(f"Found {len(cached_results)} cached results for query: {query}")
                    return cached_results

            # If no cached results or cache disabled, search PubMed
            logger.info(f"Searching PubMed for: {query}")
            
            # Format query for PubMed
            search_query = self._format_query(query)
            logger.debug(f"Formatted query: {search_query}")
            
            # First, search for article IDs
            search_results = self._safe_entrez_call(
                Entrez.esearch,
                db="pubmed",
                term=search_query,
                retmax=max_results,
                usehistory="y",
                sort="relevance"
            )
            
            if not search_results.get('IdList'):
                logger.warning(f"No results found for query: {query}")
                return []
            
            # Fetch details for found articles using history
            fetch_handle = self._safe_entrez_call(
                Entrez.efetch,
                db="pubmed",
                rettype="xml",
                webenv=search_results.get('WebEnv'),
                query_key=search_results.get('QueryKey')
            )
            
            fetch_results = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            articles = []
            for article in fetch_results['PubmedArticle']:
                medline = article['MedlineCitation']
                article_data = medline['Article']
                
                # Extract authors
                authors = []
                if 'AuthorList' in article_data:
                    for author in article_data['AuthorList']:
                        if 'LastName' in author and 'ForeName' in author:
                            authors.append(f"{author['LastName']}, {author['ForeName']}")
                        elif 'LastName' in author:
                            authors.append(author['LastName'])
                            
                # Extract abstract using the new method
                abstract = self._extract_abstract(article_data)
                
                # Extract keywords using the new method
                keywords = self._extract_keywords(article_data)
                
                article_info = {
                    'pmid': medline['PMID'],
                    'title': article_data.get('ArticleTitle', '').strip(),
                    'abstract': abstract.strip(),
                    'authors': authors,
                    'journal': article_data.get('Journal', {}).get('Title', '').strip(),
                    'publication_date': self._format_pub_date(article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})),
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{medline['PMID']}/",
                    'keywords': keywords,
                    'publication_type': article_data.get('PublicationTypeList', [])
                }
                
                articles.append(article_info)
                
                # Add to vector store for future queries
                if use_cache:
                    self.vector_store.add_article(article_info)
            
            # Add a small delay to respect NCBI's rate limits
            time.sleep(0.34)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles: {str(e)}")
            return []

    def _format_pub_date(self, pub_date: Dict) -> str:
        """Format publication date from PubMed response."""
        if not pub_date:
            return ""
            
        date_parts = []
        if 'Year' in pub_date:
            date_parts.append(pub_date['Year'])
        if 'Month' in pub_date:
            date_parts.append(pub_date['Month'])
        if 'Day' in pub_date:
            date_parts.append(pub_date['Day'])
            
        return ' '.join(date_parts) if date_parts else ""

    def get_article_by_pmid(self, pmid: str) -> Optional[Dict]:
        """
        Get article details by PubMed ID.
        
        Args:
            pmid (str): PubMed ID
            
        Returns:
            Optional[Dict]: Article metadata if found
        """
        try:
            # Check cache first
            cached_articles = [a for a in self.vector_store.articles if a['pmid'] == pmid]
            if cached_articles:
                return cached_articles[0]
            
            # If not in cache, fetch from PubMed
            fetch_handle = self._safe_entrez_call(
                Entrez.efetch,
                db="pubmed",
                id=pmid,
                rettype="xml"
            )
            
            fetch_results = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            if not fetch_results.get('PubmedArticle'):
                return None
                
            article = fetch_results['PubmedArticle'][0]
            medline = article['MedlineCitation']
            article_data = medline['Article']
            
            # Extract authors
            authors = []
            if 'AuthorList' in article_data:
                for author in article_data['AuthorList']:
                    if 'LastName' in author and 'ForeName' in author:
                        authors.append(f"{author['LastName']}, {author['ForeName']}")
                    elif 'LastName' in author:
                        authors.append(author['LastName'])
                        
            # Extract abstract using the new method
            abstract = self._extract_abstract(article_data)
            
            # Extract keywords using the new method
            keywords = self._extract_keywords(article_data)
            
            article_info = {
                'pmid': medline['PMID'],
                'title': article_data.get('ArticleTitle', '').strip(),
                'abstract': abstract.strip(),
                'authors': authors,
                'journal': article_data.get('Journal', {}).get('Title', '').strip(),
                'publication_date': self._format_pub_date(article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})),
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{medline['PMID']}/",
                'keywords': keywords,
                'publication_type': article_data.get('PublicationTypeList', [])
            }
            
            # Add to vector store for future queries
            self.vector_store.add_article(article_info)
            
            return article_info
            
        except Exception as e:
            logger.error(f"Error fetching article {pmid}: {str(e)}")
            return None

    def get_recent_searches(self, limit: int = 10) -> List[Dict]:
        """Get recent search queries."""
        return self.vector_store.get_recent_searches(limit)

    def _format_query(self, query: str) -> str:
        """
        Format a search query for PubMed.
        
        Args:
            query (str): Raw search query
            
        Returns:
            str: Formatted query
        """
        # Remove special characters except spaces and quotes
        query = re.sub(r'[^\w\s"\']', ' ', query)
        
        # Split into terms and encode each term
        terms = query.split()
        encoded_terms = [quote_plus(term) for term in terms]
        
        # Join terms with AND operator
        formatted_query = ' AND '.join(encoded_terms)
        
        # Add date filter for recent articles (last 5 years)
        current_year = datetime.now().year
        date_filter = f"({formatted_query}) AND {current_year-5}:{current_year}[pdat]"
        
        return date_filter 

    def _safe_entrez_call(self, func, **kwargs):
        """
        Safely make an Entrez API call with retries and rate limiting.
        
        Args:
            func: Entrez function to call
            **kwargs: Arguments for the function
            
        Returns:
            Result from the Entrez function
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Add delay between requests
                if attempt > 0:
                    time.sleep(retry_delay * (2 ** attempt))
                
                # Log the API call details
                func_name = func.__name__ if hasattr(func, '__name__') else str(func)
                logger.debug(f"Making Entrez API call: {func_name}")
                logger.debug(f"Parameters: {kwargs}")
                
                # Add tool name and email to kwargs
                kwargs['tool'] = 'MedicalJournalCrawler'
                kwargs['email'] = self.email
                if self.api_key:
                    kwargs['api_key'] = self.api_key
                
                # For efetch, ensure binary mode
                if func == Entrez.efetch:
                    kwargs['retmode'] = 'xml'
                
                handle = func(**kwargs)
                
                if func == Entrez.efetch:
                    # For efetch, return the handle directly
                    return handle
                else:
                    # For other calls (esearch), parse the response
                    result = Entrez.read(handle)
                    handle.close()
                    return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed for {func_name}: {str(e)}")
                    raise
                time.sleep(retry_delay) 