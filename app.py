from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService
from services.llm_service import LLMService
import traceback

app = Flask(__name__)
CORS(app)

embedding_service = None
vector_service = None
llm_service = None


def initialize_services():
    """Initialize all services with configuration"""
    global embedding_service, vector_service, llm_service
    
    print("Initializing services...")

    # Validate configuration
    Config.validate()
    
    # Initialize services
    embedding_service = EmbeddingService(Config.EMBEDDING_MODEL)
    vector_service = VectorService(
        Config.SUPABASE_URL,
        Config.SUPABASE_KEY,
        Config.VECTOR_TABLE_NAME
    )
    llm_service = LLMService(Config.OLLAMA_BASE_URL, Config.LLM_MODEL)
    
    print("All services initialized successfully!")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'IT Knowledge Retrieval Service',
        'version': '1.0.0'
    }), 200


@app.route('/api/query', methods=['POST'])
def query():
    """
    Main endpoint for querying the RAG system
    
    Expected JSON body:
    {
        "question": "Your question here",
        "match_count": 5,  # optional
        "match_threshold": 0.7  # optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: question'
            }), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question cannot be empty'
            }), 400
        
        match_count = data.get('match_count', Config.MATCH_COUNT)
        match_threshold = data.get('match_threshold', Config.MATCH_THRESHOLD)
        
        print(f"\n{'='*60}")
        print(f"Processing query: {question}")
        print(f"{'='*60}")
        
        print("Step 1: Generating query embedding...")
        query_embedding = embedding_service.generate_embedding(question)
        print(f"Generated embedding (dimension: {len(query_embedding)})")

        print(f"\nStep 2: Searching for similar documents...")
        print(f"  Parameters: match_count={match_count}, match_threshold={match_threshold}")
        similar_docs = vector_service.search_similar_documents(
            query_embedding,
            match_count=match_count,
            match_threshold=match_threshold
        )
        print(f"Found {len(similar_docs)} relevant documents")
        if similar_docs:
            print(f"  First result similarity: {similar_docs[0].get('similarity', 'N/A')}")
        
        if not similar_docs:
            return jsonify({
                'success': True,
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': [],
                'message': 'No matching documents found'
            }), 200
        
        print(f"\nStep 3: Generating answer with LLM...")
        answer = llm_service.generate_answer(question, similar_docs)
        print(f"Answer generated successfully")

        response = {
            'success': True,
            'answer': answer,
            'sources': similar_docs,
            'metadata': {
                'question': question,
                'num_sources': len(similar_docs),
                'match_threshold': match_threshold
            }
        }
        
        print(f"\n{'='*60}")
        print("Query processed successfully!")
        print(f"{'='*60}\n")
        
        return jsonify(response), 200
        
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'An error occurred processing your request',
            'details': str(e) if Config.FLASK_ENV == 'development' else None
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    try:
        initialize_services()
        
        print(f"\n{'='*60}")
        print(f"Starting Flask server on port {Config.PORT}...")
        print(f"Environment: {Config.FLASK_ENV}")
        print(f"{'='*60}\n")
        
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=(Config.FLASK_ENV == 'development')
        )
        
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        print(traceback.format_exc())
        exit(1)