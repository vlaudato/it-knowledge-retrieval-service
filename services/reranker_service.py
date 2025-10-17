from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any
import torch


class RerankerService:
    """Service for reranking retrieved documents using Qwen3-Reranker model"""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-Reranker-0.6B"):
        """
        Initialize the reranker service with Qwen reranker model
        
        Args:
            model_name: Qwen reranker model from HuggingFace
        """
        print(f"Loading reranker model: {model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Get token IDs for yes/no
        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")
        self.max_length = 8192

        prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(suffix, add_special_tokens=False)
        
        print(f"Reranker model loaded successfully on {self.device}")
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on relevance to query using Qwen reranker
        
        Args:
            query: User's question
            documents: List of retrieved documents with 'content' field
            top_k: Number of top documents to return after reranking
            
        Returns:
            Reranked list of documents with updated scores
        """
        if not documents:
            return []
        
        print(f"  Reranking {len(documents)} documents...")
        
        # Prepare query-document pairs for reranking
        pairs = []
        for doc in documents:
            content = doc.get('content', '')
            pairs.append([query, content])
        
        # Get relevance scores from reranker
        scores = self._score_pairs(pairs)
        
        # Attach rerank scores to documents
        for doc, score in zip(documents, scores):
            doc['rerank_score'] = float(score)
        
        # Sort by rerank score (higher is better)
        reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
        
        # Return top-k
        result = reranked[:top_k]
        
        print(f"  Reranked to top {len(result)} documents")
        if result:
            print(f"    Top score: {result[0]['rerank_score']:.3f}")
            print(f"    Lowest score: {result[-1]['rerank_score']:.3f}")
        
        return result
    
    def _format_instruction(self, query: str, doc: str, instruction: str = None) -> str:
        """Format input according to Qwen reranker template"""
        if instruction is None:
            instruction = 'Given a search query, retrieve relevant passages that answer the query'
        return "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}".format(
            instruction=instruction, query=query, doc=doc
        )
    
    def _process_inputs(self, pairs: List[str]):
        """Process inputs with special token handling"""
        inputs = self.tokenizer(
            pairs, 
            padding=False, 
            truncation='longest_first',
            return_attention_mask=False, 
            max_length=self.max_length - len(self.prefix_tokens) - len(self.suffix_tokens)
        )
        
        # Add prefix and suffix tokens
        for i, ele in enumerate(inputs['input_ids']):
            inputs['input_ids'][i] = self.prefix_tokens + ele + self.suffix_tokens
        
        # Pad to max_length and convert to tensors
        inputs = self.tokenizer.pad(
            inputs, 
            padding='max_length', 
            return_tensors="pt", 
            max_length=self.max_length
        )
        
        # Move to device
        for key in inputs:
            inputs[key] = inputs[key].to(self.device)
        
        return inputs
    
    def _score_pairs(self, pairs: List[List[str]]) -> List[float]:
        """
        Score query-document pairs using the reranker model
        
        Args:
            pairs: List of [query, document] pairs
            
        Returns:
            List of relevance scores (0-1, higher is better)
        """
        formatted_pairs = [
            self._format_instruction(query, doc) 
            for query, doc in pairs
        ]
        
        inputs = self._process_inputs(formatted_pairs)
        
        # Compute scores
        with torch.no_grad():
            # Get logits for last token (yes/no prediction)
            batch_scores = self.model(**inputs).logits[:, -1, :]
            
            # Extract yes/no token logits
            true_vector = batch_scores[:, self.token_true_id]
            false_vector = batch_scores[:, self.token_false_id]
            
            # Stack and compute log softmax
            batch_scores = torch.stack([false_vector, true_vector], dim=1)
            batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
            
            # Get probability of "yes" (relevant)
            scores = batch_scores[:, 1].exp().cpu().tolist()
        
        return scores
