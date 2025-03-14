import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import pickle
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the vector store with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Default dimension for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dimension)
        self.articles: List[Dict] = []
        self.data_dir = "data"
        self.index_file = os.path.join(self.data_dir, "faiss_index.bin")
        self.articles_file = os.path.join(self.data_dir, "articles.pkl")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing index and articles if available
        self.load_store()

    def _get_article_embedding(self, article: Dict) -> np.ndarray:
        """Generate embedding for an article."""
        # Combine relevant fields for embedding
        text = f"{article['title']} {article['abstract']} {' '.join(article['authors'])}"
        return self.model.encode([text])[0]

    def add_article(self, article: Dict) -> bool:
        """
        Add an article to the vector store.
        
        Args:
            article (Dict): Article dictionary containing title, abstract, authors, etc.
            
        Returns:
            bool: True if article was added, False if it already exists
        """
        try:
            # Check if article already exists
            if any(a['pmid'] == article['pmid'] for a in self.articles):
                return False

            # Generate embedding
            embedding = self._get_article_embedding(article)
            
            # Add to FAISS index
            self.index.add(np.array([embedding]).astype('float32'))
            
            # Add metadata
            article['added_date'] = datetime.now().isoformat()
            self.articles.append(article)
            
            # Save updated store
            self.save_store()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding article to vector store: {str(e)}")
            return False

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar articles using semantic search.
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Dict]: List of similar articles with their metadata
        """
        try:
            # Generate query embedding
            query_vector = self.model.encode([query])[0]
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array([query_vector]).astype('float32'), 
                min(k, len(self.articles))
            )
            
            # Return matched articles with distances
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx != -1:  # Valid index
                    article = self.articles[idx].copy()
                    article['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity score
                    results.append(article)
                    
            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []

    def save_store(self):
        """Save the current state of the vector store."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)
            
            # Save article metadata
            with open(self.articles_file, 'wb') as f:
                pickle.dump(self.articles, f)
                
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")

    def load_store(self):
        """Load the vector store from disk if it exists."""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.articles_file):
                # Load FAISS index
                self.index = faiss.read_index(self.index_file)
                
                # Load article metadata
                with open(self.articles_file, 'rb') as f:
                    self.articles = pickle.load(f)
                    
                logger.info(f"Loaded vector store with {len(self.articles)} articles")
            else:
                logger.info("No existing vector store found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            # Initialize empty index if load fails
            self.index = faiss.IndexFlatL2(self.dimension)
            self.articles = [] 