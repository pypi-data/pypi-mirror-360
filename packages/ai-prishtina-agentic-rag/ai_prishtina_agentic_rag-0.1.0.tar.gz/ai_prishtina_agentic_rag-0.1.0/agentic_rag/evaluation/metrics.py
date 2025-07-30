"""Evaluation metrics for the Agentic RAG library."""

import asyncio
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np
from pydantic import BaseModel, Field

from ..utils.exceptions import AgenticRAGError
from ..utils.logging import LoggerMixin


class EvaluationResult(BaseModel):
    """Result of an evaluation metric."""
    
    metric_name: str = Field(description="Name of the metric")
    score: float = Field(description="Metric score")
    max_score: float = Field(description="Maximum possible score")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.now)


class BaseMetric(ABC, LoggerMixin):
    """Abstract base class for evaluation metrics."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate the metric."""
        pass
    
    def _normalize_score(self, score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize score to [0, 1] range."""
        return max(0.0, min(1.0, (score - min_val) / (max_val - min_val)))


class RelevanceMetric(BaseMetric):
    """Metric for evaluating relevance of retrieved documents."""
    
    def __init__(self):
        super().__init__(
            name="relevance",
            description="Measures how relevant the retrieved documents are to the query"
        )
    
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate relevance using keyword overlap and semantic similarity."""
        if not context:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                max_score=1.0,
                details={"error": "No context provided"}
            )
        
        try:
            # Simple keyword-based relevance
            query_words = set(query.lower().split())
            relevance_scores = []
            
            for doc in context:
                doc_words = set(doc.lower().split())
                overlap = len(query_words.intersection(doc_words))
                relevance = overlap / len(query_words) if query_words else 0.0
                relevance_scores.append(relevance)
            
            # Average relevance across all documents
            avg_relevance = np.mean(relevance_scores) if relevance_scores else 0.0
            
            # Try to use sentence transformers for semantic similarity if available
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                
                query_embedding = model.encode([query])
                doc_embeddings = model.encode(context)
                
                # Calculate cosine similarity
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
                semantic_relevance = np.mean(similarities)
                
                # Combine keyword and semantic relevance
                final_score = 0.4 * avg_relevance + 0.6 * semantic_relevance
                
            except ImportError:
                # Fall back to keyword-based relevance only
                final_score = avg_relevance
            
            return EvaluationResult(
                metric_name=self.name,
                score=final_score,
                max_score=1.0,
                details={
                    "keyword_relevance": avg_relevance,
                    "num_documents": len(context),
                    "individual_scores": relevance_scores
                }
            )
            
        except Exception as e:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                max_score=1.0,
                details={"error": str(e)}
            )


class FaithfulnessMetric(BaseMetric):
    """Metric for evaluating faithfulness of response to source documents."""
    
    def __init__(self):
        super().__init__(
            name="faithfulness",
            description="Measures how faithful the response is to the source documents"
        )
    
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate faithfulness by checking if response claims are supported by context."""
        if not context or not response:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                max_score=1.0,
                details={"error": "No context or response provided"}
            )
        
        try:
            # Split response into sentences/claims
            sentences = re.split(r'[.!?]+', response)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return EvaluationResult(
                    metric_name=self.name,
                    score=0.0,
                    max_score=1.0,
                    details={"error": "No sentences found in response"}
                )
            
            # Combine all context documents
            combined_context = " ".join(context).lower()
            
            # Check each sentence for support in context
            supported_sentences = 0
            sentence_scores = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                # Simple keyword overlap check
                sentence_words = set(sentence_lower.split())
                context_words = set(combined_context.split())
                
                overlap = len(sentence_words.intersection(context_words))
                support_score = overlap / len(sentence_words) if sentence_words else 0.0
                
                # Consider sentence supported if overlap > threshold
                if support_score > 0.3:  # 30% word overlap threshold
                    supported_sentences += 1
                
                sentence_scores.append(support_score)
            
            # Calculate faithfulness as percentage of supported sentences
            faithfulness_score = supported_sentences / len(sentences)
            
            return EvaluationResult(
                metric_name=self.name,
                score=faithfulness_score,
                max_score=1.0,
                details={
                    "total_sentences": len(sentences),
                    "supported_sentences": supported_sentences,
                    "sentence_scores": sentence_scores,
                    "average_support": np.mean(sentence_scores)
                }
            )
            
        except Exception as e:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                max_score=1.0,
                details={"error": str(e)}
            )


class AnswerQualityMetric(BaseMetric):
    """Metric for evaluating overall answer quality."""
    
    def __init__(self):
        super().__init__(
            name="answer_quality",
            description="Measures overall quality of the generated answer"
        )
    
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate answer quality using multiple factors."""
        if not response:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                max_score=1.0,
                details={"error": "No response provided"}
            )
        
        try:
            quality_factors = {}
            
            # 1. Length appropriateness (not too short, not too long)
            response_length = len(response.split())
            if response_length < 10:
                length_score = response_length / 10.0
            elif response_length > 200:
                length_score = max(0.5, 1.0 - (response_length - 200) / 400.0)
            else:
                length_score = 1.0
            
            quality_factors["length_score"] = length_score
            
            # 2. Completeness (addresses the query)
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            query_coverage = len(query_words.intersection(response_words)) / len(query_words)
            quality_factors["query_coverage"] = query_coverage
            
            # 3. Coherence (basic check for sentence structure)
            sentences = re.split(r'[.!?]+', response)
            valid_sentences = [s for s in sentences if len(s.strip().split()) >= 3]
            coherence_score = len(valid_sentences) / len(sentences) if sentences else 0.0
            quality_factors["coherence_score"] = coherence_score
            
            # 4. Information density (avoid repetition)
            unique_words = len(set(response.lower().split()))
            total_words = len(response.split())
            diversity_score = unique_words / total_words if total_words > 0 else 0.0
            quality_factors["diversity_score"] = diversity_score
            
            # 5. Ground truth similarity (if available)
            if ground_truth:
                try:
                    from sentence_transformers import SentenceTransformer
                    from sklearn.metrics.pairwise import cosine_similarity
                    
                    model = SentenceTransformer('all-MiniLM-L6-v2')
                    response_emb = model.encode([response])
                    truth_emb = model.encode([ground_truth])
                    
                    similarity = cosine_similarity(response_emb, truth_emb)[0][0]
                    quality_factors["ground_truth_similarity"] = float(similarity)
                    
                except ImportError:
                    # Simple word overlap if sentence transformers not available
                    truth_words = set(ground_truth.lower().split())
                    overlap = len(response_words.intersection(truth_words))
                    similarity = overlap / len(truth_words.union(response_words))
                    quality_factors["ground_truth_similarity"] = similarity
            
            # Calculate weighted overall score
            weights = {
                "length_score": 0.15,
                "query_coverage": 0.25,
                "coherence_score": 0.20,
                "diversity_score": 0.15,
                "ground_truth_similarity": 0.25 if ground_truth else 0.0
            }
            
            # Adjust weights if no ground truth
            if not ground_truth:
                weights["query_coverage"] += 0.125
                weights["coherence_score"] += 0.125
            
            overall_score = sum(
                quality_factors.get(factor, 0.0) * weight
                for factor, weight in weights.items()
            )
            
            return EvaluationResult(
                metric_name=self.name,
                score=overall_score,
                max_score=1.0,
                details=quality_factors
            )
            
        except Exception as e:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                max_score=1.0,
                details={"error": str(e)}
            )


class LatencyMetric(BaseMetric):
    """Metric for evaluating response latency."""
    
    def __init__(self):
        super().__init__(
            name="latency",
            description="Measures response generation latency"
        )
    
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate latency (expects latency_seconds in kwargs)."""
        latency_seconds = kwargs.get("latency_seconds", 0.0)
        
        # Score based on latency thresholds
        if latency_seconds <= 1.0:
            score = 1.0
        elif latency_seconds <= 3.0:
            score = 0.8
        elif latency_seconds <= 5.0:
            score = 0.6
        elif latency_seconds <= 10.0:
            score = 0.4
        else:
            score = 0.2
        
        return EvaluationResult(
            metric_name=self.name,
            score=score,
            max_score=1.0,
            details={
                "latency_seconds": latency_seconds,
                "threshold_category": self._get_latency_category(latency_seconds)
            }
        )
    
    def _get_latency_category(self, latency: float) -> str:
        """Get latency category."""
        if latency <= 1.0:
            return "excellent"
        elif latency <= 3.0:
            return "good"
        elif latency <= 5.0:
            return "acceptable"
        elif latency <= 10.0:
            return "slow"
        else:
            return "very_slow"


class ComprehensiveEvaluator(LoggerMixin):
    """Comprehensive evaluator that runs multiple metrics."""
    
    def __init__(self, metrics: Optional[List[BaseMetric]] = None):
        if metrics is None:
            self.metrics = [
                RelevanceMetric(),
                FaithfulnessMetric(),
                AnswerQualityMetric(),
                LatencyMetric()
            ]
        else:
            self.metrics = metrics
    
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, EvaluationResult]:
        """Run all metrics and return results."""
        results = {}
        
        for metric in self.metrics:
            try:
                result = await metric.evaluate(
                    query=query,
                    response=response,
                    ground_truth=ground_truth,
                    context=context,
                    **kwargs
                )
                results[metric.name] = result
                
            except Exception as e:
                self.logger.error(f"Error evaluating metric {metric.name}: {e}")
                results[metric.name] = EvaluationResult(
                    metric_name=metric.name,
                    score=0.0,
                    max_score=1.0,
                    details={"error": str(e)}
                )
        
        return results
    
    def calculate_overall_score(
        self,
        results: Dict[str, EvaluationResult],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate weighted overall score."""
        if weights is None:
            weights = {
                "relevance": 0.25,
                "faithfulness": 0.25,
                "answer_quality": 0.35,
                "latency": 0.15
            }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric_name, result in results.items():
            weight = weights.get(metric_name, 0.0)
            if weight > 0:
                total_score += result.score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
