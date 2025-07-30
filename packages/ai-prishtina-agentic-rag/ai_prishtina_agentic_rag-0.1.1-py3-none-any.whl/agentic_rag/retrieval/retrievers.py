"""
Advanced retrieval components for the Agentic RAG library.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from .vector_stores import BaseVectorStore, Document, SearchResult
from ..utils.exceptions import RetrievalError
from ..utils.logging import LoggerMixin


@dataclass
class RetrievalQuery:
    """Represents a retrieval query with multiple modalities."""
    text: str
    filters: Optional[Dict[str, Any]] = None
    top_k: int = 5
    similarity_threshold: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class BaseRetriever(ABC, LoggerMixin):
    """Abstract base class for all retrievers."""
    
    def __init__(self, **kwargs):
        """Initialize the retriever."""
        pass
    
    @abstractmethod
    async def retrieve(self, query: Union[str, RetrievalQuery]) -> List[SearchResult]:
        """Retrieve relevant documents for a query."""
        pass


class VectorRetriever(BaseRetriever):
    """Standard vector-based retriever."""
    
    def __init__(self, vector_store: BaseVectorStore, **kwargs):
        """
        Initialize vector retriever.
        
        Args:
            vector_store: Vector store to use for retrieval
        """
        super().__init__(**kwargs)
        self.vector_store = vector_store
    
    async def retrieve(self, query: Union[str, RetrievalQuery]) -> List[SearchResult]:
        """Retrieve documents using vector similarity."""
        if isinstance(query, str):
            query = RetrievalQuery(text=query)
        
        try:
            results = await self.vector_store.search(
                query=query.text,
                top_k=query.top_k,
                filters=query.filters
            )
            
            # Filter by similarity threshold
            if query.similarity_threshold > 0:
                results = [r for r in results if r.score >= query.similarity_threshold]
            
            self.logger.debug(f"Vector retrieval returned {len(results)} results")
            return results
            
        except Exception as e:
            raise RetrievalError(f"Vector retrieval failed: {e}") from e


class HybridRetriever(BaseRetriever):
    """Hybrid retriever combining dense and sparse retrieval."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        sparse_weight: float = 0.3,
        dense_weight: float = 0.7,
        **kwargs
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: Vector store for dense retrieval
            sparse_weight: Weight for sparse (keyword) retrieval
            dense_weight: Weight for dense (vector) retrieval
        """
        super().__init__(**kwargs)
        self.vector_store = vector_store
        self.sparse_weight = sparse_weight
        self.dense_weight = dense_weight
        
        if abs(sparse_weight + dense_weight - 1.0) > 1e-6:
            raise ValueError("Sparse and dense weights must sum to 1.0")
    
    async def retrieve(self, query: Union[str, RetrievalQuery]) -> List[SearchResult]:
        """Retrieve using hybrid dense + sparse approach."""
        if isinstance(query, str):
            query = RetrievalQuery(text=query)
        
        try:
            # Dense retrieval (vector similarity)
            dense_results = await self.vector_store.search(
                query=query.text,
                top_k=query.top_k * 2,  # Get more candidates
                filters=query.filters
            )
            
            # Sparse retrieval (keyword matching)
            sparse_results = await self._sparse_retrieval(query)
            
            # Combine and rerank results
            combined_results = self._combine_results(dense_results, sparse_results, query)
            
            # Apply similarity threshold
            if query.similarity_threshold > 0:
                combined_results = [r for r in combined_results if r.score >= query.similarity_threshold]
            
            # Return top_k results
            return combined_results[:query.top_k]
            
        except Exception as e:
            raise RetrievalError(f"Hybrid retrieval failed: {e}") from e
    
    async def _sparse_retrieval(self, query: RetrievalQuery) -> List[SearchResult]:
        """Perform sparse (keyword-based) retrieval."""
        # Simple keyword matching implementation
        # In production, this would use BM25 or similar
        query_terms = set(query.text.lower().split())
        
        # Get all documents (this is simplified - in practice, use an inverted index)
        all_results = await self.vector_store.search(
            query=query.text,
            top_k=1000,  # Get many documents for keyword filtering
            filters=query.filters
        )
        
        scored_results = []
        for result in all_results:
            content_terms = set(result.document.content.lower().split())
            overlap = len(query_terms.intersection(content_terms))
            
            if overlap > 0:
                # Simple TF-IDF-like scoring
                score = overlap / len(query_terms)
                scored_results.append(SearchResult(
                    document=result.document,
                    score=score,
                    rank=result.rank
                ))
        
        # Sort by score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results
    
    def _combine_results(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult],
        query: RetrievalQuery
    ) -> List[SearchResult]:
        """Combine dense and sparse results with weighted scoring."""
        # Create document ID to result mapping
        dense_map = {r.document.id: r for r in dense_results}
        sparse_map = {r.document.id: r for r in sparse_results}
        
        # Get all unique document IDs
        all_doc_ids = set(dense_map.keys()) | set(sparse_map.keys())
        
        combined_results = []
        for doc_id in all_doc_ids:
            dense_result = dense_map.get(doc_id)
            sparse_result = sparse_map.get(doc_id)
            
            # Calculate combined score
            dense_score = dense_result.score if dense_result else 0.0
            sparse_score = sparse_result.score if sparse_result else 0.0
            
            combined_score = (
                self.dense_weight * dense_score +
                self.sparse_weight * sparse_score
            )
            
            # Use the document from whichever result exists
            document = dense_result.document if dense_result else sparse_result.document
            
            combined_results.append(SearchResult(
                document=document,
                score=combined_score,
                rank=0  # Will be set after sorting
            ))
        
        # Sort by combined score and update ranks
        combined_results.sort(key=lambda x: x.score, reverse=True)
        for i, result in enumerate(combined_results):
            result.rank = i + 1
        
        return combined_results


class GraphRetriever(BaseRetriever):
    """Graph-based retriever for knowledge graphs."""
    
    def __init__(self, vector_store: BaseVectorStore, max_hops: int = 2, **kwargs):
        """
        Initialize graph retriever.
        
        Args:
            vector_store: Vector store containing graph nodes
            max_hops: Maximum number of hops in graph traversal
        """
        super().__init__(**kwargs)
        self.vector_store = vector_store
        self.max_hops = max_hops
    
    async def retrieve(self, query: Union[str, RetrievalQuery]) -> List[SearchResult]:
        """Retrieve using graph traversal."""
        if isinstance(query, str):
            query = RetrievalQuery(text=query)
        
        try:
            # Start with initial vector retrieval
            initial_results = await self.vector_store.search(
                query=query.text,
                top_k=query.top_k,
                filters=query.filters
            )
            
            # Expand through graph relationships
            expanded_results = await self._expand_through_graph(initial_results, query)
            
            # Rerank based on graph structure and relevance
            final_results = self._rerank_graph_results(expanded_results, query)
            
            return final_results[:query.top_k]
            
        except Exception as e:
            raise RetrievalError(f"Graph retrieval failed: {e}") from e
    
    async def _expand_through_graph(
        self,
        initial_results: List[SearchResult],
        query: RetrievalQuery
    ) -> List[SearchResult]:
        """Expand initial results through graph relationships."""
        # This is a simplified implementation
        # In practice, you'd have a proper graph database
        
        expanded_docs = set()
        current_docs = {r.document.id: r for r in initial_results}
        
        for hop in range(self.max_hops):
            next_docs = {}
            
            for doc_id, result in current_docs.items():
                # Look for related documents in metadata
                if "related_docs" in result.document.metadata:
                    related_ids = result.document.metadata["related_docs"]
                    
                    for related_id in related_ids:
                        if related_id not in expanded_docs:
                            # Fetch related document
                            related_doc = await self.vector_store.get_document(related_id)
                            if related_doc:
                                # Calculate propagated score
                                propagated_score = result.score * (0.8 ** (hop + 1))
                                next_docs[related_id] = SearchResult(
                                    document=related_doc,
                                    score=propagated_score,
                                    rank=0
                                )
            
            expanded_docs.update(current_docs.keys())
            current_docs = next_docs
            
            if not current_docs:
                break
        
        # Combine all results
        all_results = list(initial_results)
        all_results.extend(current_docs.values())
        
        return all_results
    
    def _rerank_graph_results(
        self,
        results: List[SearchResult],
        query: RetrievalQuery
    ) -> List[SearchResult]:
        """Rerank results based on graph structure."""
        # Simple reranking based on score
        # In practice, you'd use graph centrality measures
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results


class MultiModalRetriever(BaseRetriever):
    """Multi-modal retriever for text, images, and other modalities."""
    
    def __init__(self, retrievers: Dict[str, BaseRetriever], **kwargs):
        """
        Initialize multi-modal retriever.
        
        Args:
            retrievers: Dictionary mapping modality names to retrievers
        """
        super().__init__(**kwargs)
        self.retrievers = retrievers
    
    async def retrieve(self, query: Union[str, RetrievalQuery]) -> List[SearchResult]:
        """Retrieve across multiple modalities."""
        if isinstance(query, str):
            query = RetrievalQuery(text=query)
        
        try:
            # Retrieve from all modalities in parallel
            tasks = []
            for modality, retriever in self.retrievers.items():
                task = retriever.retrieve(query)
                tasks.append((modality, task))
            
            # Wait for all retrievals to complete
            all_results = []
            for modality, task in tasks:
                try:
                    results = await task
                    # Add modality information to metadata
                    for result in results:
                        result.document.metadata["modality"] = modality
                    all_results.extend(results)
                except Exception as e:
                    self.logger.warning(f"Retrieval failed for modality {modality}: {e}")
            
            # Combine and rerank results
            combined_results = self._combine_multimodal_results(all_results, query)
            
            return combined_results[:query.top_k]
            
        except Exception as e:
            raise RetrievalError(f"Multi-modal retrieval failed: {e}") from e
    
    def _combine_multimodal_results(
        self,
        results: List[SearchResult],
        query: RetrievalQuery
    ) -> List[SearchResult]:
        """Combine results from multiple modalities."""
        # Simple combination - in practice, you'd use learned fusion
        results.sort(key=lambda x: x.score, reverse=True)
        
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results
