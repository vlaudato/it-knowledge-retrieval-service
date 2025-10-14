import requests
from typing import List, Dict, Any


class LLMService:
    """Service for generating answers using Ollama LLM"""
    
    def __init__(self, ollama_url: str, model: str = "llama3.2:latest"):
        """
        Initialize the LLM service
        
        Args:
            ollama_url: Ollama API base URL (e.g., http://ollama:11434)
            model: Ollama model to use for generation
        """
        self.ollama_url = ollama_url
        self.model = model
        print(f"LLM service initialized with Ollama model: {model}")
        print(f"Ollama URL: {ollama_url}")
    
    def generate_answer(
        self, 
        question: str, 
        context_documents: List[Dict[str, Any]],
        temperature: float = 1.0
    ) -> str:
        """
        Generate an answer based on the question and retrieved context
        
        Args:
            question: User's question
            context_documents: List of relevant documents from vector search
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated answer
        """
        # Build context from retrieved documents
        context = self._build_context(context_documents)
        
        # Create the prompt
        system_prompt = """
        You are a helpful AI assistant that answers questions based on the provided context.
        Use the context below to answer the user's question accurately and concisely.
        If the context doesn't contain enough information to answer the question, say so honestl and
        reply that you do not know the answer. Base your answers solelz on the provided context.
        Be as concise as possible and trz to answer in maximum two paragraphs."""

        user_prompt = f"""Context:
        {context}

        Question: {question}

        Answer:"""

        try:
            # Combine system prompt and user prompt for Ollama
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=180
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get('response', '').strip()
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            raise
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved documents
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('content')
            if content:
                context_parts.append(f"[Document {i}]\n{content}")
        
        return "\n\n".join(context_parts)
