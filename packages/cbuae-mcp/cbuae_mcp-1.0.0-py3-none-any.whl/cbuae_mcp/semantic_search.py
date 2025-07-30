"""
Semantic search engine for CBUAE policies using sentence transformers.
Provides enterprise-grade search capabilities beyond simple fuzzy matching.
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CBUAESemanticSearch:
    """
    Semantic search engine for CBUAE compliance policies.
    Uses lightweight sentence transformers for enterprise deployment.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embeddings = {}
        self.policy_texts = {}
        self.embeddings_file = "policy_embeddings.pkl"
        self.initialized = False
        
        # Try to initialize the model
        self._try_initialize_model()
    
    def _try_initialize_model(self):
        """Try to initialize the sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.initialized = True
            logger.info(f"Semantic search initialized with model: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not available. Semantic search disabled.")
            self.initialized = False
        except Exception as e:
            logger.warning(f"Failed to initialize semantic search: {e}")
            self.initialized = False
    
    def is_available(self) -> bool:
        """Check if semantic search is available."""
        return self.initialized
    
    def build_embeddings(self, policy_db: Dict[str, Any]) -> bool:
        """Build embeddings for all policies in the database."""
        if not self.initialized:
            logger.warning("Cannot build embeddings - model not initialized")
            return False
        
        try:
            logger.info("Building semantic embeddings for policies...")
            
            # Prepare texts for embedding
            policy_texts = []
            policy_ids = []
            
            for policy_id, policy_data in policy_db.items():
                # Combine title and text for better semantic understanding
                combined_text = f"{policy_data.get('title', '')} {policy_data.get('text', '')}"
                
                # Also include key terms if available
                if 'key_terms' in policy_data:
                    key_terms = ' '.join(policy_data['key_terms'])
                    combined_text += f" {key_terms}"
                
                policy_texts.append(combined_text)
                policy_ids.append(policy_id)
                self.policy_texts[policy_id] = combined_text
            
            # Generate embeddings
            embeddings = self.model.encode(policy_texts, show_progress_bar=True)
            
            # Store embeddings
            for i, policy_id in enumerate(policy_ids):
                self.embeddings[policy_id] = embeddings[i]
            
            # Save embeddings to disk
            self._save_embeddings()
            
            logger.info(f"Built embeddings for {len(policy_ids)} policies")
            return True
            
        except Exception as e:
            logger.error(f"Error building embeddings: {e}")
            return False
    
    def _save_embeddings(self):
        """Save embeddings to disk for persistence."""
        try:
            embedding_data = {
                'embeddings': self.embeddings,
                'policy_texts': self.policy_texts,
                'model_name': self.model_name,
                'created_date': datetime.now().isoformat()
            }
            
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(embedding_data, f)
                
            logger.info(f"Saved embeddings to {self.embeddings_file}")
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
    
    def _load_embeddings(self) -> bool:
        """Load embeddings from disk."""
        try:
            if not os.path.exists(self.embeddings_file):
                return False
                
            with open(self.embeddings_file, 'rb') as f:
                embedding_data = pickle.load(f)
            
            # Verify model compatibility
            if embedding_data.get('model_name') != self.model_name:
                logger.warning("Model mismatch - rebuilding embeddings")
                return False
            
            self.embeddings = embedding_data['embeddings']
            self.policy_texts = embedding_data['policy_texts']
            
            logger.info(f"Loaded embeddings for {len(self.embeddings)} policies")
            return True
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """
        Perform semantic search for policies.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of search results with similarity scores
        """
        if not self.initialized:
            return []
        
        # Load embeddings if not already loaded
        if not self.embeddings:
            if not self._load_embeddings():
                logger.warning("No embeddings available for search")
                return []
        
        try:
            # Encode the query
            query_embedding = self.model.encode([query])
            
            # Calculate similarities
            results = []
            for policy_id, policy_embedding in self.embeddings.items():
                similarity = self._cosine_similarity(query_embedding[0], policy_embedding)
                
                if similarity >= min_similarity:
                    results.append({
                        'policy_id': policy_id,
                        'similarity_score': float(similarity),
                        'search_type': 'semantic'
                    })
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def hybrid_search(self, query: str, fuzzy_results: List[Dict], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Combine semantic search with fuzzy search results.
        
        Args:
            query: Search query
            fuzzy_results: Results from fuzzy matching
            top_k: Number of results to return
            
        Returns:
            Combined and ranked results
        """
        semantic_results = self.search(query, top_k=top_k)
        
        # Combine results
        combined_results = {}
        
        # Add fuzzy results
        for result in fuzzy_results:
            policy_id = result.get('policy_id')
            if policy_id:
                combined_results[policy_id] = {
                    **result,
                    'fuzzy_score': result.get('fuzzy_score', 0),
                    'semantic_score': 0.0,
                    'combined_score': result.get('fuzzy_score', 0) * 0.4  # Weight fuzzy at 40%
                }
        
        # Add semantic results
        for result in semantic_results:
            policy_id = result['policy_id']
            semantic_score = result['similarity_score']
            
            if policy_id in combined_results:
                # Update existing result
                combined_results[policy_id]['semantic_score'] = semantic_score
                combined_results[policy_id]['combined_score'] = (
                    combined_results[policy_id]['fuzzy_score'] * 0.4 +
                    semantic_score * 0.6  # Weight semantic at 60%
                )
            else:
                # New semantic result
                combined_results[policy_id] = {
                    'policy_id': policy_id,
                    'fuzzy_score': 0.0,
                    'semantic_score': semantic_score,
                    'combined_score': semantic_score * 0.6,
                    'search_type': 'semantic'
                }
        
        # Sort by combined score
        final_results = list(combined_results.values())
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return final_results[:top_k]
    
    def get_similar_policies(self, policy_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find policies similar to a given policy."""
        if not self.initialized or policy_id not in self.embeddings:
            return []
        
        policy_embedding = self.embeddings[policy_id]
        similarities = []
        
        for other_id, other_embedding in self.embeddings.items():
            if other_id != policy_id:
                similarity = self._cosine_similarity(policy_embedding, other_embedding)
                similarities.append({
                    'policy_id': other_id,
                    'similarity_score': float(similarity)
                })
        
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:top_k]
    
    def update_embeddings(self, policy_db: Dict[str, Any], force_rebuild: bool = False) -> bool:
        """Update embeddings when policy database changes."""
        if not self.initialized:
            return False
        
        # Check if we need to rebuild
        current_policies = set(policy_db.keys())
        existing_policies = set(self.embeddings.keys()) if self.embeddings else set()
        
        if force_rebuild or current_policies != existing_policies:
            logger.info("Policy database changed - rebuilding embeddings")
            return self.build_embeddings(policy_db)
        
        return True