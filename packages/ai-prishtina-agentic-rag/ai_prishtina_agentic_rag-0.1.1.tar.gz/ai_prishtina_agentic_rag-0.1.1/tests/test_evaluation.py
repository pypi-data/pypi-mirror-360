"""Tests for evaluation components."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock

from agentic_rag.evaluation.metrics import (
    RelevanceMetric,
    FaithfulnessMetric,
    AnswerQualityMetric,
    LatencyMetric,
    ComprehensiveEvaluator,
    EvaluationResult
)
from agentic_rag.evaluation.benchmarks import (
    BenchmarkQuery,
    BenchmarkResult,
    BenchmarkSuite,
    PerformanceBenchmark,
    RAGBenchmark
)


class TestEvaluationResult:
    """Test EvaluationResult model."""
    
    def test_evaluation_result_creation(self):
        """Test creating an evaluation result."""
        result = EvaluationResult(
            metric_name="test_metric",
            score=0.85,
            max_score=1.0,
            details={"info": "test"}
        )
        
        assert result.metric_name == "test_metric"
        assert result.score == 0.85
        assert result.max_score == 1.0
        assert result.details["info"] == "test"


@pytest.mark.asyncio
class TestRelevanceMetric:
    """Test RelevanceMetric implementation."""
    
    def test_relevance_metric_initialization(self):
        """Test relevance metric initialization."""
        metric = RelevanceMetric()
        
        assert metric.name == "relevance"
        assert "relevant" in metric.description.lower()
    
    async def test_relevance_evaluation_no_context(self):
        """Test relevance evaluation without context."""
        metric = RelevanceMetric()
        
        result = await metric.evaluate(
            query="What is AI?",
            response="AI is artificial intelligence",
            context=None
        )
        
        assert result.metric_name == "relevance"
        assert result.score == 0.0
        assert "error" in result.details
    
    async def test_relevance_evaluation_with_context(self):
        """Test relevance evaluation with context."""
        metric = RelevanceMetric()
        
        context = [
            "Artificial intelligence (AI) is a branch of computer science",
            "Machine learning is a subset of AI that enables computers to learn"
        ]
        
        result = await metric.evaluate(
            query="What is artificial intelligence?",
            response="AI is a branch of computer science",
            context=context
        )
        
        assert result.metric_name == "relevance"
        assert result.score > 0.0
        assert result.max_score == 1.0
        assert "keyword_relevance" in result.details
    
    @patch('sentence_transformers.SentenceTransformer')
    @patch('sklearn.metrics.pairwise.cosine_similarity')
    async def test_relevance_with_semantic_similarity(self, mock_cosine, mock_transformer):
        """Test relevance evaluation with semantic similarity."""
        # Mock sentence transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
        mock_transformer.return_value = mock_model
        
        # Mock cosine similarity
        mock_cosine.return_value = [[0.8, 0.6]]
        
        metric = RelevanceMetric()
        
        context = ["AI is artificial intelligence"]
        
        result = await metric.evaluate(
            query="What is AI?",
            response="AI is artificial intelligence",
            context=context
        )
        
        assert result.score > 0.0
        assert result.details["keyword_relevance"] >= 0.0


@pytest.mark.asyncio
class TestFaithfulnessMetric:
    """Test FaithfulnessMetric implementation."""
    
    def test_faithfulness_metric_initialization(self):
        """Test faithfulness metric initialization."""
        metric = FaithfulnessMetric()
        
        assert metric.name == "faithfulness"
        assert "faithful" in metric.description.lower()
    
    async def test_faithfulness_evaluation_no_context(self):
        """Test faithfulness evaluation without context."""
        metric = FaithfulnessMetric()
        
        result = await metric.evaluate(
            query="What is AI?",
            response="AI is artificial intelligence",
            context=None
        )
        
        assert result.metric_name == "faithfulness"
        assert result.score == 0.0
        assert "error" in result.details
    
    async def test_faithfulness_evaluation_with_context(self):
        """Test faithfulness evaluation with context."""
        metric = FaithfulnessMetric()
        
        context = [
            "Artificial intelligence is a branch of computer science that aims to create intelligent machines."
        ]
        
        response = "AI is a branch of computer science. It aims to create intelligent machines."
        
        result = await metric.evaluate(
            query="What is AI?",
            response=response,
            context=context
        )
        
        assert result.metric_name == "faithfulness"
        assert result.score > 0.0
        assert result.max_score == 1.0
        assert "total_sentences" in result.details
        assert "supported_sentences" in result.details
    
    async def test_faithfulness_unsupported_claims(self):
        """Test faithfulness with unsupported claims."""
        metric = FaithfulnessMetric()
        
        context = ["AI is artificial intelligence."]
        response = "AI is artificial intelligence. AI was invented yesterday by aliens."
        
        result = await metric.evaluate(
            query="What is AI?",
            response=response,
            context=context
        )
        
        # Should have lower faithfulness due to unsupported claim
        assert result.score < 1.0
        assert result.details["total_sentences"] == 2
        assert result.details["supported_sentences"] < 2


@pytest.mark.asyncio
class TestAnswerQualityMetric:
    """Test AnswerQualityMetric implementation."""
    
    def test_answer_quality_metric_initialization(self):
        """Test answer quality metric initialization."""
        metric = AnswerQualityMetric()
        
        assert metric.name == "answer_quality"
        assert "quality" in metric.description.lower()
    
    async def test_answer_quality_no_response(self):
        """Test answer quality evaluation without response."""
        metric = AnswerQualityMetric()
        
        result = await metric.evaluate(
            query="What is AI?",
            response="",
            context=None
        )
        
        assert result.metric_name == "answer_quality"
        assert result.score == 0.0
        assert "error" in result.details
    
    async def test_answer_quality_evaluation(self):
        """Test answer quality evaluation."""
        metric = AnswerQualityMetric()
        
        query = "What is artificial intelligence?"
        response = "Artificial intelligence is a branch of computer science that aims to create intelligent machines capable of performing tasks that typically require human intelligence."
        
        result = await metric.evaluate(
            query=query,
            response=response,
            context=None
        )
        
        assert result.metric_name == "answer_quality"
        assert result.score > 0.0
        assert result.max_score == 1.0
        assert "length_score" in result.details
        assert "query_coverage" in result.details
        assert "coherence_score" in result.details
        assert "diversity_score" in result.details
    
    async def test_answer_quality_with_ground_truth(self):
        """Test answer quality evaluation with ground truth."""
        metric = AnswerQualityMetric()
        
        query = "What is AI?"
        response = "AI is artificial intelligence, a field of computer science."
        ground_truth = "Artificial intelligence is a branch of computer science focused on creating intelligent machines."
        
        result = await metric.evaluate(
            query=query,
            response=response,
            ground_truth=ground_truth,
            context=None
        )
        
        assert result.score > 0.0
        assert "ground_truth_similarity" in result.details
    
    async def test_answer_quality_length_scoring(self):
        """Test answer quality length scoring."""
        metric = AnswerQualityMetric()
        
        # Test very short response
        short_result = await metric.evaluate(
            query="What is AI?",
            response="AI.",
            context=None
        )
        
        # Test very long response
        long_response = " ".join(["This is a very long response."] * 100)
        long_result = await metric.evaluate(
            query="What is AI?",
            response=long_response,
            context=None
        )
        
        # Test appropriate length response
        good_response = "AI is artificial intelligence, a field of computer science that creates intelligent machines."
        good_result = await metric.evaluate(
            query="What is AI?",
            response=good_response,
            context=None
        )
        
        # Good length should score higher than too short or too long
        assert good_result.details["length_score"] >= short_result.details["length_score"]
        assert good_result.details["length_score"] >= long_result.details["length_score"]


@pytest.mark.asyncio
class TestLatencyMetric:
    """Test LatencyMetric implementation."""
    
    def test_latency_metric_initialization(self):
        """Test latency metric initialization."""
        metric = LatencyMetric()
        
        assert metric.name == "latency"
        assert "latency" in metric.description.lower()
    
    async def test_latency_evaluation_excellent(self):
        """Test latency evaluation for excellent performance."""
        metric = LatencyMetric()
        
        result = await metric.evaluate(
            query="What is AI?",
            response="AI is artificial intelligence",
            latency_seconds=0.5
        )
        
        assert result.metric_name == "latency"
        assert result.score == 1.0
        assert result.details["latency_seconds"] == 0.5
        assert result.details["threshold_category"] == "excellent"
    
    async def test_latency_evaluation_slow(self):
        """Test latency evaluation for slow performance."""
        metric = LatencyMetric()
        
        result = await metric.evaluate(
            query="What is AI?",
            response="AI is artificial intelligence",
            latency_seconds=15.0
        )
        
        assert result.metric_name == "latency"
        assert result.score == 0.2
        assert result.details["threshold_category"] == "very_slow"
    
    async def test_latency_evaluation_categories(self):
        """Test latency evaluation categories."""
        metric = LatencyMetric()
        
        test_cases = [
            (0.5, "excellent", 1.0),
            (2.0, "good", 0.8),
            (4.0, "acceptable", 0.6),
            (8.0, "slow", 0.4),
            (15.0, "very_slow", 0.2)
        ]
        
        for latency, expected_category, expected_score in test_cases:
            result = await metric.evaluate(
                query="test",
                response="test",
                latency_seconds=latency
            )
            
            assert result.details["threshold_category"] == expected_category
            assert result.score == expected_score


@pytest.mark.asyncio
class TestComprehensiveEvaluator:
    """Test ComprehensiveEvaluator implementation."""
    
    def test_comprehensive_evaluator_initialization(self):
        """Test comprehensive evaluator initialization."""
        evaluator = ComprehensiveEvaluator()
        
        assert len(evaluator.metrics) == 4  # Default metrics
        metric_names = [metric.name for metric in evaluator.metrics]
        assert "relevance" in metric_names
        assert "faithfulness" in metric_names
        assert "answer_quality" in metric_names
        assert "latency" in metric_names
    
    def test_comprehensive_evaluator_custom_metrics(self):
        """Test comprehensive evaluator with custom metrics."""
        custom_metrics = [RelevanceMetric(), AnswerQualityMetric()]
        evaluator = ComprehensiveEvaluator(metrics=custom_metrics)
        
        assert len(evaluator.metrics) == 2
        metric_names = [metric.name for metric in evaluator.metrics]
        assert "relevance" in metric_names
        assert "answer_quality" in metric_names
    
    async def test_comprehensive_evaluation(self):
        """Test comprehensive evaluation."""
        evaluator = ComprehensiveEvaluator()
        
        results = await evaluator.evaluate(
            query="What is artificial intelligence?",
            response="AI is a branch of computer science that creates intelligent machines.",
            context=["Artificial intelligence is a field of computer science"],
            latency_seconds=1.5
        )
        
        assert len(results) == 4
        assert "relevance" in results
        assert "faithfulness" in results
        assert "answer_quality" in results
        assert "latency" in results
        
        for metric_name, result in results.items():
            assert isinstance(result, EvaluationResult)
            assert result.metric_name == metric_name
            assert 0.0 <= result.score <= 1.0
    
    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        evaluator = ComprehensiveEvaluator()
        
        # Mock results
        results = {
            "relevance": EvaluationResult(metric_name="relevance", score=0.8, max_score=1.0),
            "faithfulness": EvaluationResult(metric_name="faithfulness", score=0.9, max_score=1.0),
            "answer_quality": EvaluationResult(metric_name="answer_quality", score=0.7, max_score=1.0),
            "latency": EvaluationResult(metric_name="latency", score=0.6, max_score=1.0)
        }
        
        overall_score = evaluator.calculate_overall_score(results)
        
        # Should be weighted average
        expected = 0.25 * 0.8 + 0.25 * 0.9 + 0.35 * 0.7 + 0.15 * 0.6
        assert abs(overall_score - expected) < 0.001
    
    def test_calculate_overall_score_custom_weights(self):
        """Test overall score calculation with custom weights."""
        evaluator = ComprehensiveEvaluator()
        
        results = {
            "relevance": EvaluationResult(metric_name="relevance", score=0.8, max_score=1.0),
            "answer_quality": EvaluationResult(metric_name="answer_quality", score=0.6, max_score=1.0)
        }
        
        custom_weights = {"relevance": 0.7, "answer_quality": 0.3}
        overall_score = evaluator.calculate_overall_score(results, weights=custom_weights)
        
        expected = 0.7 * 0.8 + 0.3 * 0.6
        assert abs(overall_score - expected) < 0.001


class TestBenchmarkModels:
    """Test benchmark model classes."""
    
    def test_benchmark_query_creation(self):
        """Test creating a benchmark query."""
        query = BenchmarkQuery(
            id="test_001",
            query="What is AI?",
            expected_answer="AI is artificial intelligence",
            category="definition",
            difficulty="easy"
        )
        
        assert query.id == "test_001"
        assert query.query == "What is AI?"
        assert query.expected_answer == "AI is artificial intelligence"
        assert query.category == "definition"
        assert query.difficulty == "easy"
    
    def test_benchmark_result_creation(self):
        """Test creating a benchmark result."""
        result = BenchmarkResult(
            query_id="test_001",
            query="What is AI?",
            response="AI is artificial intelligence",
            latency_seconds=1.2,
            evaluation_scores={"relevance": 0.8, "quality": 0.7},
            overall_score=0.75,
            sources_used=["doc1", "doc2"],
            reasoning_steps=["Retrieved documents", "Generated response"]
        )
        
        assert result.query_id == "test_001"
        assert result.latency_seconds == 1.2
        assert result.overall_score == 0.75
        assert len(result.sources_used) == 2
        assert len(result.reasoning_steps) == 2
    
    def test_benchmark_suite_creation(self):
        """Test creating a benchmark suite."""
        queries = [
            BenchmarkQuery(id="q1", query="What is AI?"),
            BenchmarkQuery(id="q2", query="What is ML?")
        ]
        
        suite = BenchmarkSuite(
            name="Test Suite",
            description="A test benchmark suite",
            queries=queries
        )
        
        assert suite.name == "Test Suite"
        assert len(suite.queries) == 2
        assert suite.version == "1.0"


class TestRAGBenchmark:
    """Test RAGBenchmark predefined suites."""
    
    def test_create_basic_qa_benchmark(self):
        """Test creating basic Q&A benchmark."""
        suite = RAGBenchmark.create_basic_qa_benchmark()
        
        assert suite.name == "Basic Q&A Benchmark"
        assert len(suite.queries) == 5
        
        # Check query categories
        categories = [q.category for q in suite.queries]
        assert "definition" in categories
        assert "comparison" in categories
        assert "technical" in categories
        assert "calculation" in categories
    
    def test_create_reasoning_benchmark(self):
        """Test creating reasoning benchmark."""
        suite = RAGBenchmark.create_reasoning_benchmark()
        
        assert suite.name == "Reasoning Benchmark"
        assert len(suite.queries) == 3
        
        # Check that all queries are reasoning-focused
        for query in suite.queries:
            assert query.category in ["reasoning", "analysis", "application"]
    
    def test_create_multi_step_benchmark(self):
        """Test creating multi-step benchmark."""
        suite = RAGBenchmark.create_multi_step_benchmark()
        
        assert suite.name == "Multi-Step Benchmark"
        assert len(suite.queries) == 2
        
        # Check that queries require multi-step reasoning
        for query in suite.queries:
            assert query.category in ["multi_step", "research_application"]
            assert query.difficulty == "hard"
