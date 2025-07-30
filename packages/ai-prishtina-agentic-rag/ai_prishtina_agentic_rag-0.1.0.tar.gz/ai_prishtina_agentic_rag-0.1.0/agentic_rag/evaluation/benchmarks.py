"""Performance benchmarking for the Agentic RAG library."""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field

from ..core.agent import AgenticRAG, RAGResponse
from ..utils.logging import LoggerMixin
from .metrics import ComprehensiveEvaluator, EvaluationResult


class BenchmarkQuery(BaseModel):
    """A benchmark query with expected results."""
    
    id: str = Field(description="Query ID")
    query: str = Field(description="Query text")
    expected_answer: Optional[str] = Field(default=None, description="Expected answer")
    expected_sources: Optional[List[str]] = Field(default=None, description="Expected source IDs")
    category: str = Field(default="general", description="Query category")
    difficulty: str = Field(default="medium", description="Query difficulty")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BenchmarkResult(BaseModel):
    """Result of a benchmark run."""
    
    query_id: str = Field(description="Query ID")
    query: str = Field(description="Query text")
    response: str = Field(description="Generated response")
    latency_seconds: float = Field(description="Response latency")
    evaluation_scores: Dict[str, float] = Field(description="Evaluation metric scores")
    overall_score: float = Field(description="Overall score")
    sources_used: List[str] = Field(description="Source IDs used")
    reasoning_steps: List[str] = Field(description="Reasoning steps")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BenchmarkSuite(BaseModel):
    """A collection of benchmark queries."""
    
    name: str = Field(description="Benchmark suite name")
    description: str = Field(description="Benchmark suite description")
    version: str = Field(default="1.0", description="Benchmark version")
    queries: List[BenchmarkQuery] = Field(description="Benchmark queries")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Suite metadata")


class PerformanceBenchmark(LoggerMixin):
    """Performance benchmarking system for RAG."""
    
    def __init__(
        self,
        rag_system: AgenticRAG,
        evaluator: Optional[ComprehensiveEvaluator] = None
    ):
        self.rag_system = rag_system
        self.evaluator = evaluator or ComprehensiveEvaluator()
        self.results: List[BenchmarkResult] = []
    
    async def run_benchmark(
        self,
        benchmark_suite: BenchmarkSuite,
        warmup_queries: int = 3,
        repeat_count: int = 1
    ) -> Dict[str, Any]:
        """Run a complete benchmark suite."""
        self.logger.info(f"Starting benchmark: {benchmark_suite.name}")
        
        # Warmup phase
        if warmup_queries > 0:
            self.logger.info(f"Running {warmup_queries} warmup queries...")
            warmup_suite = BenchmarkSuite(
                name="warmup",
                description="Warmup queries",
                queries=benchmark_suite.queries[:warmup_queries]
            )
            await self._run_queries(warmup_suite.queries, is_warmup=True)
        
        # Main benchmark
        all_results = []
        for run in range(repeat_count):
            self.logger.info(f"Running benchmark iteration {run + 1}/{repeat_count}")
            run_results = await self._run_queries(benchmark_suite.queries)
            all_results.extend(run_results)
        
        # Calculate statistics
        stats = self._calculate_statistics(all_results)
        
        # Generate report
        report = {
            "benchmark_name": benchmark_suite.name,
            "benchmark_version": benchmark_suite.version,
            "total_queries": len(benchmark_suite.queries),
            "repeat_count": repeat_count,
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "results": [result.dict() for result in all_results]
        }
        
        self.logger.info(f"Benchmark completed. Overall score: {stats['overall_score']:.3f}")
        return report
    
    async def _run_queries(
        self,
        queries: List[BenchmarkQuery],
        is_warmup: bool = False
    ) -> List[BenchmarkResult]:
        """Run a list of queries and collect results."""
        results = []
        
        for i, query in enumerate(queries):
            if not is_warmup:
                self.logger.info(f"Processing query {i + 1}/{len(queries)}: {query.id}")
            
            try:
                # Measure latency
                start_time = time.time()
                response = await self.rag_system.query(query.query)
                end_time = time.time()
                latency = end_time - start_time
                
                if not is_warmup:
                    # Evaluate response
                    evaluation_results = await self.evaluator.evaluate(
                        query=query.query,
                        response=response.answer,
                        ground_truth=query.expected_answer,
                        context=[source.get('content', '') for source in response.sources],
                        latency_seconds=latency
                    )
                    
                    # Calculate overall score
                    overall_score = self.evaluator.calculate_overall_score(evaluation_results)
                    
                    # Create benchmark result
                    result = BenchmarkResult(
                        query_id=query.id,
                        query=query.query,
                        response=response.answer,
                        latency_seconds=latency,
                        evaluation_scores={
                            name: result.score for name, result in evaluation_results.items()
                        },
                        overall_score=overall_score,
                        sources_used=[source.get('id', '') for source in response.sources],
                        reasoning_steps=response.reasoning_steps,
                        metadata={
                            "category": query.category,
                            "difficulty": query.difficulty,
                            "confidence": response.confidence
                        }
                    )
                    
                    results.append(result)
                
            except Exception as e:
                if not is_warmup:
                    self.logger.error(f"Error processing query {query.id}: {e}")
                    # Create error result
                    error_result = BenchmarkResult(
                        query_id=query.id,
                        query=query.query,
                        response=f"Error: {str(e)}",
                        latency_seconds=0.0,
                        evaluation_scores={},
                        overall_score=0.0,
                        sources_used=[],
                        reasoning_steps=[],
                        metadata={"error": str(e)}
                    )
                    results.append(error_result)
        
        return results
    
    def _calculate_statistics(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate benchmark statistics."""
        if not results:
            return {}
        
        # Overall metrics
        overall_scores = [r.overall_score for r in results]
        latencies = [r.latency_seconds for r in results]
        
        # Per-metric statistics
        metric_stats = {}
        all_metrics = set()
        for result in results:
            all_metrics.update(result.evaluation_scores.keys())
        
        for metric in all_metrics:
            scores = [r.evaluation_scores.get(metric, 0.0) for r in results]
            metric_stats[metric] = {
                "mean": np.mean(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores),
                "median": np.median(scores)
            }
        
        # Category-wise statistics
        category_stats = {}
        categories = set(r.metadata.get('category', 'general') for r in results)
        for category in categories:
            category_results = [r for r in results if r.metadata.get('category') == category]
            if category_results:
                category_scores = [r.overall_score for r in category_results]
                category_latencies = [r.latency_seconds for r in category_results]
                category_stats[category] = {
                    "count": len(category_results),
                    "mean_score": np.mean(category_scores),
                    "mean_latency": np.mean(category_latencies)
                }
        
        # Difficulty-wise statistics
        difficulty_stats = {}
        difficulties = set(r.metadata.get('difficulty', 'medium') for r in results)
        for difficulty in difficulties:
            difficulty_results = [r for r in results if r.metadata.get('difficulty') == difficulty]
            if difficulty_results:
                difficulty_scores = [r.overall_score for r in difficulty_results]
                difficulty_stats[difficulty] = {
                    "count": len(difficulty_results),
                    "mean_score": np.mean(difficulty_scores)
                }
        
        return {
            "overall_score": np.mean(overall_scores),
            "overall_score_std": np.std(overall_scores),
            "mean_latency": np.mean(latencies),
            "latency_std": np.std(latencies),
            "p95_latency": np.percentile(latencies, 95),
            "p99_latency": np.percentile(latencies, 99),
            "total_queries": len(results),
            "successful_queries": len([r for r in results if "error" not in r.metadata]),
            "error_rate": len([r for r in results if "error" in r.metadata]) / len(results),
            "metric_statistics": metric_stats,
            "category_statistics": category_stats,
            "difficulty_statistics": difficulty_stats
        }
    
    def save_results(self, filepath: Path, results: Dict[str, Any]) -> None:
        """Save benchmark results to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        self.logger.info(f"Benchmark results saved to {filepath}")
    
    def load_benchmark_suite(self, filepath: Path) -> BenchmarkSuite:
        """Load benchmark suite from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return BenchmarkSuite(**data)


class RAGBenchmark:
    """Main benchmark class with predefined benchmark suites."""
    
    @staticmethod
    def create_basic_qa_benchmark() -> BenchmarkSuite:
        """Create a basic Q&A benchmark suite."""
        queries = [
            BenchmarkQuery(
                id="basic_001",
                query="What is artificial intelligence?",
                category="definition",
                difficulty="easy"
            ),
            BenchmarkQuery(
                id="basic_002",
                query="How does machine learning differ from traditional programming?",
                category="comparison",
                difficulty="medium"
            ),
            BenchmarkQuery(
                id="basic_003",
                query="Explain the transformer architecture and its key innovations in natural language processing.",
                category="technical",
                difficulty="hard"
            ),
            BenchmarkQuery(
                id="basic_004",
                query="What are the ethical considerations in AI development?",
                category="ethics",
                difficulty="medium"
            ),
            BenchmarkQuery(
                id="basic_005",
                query="Calculate the accuracy of a model with 85 correct predictions out of 100 total predictions.",
                category="calculation",
                difficulty="easy"
            )
        ]
        
        return BenchmarkSuite(
            name="Basic Q&A Benchmark",
            description="Basic question-answering benchmark covering various AI topics",
            queries=queries
        )
    
    @staticmethod
    def create_reasoning_benchmark() -> BenchmarkSuite:
        """Create a reasoning benchmark suite."""
        queries = [
            BenchmarkQuery(
                id="reasoning_001",
                query="If a neural network has 3 layers with 100, 50, and 10 neurons respectively, and uses ReLU activation, what would be the total number of parameters if it's fully connected?",
                category="reasoning",
                difficulty="hard"
            ),
            BenchmarkQuery(
                id="reasoning_002",
                query="Compare the advantages and disadvantages of supervised vs unsupervised learning, and provide examples of when to use each.",
                category="analysis",
                difficulty="medium"
            ),
            BenchmarkQuery(
                id="reasoning_003",
                query="A company wants to implement a recommendation system. What factors should they consider, and what approach would you recommend?",
                category="application",
                difficulty="hard"
            )
        ]
        
        return BenchmarkSuite(
            name="Reasoning Benchmark",
            description="Benchmark focusing on reasoning and analytical capabilities",
            queries=queries
        )
    
    @staticmethod
    def create_multi_step_benchmark() -> BenchmarkSuite:
        """Create a multi-step reasoning benchmark."""
        queries = [
            BenchmarkQuery(
                id="multistep_001",
                query="I need to build a chatbot for customer service. First, explain what technologies I should consider, then calculate the estimated cost if I expect 1000 queries per day and each query costs $0.01 to process.",
                category="multi_step",
                difficulty="hard"
            ),
            BenchmarkQuery(
                id="multistep_002",
                query="Research the latest developments in large language models, then explain how they could be applied to improve search engines.",
                category="research_application",
                difficulty="hard"
            )
        ]
        
        return BenchmarkSuite(
            name="Multi-Step Benchmark",
            description="Benchmark requiring multi-step reasoning and tool usage",
            queries=queries
        )
