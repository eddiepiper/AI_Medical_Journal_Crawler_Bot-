from Bio import Entrez
from typing import List, Dict, Optional
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedCrawler:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('PUBMED_EMAIL', 'your-email@example.com')
        self.api_key = os.getenv('PUBMED_API_KEY')
        Entrez.email = self.email
        if self.api_key:
            Entrez.api_key = self.api_key

    def search_articles(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search PubMed for articles matching the query.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: List of article metadata
        """
        try:
            # Search PubMed
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()

            if not record["IdList"]:
                logger.warning(f"No results found for query: {query}")
                return []

            # Fetch article details
            articles = []
            for pmid in record["IdList"]:
                try:
                    article = self._fetch_article_details(pmid)
                    if article:
                        articles.append(article)
                    time.sleep(0.34)  # Respect NCBI's rate limit
                except Exception as e:
                    logger.error(f"Error fetching article {pmid}: {str(e)}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"Error searching PubMed: {str(e)}")
            return []

    def _fetch_article_details(self, pmid: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific article.
        
        Args:
            pmid (str): PubMed ID
            
        Returns:
            Optional[Dict]: Article details or None if error occurs
        """
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="xml")
            records = Entrez.read(handle)
            handle.close()

            if not records['PubmedArticle']:
                return None

            article = records['PubmedArticle'][0]
            medline_citation = article['MedlineCitation']
            article_info = medline_citation['Article']

            # Extract abstract text
            abstract = ""
            if 'Abstract' in article_info:
                abstract_texts = article_info['Abstract'].get('AbstractText', [])
                if isinstance(abstract_texts, list):
                    abstract = ' '.join(str(text) for text in abstract_texts)
                else:
                    abstract = str(abstract_texts)

            return {
                "pmid": pmid,
                "title": article_info.get('ArticleTitle', ''),
                "abstract": abstract,
                "authors": self._extract_authors(article_info),
                "publication_date": self._extract_publication_date(article_info),
                "journal": article_info.get('Journal', {}).get('Title', ''),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }

        except Exception as e:
            logger.error(f"Error fetching article details for PMID {pmid}: {str(e)}")
            return None

    def _extract_authors(self, article_info: Dict) -> List[str]:
        """Extract author names from article data."""
        authors = []
        try:
            author_list = article_info.get('AuthorList', [])
            for author in author_list:
                last_name = author.get('LastName', '')
                fore_name = author.get('ForeName', '')
                if last_name and fore_name:
                    authors.append(f"{last_name}, {fore_name}")
                elif last_name:
                    authors.append(last_name)
        except Exception as e:
            logger.error(f"Error extracting authors: {str(e)}")
        return authors

    def _extract_publication_date(self, article_info: Dict) -> str:
        """Extract publication date from article data."""
        try:
            pub_date = article_info.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', '')
            month = pub_date.get('Month', '')
            day = pub_date.get('Day', '')
            
            if year:
                date_parts = [year]
                if month:
                    date_parts.append(month)
                if day:
                    date_parts.append(day)
                return " ".join(date_parts)
            return "Date not available"
        except Exception as e:
            logger.error(f"Error extracting publication date: {str(e)}")
            return "Date not available" 