"""
Reranking components for the Agentic RAG library.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .vector_stores import SearchResult
from ..utils.exceptions import RetrievalError
from ..utils.logging import LoggerMixin


@dataclass
class RerankingResult:
    """Result from reranking operation."""
    results: List[SearchResult]
    reranking_time: float
    original_order: List[int]
    reranked_order: List[int]
    score_changes: List[float]


class BaseReranker(ABC, LoggerMixin):
    """Abstract base class for all rerankers."""
    
    def __init__(self, **kwargs):
        """Initialize the reranker."""
        pass
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> RerankingResult:
        """Rerank search results based on query relevance."""
        pass


class CrossEncoderReranker(BaseReranker):
    """Cross-encoder based reranker for improved relevance scoring."""
    
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        batch_size: int = 32,
        **kwargs
    ):
        """
        Initialize cross-encoder reranker.
        
        Args:
            model_name: HuggingFace model name for cross-encoder
            batch_size: Batch size for processing
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the cross-encoder model."""
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            self.logger.info(f"Initialized CrossEncoder: {self.model_name}")
        except ImportError:
            self.logger.warning("sentence-transformers not available, using fallback scoring")
            self._model = None
        except Exception as e:
            self.logger.error(f"Failed to initialize CrossEncoder: {e}")
            self._model = None
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> RerankingResult:
        """Rerank results using cross-encoder scoring."""
        start_time = time.time()
        
        if not results:
            return RerankingResult(
                results=[],
                reranking_time=0.0,
                original_order=[],
                reranked_order=[],
                score_changes=[]
            )
        
        try:
            # Store original order and scores
            original_order = list(range(len(results)))
            original_scores = [r.score for r in results]
            
            if self._model is not None:
                # Use cross-encoder for reranking
                new_scores = await self._cross_encoder_score(query, results)
            else:
                # Fallback to simple text similarity
                new_scores = await self._fallback_score(query, results)
            
            # Create reranked results
            reranked_results = []
            for i, (result, new_score) in enumerate(zip(results, new_scores)):
                new_result = SearchResult(
                    document=result.document,
                    score=new_score,
                    rank=0  # Will be updated after sorting
                )
                reranked_results.append(new_result)
            
            # Sort by new scores
            reranked_results.sort(key=lambda x: x.score, reverse=True)
            
            # Update ranks
            for i, result in enumerate(reranked_results):
                result.rank = i + 1
            
            # Apply top_k if specified
            if top_k is not None:
                reranked_results = reranked_results[:top_k]
            
            # Calculate metrics using document IDs for matching
            reranked_order = []
            for r in reranked_results:
                for i, orig_result in enumerate(results):
                    if r.document.id == orig_result.document.id:
                        reranked_order.append(i)
                        break
            score_changes = [new - orig for new, orig in zip(new_scores, original_scores)]
            
            reranking_time = time.time() - start_time
            
            self.logger.debug(f"Reranked {len(results)} results in {reranking_time:.3f}s")
            
            return RerankingResult(
                results=reranked_results,
                reranking_time=reranking_time,
                original_order=original_order,
                reranked_order=reranked_order,
                score_changes=score_changes
            )
            
        except Exception as e:
            raise RetrievalError(f"Cross-encoder reranking failed: {e}") from e
    
    async def _cross_encoder_score(self, query: str, results: List[SearchResult]) -> List[float]:
        """Score query-document pairs using cross-encoder."""
        # Prepare query-document pairs
        pairs = [(query, result.document.content) for result in results]
        
        # Score in batches
        all_scores = []
        for i in range(0, len(pairs), self.batch_size):
            batch_pairs = pairs[i:i + self.batch_size]
            batch_scores = self._model.predict(batch_pairs)
            all_scores.extend(batch_scores.tolist())
        
        return all_scores
    
    async def _fallback_score(self, query: str, results: List[SearchResult]) -> List[float]:
        """Fallback scoring using simple text similarity."""
        query_words = set(query.lower().split())
        scores = []
        
        for result in results:
            content_words = set(result.document.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            score = overlap / max(len(query_words), 1)
            scores.append(score)
        
        return scores


class ColBERTReranker(BaseReranker):
    """ColBERT-based reranker for fine-grained relevance scoring."""
    
    def __init__(
        self,
        model_name: str = "colbert-ir/colbertv2.0",
        max_length: int = 512,
        **kwargs
    ):
        """
        Initialize ColBERT reranker.
        
        Args:
            model_name: ColBERT model name
            max_length: Maximum sequence length
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        self.max_length = max_length
        self._model = None
        self._tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the ColBERT model."""
        try:
            # This is a simplified implementation
            # In practice, you'd use the official ColBERT library
            from transformers import AutoTokenizer, AutoModel
            self._tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self._model = AutoModel.from_pretrained("bert-base-uncased")
            self.logger.info(f"Initialized ColBERT-style model")
        except ImportError:
            self.logger.warning("transformers not available, using fallback")
            self._model = None
        except Exception as e:
            self.logger.error(f"Failed to initialize ColBERT model: {e}")
            self._model = None
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> RerankingResult:
        """Rerank results using ColBERT-style scoring."""
        start_time = time.time()
        
        if not results:
            return RerankingResult(
                results=[],
                reranking_time=0.0,
                original_order=[],
                reranked_order=[],
                score_changes=[]
            )
        
        try:
            # Store original order and scores
            original_order = list(range(len(results)))
            original_scores = [r.score for r in results]
            
            if self._model is not None:
                # Use ColBERT-style scoring
                new_scores = await self._colbert_score(query, results)
            else:
                # Fallback to simple scoring
                new_scores = await self._fallback_score(query, results)
            
            # Create reranked results
            reranked_results = []
            for i, (result, new_score) in enumerate(zip(results, new_scores)):
                new_result = SearchResult(
                    document=result.document,
                    score=new_score,
                    rank=0
                )
                reranked_results.append(new_result)
            
            # Sort and update ranks
            reranked_results.sort(key=lambda x: x.score, reverse=True)
            for i, result in enumerate(reranked_results):
                result.rank = i + 1
            
            if top_k is not None:
                reranked_results = reranked_results[:top_k]
            
            # Calculate metrics using document IDs for matching
            reranked_order = []
            for r in reranked_results:
                for i, orig_result in enumerate(results):
                    if r.document.id == orig_result.document.id:
                        reranked_order.append(i)
                        break
            score_changes = [new - orig for new, orig in zip(new_scores, original_scores)]
            
            reranking_time = time.time() - start_time
            
            return RerankingResult(
                results=reranked_results,
                reranking_time=reranking_time,
                original_order=original_order,
                reranked_order=reranked_order,
                score_changes=score_changes
            )
            
        except Exception as e:
            raise RetrievalError(f"ColBERT reranking failed: {e}") from e
    
    async def _colbert_score(self, query: str, results: List[SearchResult]) -> List[float]:
        """Score using ColBERT-style late interaction."""
        # Simplified ColBERT scoring
        # In practice, you'd use proper ColBERT embeddings and MaxSim
        
        import torch
        
        # Tokenize query
        query_tokens = self._tokenizer(
            query,
            max_length=self.max_length,
            truncation=True,
            padding=True,
            return_tensors="pt"
        )
        
        scores = []
        for result in results:
            # Tokenize document
            doc_tokens = self._tokenizer(
                result.document.content,
                max_length=self.max_length,
                truncation=True,
                padding=True,
                return_tensors="pt"
            )
            
            # Get embeddings
            with torch.no_grad():
                query_embeddings = self._model(**query_tokens).last_hidden_state
                doc_embeddings = self._model(**doc_tokens).last_hidden_state
            
            # Simplified late interaction (MaxSim)
            similarity_matrix = torch.matmul(query_embeddings, doc_embeddings.transpose(-1, -2))
            max_similarities = torch.max(similarity_matrix, dim=-1)[0]
            score = torch.mean(max_similarities).item()
            
            scores.append(score)
        
        return scores
    
    async def _fallback_score(self, query: str, results: List[SearchResult]) -> List[float]:
        """Fallback scoring method."""
        query_words = set(query.lower().split())
        scores = []
        
        for result in results:
            content_words = set(result.document.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            score = overlap / max(len(query_words), 1)
            scores.append(score)
        
        return scores


class EnsembleReranker(BaseReranker):
    """Ensemble reranker combining multiple reranking strategies."""
    
    def __init__(self, rerankers: List[Tuple[BaseReranker, float]], **kwargs):
        """
        Initialize ensemble reranker.
        
        Args:
            rerankers: List of (reranker, weight) tuples
        """
        super().__init__(**kwargs)
        self.rerankers = rerankers
        
        # Normalize weights
        total_weight = sum(weight for _, weight in rerankers)
        self.rerankers = [(reranker, weight / total_weight) for reranker, weight in rerankers]
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> RerankingResult:
        """Rerank using ensemble of rerankers."""
        start_time = time.time()
        
        if not results:
            return RerankingResult(
                results=[],
                reranking_time=0.0,
                original_order=[],
                reranked_order=[],
                score_changes=[]
            )
        
        try:
            # Store original order
            original_order = list(range(len(results)))
            original_scores = [r.score for r in results]
            
            # Get scores from all rerankers
            all_reranking_results = []
            for reranker, weight in self.rerankers:
                reranking_result = await reranker.rerank(query, results, top_k=None)
                all_reranking_results.append((reranking_result, weight))
            
            # Combine scores using weighted average
            combined_scores = [0.0] * len(results)
            for reranking_result, weight in all_reranking_results:
                for i, result in enumerate(reranking_result.results):
                    # Find original index
                    original_idx = next(
                        j for j, orig_result in enumerate(results)
                        if orig_result.document.id == result.document.id
                    )
                    combined_scores[original_idx] += weight * result.score
            
            # Create final reranked results
            reranked_results = []
            for i, (result, combined_score) in enumerate(zip(results, combined_scores)):
                new_result = SearchResult(
                    document=result.document,
                    score=combined_score,
                    rank=0
                )
                reranked_results.append(new_result)
            
            # Sort and update ranks
            reranked_results.sort(key=lambda x: x.score, reverse=True)
            for i, result in enumerate(reranked_results):
                result.rank = i + 1
            
            if top_k is not None:
                reranked_results = reranked_results[:top_k]
            
            # Calculate metrics using document IDs for matching
            reranked_order = []
            for r in reranked_results:
                for i, orig_result in enumerate(results):
                    if r.document.id == orig_result.document.id:
                        reranked_order.append(i)
                        break
            score_changes = [new - orig for new, orig in zip(combined_scores, original_scores)]
            
            reranking_time = time.time() - start_time
            
            return RerankingResult(
                results=reranked_results,
                reranking_time=reranking_time,
                original_order=original_order,
                reranked_order=reranked_order,
                score_changes=score_changes
            )
            
        except Exception as e:
            raise RetrievalError(f"Ensemble reranking failed: {e}") from e
