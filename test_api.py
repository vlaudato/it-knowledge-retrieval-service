"""
Simple test script to verify the RAG API is working correctly
"""
import requests
import json


def test_health_check(base_url: str = "http://localhost:5000"):
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Check Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_query(question: str, base_url: str = "http://localhost:5000"):
    """Test the query endpoint"""
    print("\n" + "="*60)
    print("Testing Query Endpoint")
    print("="*60)
    print(f"Question: {question}")
    
    try:
        response = requests.post(
            f"{base_url}/api/query",
            json={"question": question},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAnswer:\n{data.get('answer', 'No answer')}")
            print(f"\nNumber of sources: {len(data.get('sources', []))}")
            
            if data.get('sources'):
                print("\nSources:")
                for i, source in enumerate(data['sources'][:3], 1):
                    print(f"\n  Source {i}:")
                    content = source.get('content', source.get('text', 'N/A'))
                    print(f"  {content[:200]}...")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_embedding(text: str, base_url: str = "http://localhost:5000"):
    """Test the embedding endpoint"""
    print("\n" + "="*60)
    print("Testing Embedding Endpoint")
    print("="*60)
    print(f"Text: {text}")
    
    try:
        response = requests.post(
            f"{base_url}/api/embedding",
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Embedding dimension: {data.get('dimension')}")
            print(f"First 5 values: {data.get('embedding', [])[:5]}")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    BASE_URL = "http://localhost:5000"
    
    print("\n" + "="*60)
    print("RAG API Test Suite")
    print("="*60)
    
    # Test 1: Health check
    health_ok = test_health_check(BASE_URL)
    
    # Test 2: Query endpoint
    test_question = "What is the company policy on remote work?"
    query_ok = test_query(test_question, BASE_URL)
    
    # Test 3: Embedding endpoint
    embedding_ok = test_embedding("Test text for embedding", BASE_URL)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Health Check: {'✓ PASSED' if health_ok else '✗ FAILED'}")
    print(f"Query Endpoint: {'✓ PASSED' if query_ok else '✗ FAILED'}")
    print(f"Embedding Endpoint: {'✓ PASSED' if embedding_ok else '✗ FAILED'}")
    print("="*60 + "\n")
