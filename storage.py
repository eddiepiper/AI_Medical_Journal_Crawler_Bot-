import sqlite3
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleStorage:
    def __init__(self, db_path: str = "data/articles.db"):
        """Initialize the storage with a SQLite database."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create articles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        pmid TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abstract TEXT,
                        authors TEXT,  -- JSON array
                        publication_date TEXT,
                        journal TEXT,
                        url TEXT,
                        query TEXT,    -- Search query that found this article
                        crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create search history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def store_article(self, article: Dict, query: str) -> bool:
        """
        Store an article in the database.
        
        Args:
            article (Dict): Article metadata
            query (str): Search query that found this article
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert authors list to JSON string
                authors_json = json.dumps(article.get('authors', []))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO articles 
                    (pmid, title, abstract, authors, publication_date, journal, url, query, crawled_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    article.get('pmid'),
                    article.get('title'),
                    article.get('abstract'),
                    authors_json,
                    article.get('publication_date'),
                    article.get('journal'),
                    article.get('url'),
                    query
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error storing article: {str(e)}")
            return False

    def get_article(self, pmid: str) -> Optional[Dict]:
        """
        Retrieve an article by its PubMed ID.
        
        Args:
            pmid (str): PubMed ID
            
        Returns:
            Optional[Dict]: Article metadata or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM articles WHERE pmid = ?", (pmid,))
                row = cursor.fetchone()
                
                if row:
                    # Convert row to dictionary
                    columns = [col[0] for col in cursor.description]
                    article = dict(zip(columns, row))
                    
                    # Convert JSON string back to list
                    article['authors'] = json.loads(article['authors'])
                    
                    return article
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving article: {str(e)}")
            return None

    def get_articles_by_query(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve articles matching a search query.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of articles to return
            
        Returns:
            List[Dict]: List of article metadata
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM articles 
                    WHERE query LIKE ? 
                    ORDER BY crawled_at DESC 
                    LIMIT ?
                """, (f"%{query}%", limit))
                
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                
                articles = []
                for row in rows:
                    article = dict(zip(columns, row))
                    article['authors'] = json.loads(article['authors'])
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.error(f"Error retrieving articles by query: {str(e)}")
            return []

    def log_search(self, query: str):
        """Log a search query to track usage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO search_history (query) VALUES (?)",
                    (query,)
                )
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging search: {str(e)}")

    def get_recent_searches(self, limit: int = 10) -> List[Dict]:
        """Get recent search queries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT query, COUNT(*) as count, MAX(timestamp) as last_searched
                    FROM search_history
                    GROUP BY query
                    ORDER BY last_searched DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [
                    {
                        'query': row[0],
                        'count': row[1],
                        'last_searched': row[2]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Error retrieving recent searches: {str(e)}")
            return [] 