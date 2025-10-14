from supabase import create_client, Client
from typing import List, Dict, Any
import numpy as np


class VectorService:
    """Service for querying the Supabase vector database"""
    
    def __init__(self, supabase_url: str, supabase_key: str, table_name: str):
        """
        Initialize the vector service
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            table_name: Name of the vector table
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        print(f"Connected to Supabase vector database")
    
    def search_similar_documents(
        self, 
        query_embedding: List[float], 
        match_count: int = 5,
        match_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using the Postgres function
        
        Args:
            query_embedding: The query embedding vector
            match_count: Number of results to return
            match_threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of matching documents with content and metadata
        """
        try:
            response = self.client.rpc(
                'match_doc',
                {
                    'query_embedding': query_embedding,
                    'match_count': match_count,
                    'match_threshold': match_threshold
                }
            ).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            raise