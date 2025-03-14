import logging
from pubmed_crawler import PubMedCrawler
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from datetime import datetime

def format_keywords(keywords):
    formatted = []
    for keyword in keywords:
        if isinstance(keyword, dict):
            if 'DescriptorName' in keyword:
                descriptor = keyword['DescriptorName']
                if 'QualifierName' in keyword:
                    descriptor += f" ({keyword['QualifierName']})"
                formatted.append(descriptor)
        else:
            formatted.append(str(keyword))
    return sorted(formatted)

def test_complete_article():
    print("\n=== Test: Complete Article Retrieval ===")
    crawler = PubMedCrawler()
    
    # Test with a recent article about immunotherapy
    pmid = "39335671"  # Example PMID for a recent immunotherapy article
    article = crawler.get_article_by_pmid(pmid)
    
    if article:
        print("\nAbstract")
        print("=" * 80)  # Add a separator line
        print(article['abstract'])
        print("=" * 80)  # Add a separator line
    else:
        print(f"Article with PMID {pmid} not found")

def test_search_articles():
    print("\n=== Test 1: Basic Search ===")
    crawler = PubMedCrawler()
    query = "diabetes treatment"
    articles = crawler.search_articles(query, max_results=5)
    
    print(f"\nFound {len(articles)} articles for query: {query}")
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Authors: {', '.join(article['authors'])}")
        print(f"Journal: {article['journal']}")
        print(f"URL: {article['url']}")
        print(f"Abstract: {article['abstract'][:200]}...")
        print(f"Keywords: {', '.join(format_keywords(article['keywords']))}")

def test_cached_search():
    print("\n=== Test 2: Cached Search ===")
    crawler = PubMedCrawler()
    query = "diabetes therapy"
    articles = crawler.search_articles(query, max_results=5)
    
    print(f"\nFound {len(articles)} cached articles for query: {query}")
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Authors: {', '.join(article['authors'])}")
        print(f"Journal: {article['journal']}")
        print(f"URL: {article['url']}")
        print(f"Abstract: {article['abstract'][:200]}...")
        print(f"Keywords: {', '.join(format_keywords(article['keywords']))}")

def test_get_article_by_pmid():
    print("\n=== Test 3: Get Article by PMID ===")
    crawler = PubMedCrawler()
    pmid = "38910057"  # Example PMID
    article = crawler.get_article_by_pmid(pmid)
    
    if article:
        print(f"\nRetrieved article with PMID: {pmid}")
        print(f"Title: {article['title']}")
        print(f"Authors: {', '.join(article['authors'])}")
        print(f"Journal: {article['journal']}")
        print(f"Publication Date: {article['publication_date']}")
        print(f"URL: {article['url']}")
        print(f"Abstract: {article['abstract'][:200]}...")
        print(f"Keywords: {', '.join(format_keywords(article['keywords']))}")
    else:
        print(f"Article with PMID {pmid} not found")

def test_semantic_search():
    print("\n=== Test 4: Semantic Search ===")
    crawler = PubMedCrawler()
    query = "novel approaches to cancer immunotherapy"
    articles = crawler.search_articles(query, max_results=5)
    
    print(f"\nFound {len(articles)} semantically relevant articles for query: {query}")
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Similarity Score: {article['similarity_score']:.3f}")
        print(f"URL: {article['url']}")

def test_error_handling():
    print("\n=== Test 5: Error Handling ===")
    crawler = PubMedCrawler()
    
    # Test with invalid PMID
    print("\nTesting invalid PMID:")
    article = crawler.get_article_by_pmid("invalid_pmid")
    print(f"Result: {'Article not found' if not article else 'Unexpectedly found article'}")
    
    # Test with empty query
    print("\nTesting empty query:")
    articles = crawler.search_articles("", max_results=5)
    print(f"Result: {'No articles found' if not articles else 'Unexpectedly found articles'}")

def main():
    print("Starting Medical Journal Crawler Tests...")
    
    try:
        test_complete_article()  # Add the new test first
        test_search_articles()
        test_cached_search()
        test_get_article_by_pmid()
        test_semantic_search()
        test_error_handling()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    main() 