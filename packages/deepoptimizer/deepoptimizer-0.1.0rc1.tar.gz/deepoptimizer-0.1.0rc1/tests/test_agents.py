"""Tests for AI agents."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json

from deepoptimizer.agents import (
    ExperimentDesigner,
    HypothesisGenerator,
    ResultAnalyzer
)
from deepoptimizer.agents.base import Agent, ResearchAgent, AgentConfig
from deepoptimizer.core.models import (
    ResearchContext, OptimizationResult, Trial,
    Experiment
)


class TestExperimentDesigner:
    """Test cases for ExperimentDesigner."""
    
    def test_initialization(self):
        """Test ExperimentDesigner initialization."""
        designer = ExperimentDesigner()
        
        assert designer.config.name == "ExperimentDesigner"
        assert "experiment_design" in designer.config.capabilities
        assert designer.config.temperature == 0.3
    
    def test_design_basic_experiment(self):
        """Test basic experiment design."""
        designer = ExperimentDesigner()
        
        experiment = designer.design(
            objective="Optimize model performance",
            constraints={"max_epochs": 100}
        )
        
        assert isinstance(experiment, Experiment)
        assert experiment.name.startswith("Experiment:")
        assert len(experiment.hyperparameters) > 0
        assert len(experiment.objectives) > 0
    
    def test_design_with_constraints(self):
        """Test experiment design with constraints."""
        designer = ExperimentDesigner()
        
        constraints = {
            "max_epochs": 50,
            "budget": 1000
        }
        
        experiment = designer.design(
            objective="Minimize cost",
            constraints=constraints
        )
        
        assert experiment.constraints is not None
        assert len(experiment.constraints) == 2
        
        # Check constraint names
        constraint_names = [c.name for c in experiment.constraints]
        assert "max_epochs" in constraint_names
        assert "budget" in constraint_names
    
    def test_suggest_parameters(self):
        """Test parameter suggestion."""
        designer = ExperimentDesigner()
        
        # Test for classification problem
        params = designer.suggest_parameters(
            problem_type="classification",
            model_type="neural_network"
        )
        
        param_names = [p.name for p in params]
        assert "random_seed" in param_names
        assert "class_weight" in param_names
        assert "hidden_layers" in param_names
        assert "dropout_rate" in param_names
    
    def test_estimate_experiment_cost(self):
        """Test experiment cost estimation."""
        designer = ExperimentDesigner()
        
        experiment = Experiment(
            name="Test",
            hyperparameters=[],
            objectives=[],
            max_trials=100
        )
        
        resource_costs = {
            "compute_per_minute": 0.1,
            "storage_per_trial": 0.01,
            "api_per_call": 0.02
        }
        
        cost_estimate = designer.estimate_experiment_cost(
            experiment, resource_costs
        )
        
        assert "compute_cost" in cost_estimate
        assert "storage_cost" in cost_estimate
        assert "api_cost" in cost_estimate
        assert "total_cost" in cost_estimate
        assert cost_estimate["total_cost"] > 0


class TestHypothesisGenerator:
    """Test cases for HypothesisGenerator."""
    
    def test_initialization(self):
        """Test HypothesisGenerator initialization."""
        generator = HypothesisGenerator()
        
        assert generator.config.name == "HypothesisGenerator"
        assert "hypothesis_generation" in generator.config.capabilities
        assert generator.config.temperature == 0.8
    
    def test_generate_exploratory_hypotheses(self):
        """Test exploratory hypothesis generation."""
        generator = HypothesisGenerator()
        
        context = ResearchContext(
            domain="machine_learning",
            problem_statement="Improve model accuracy"
        )
        
        hypotheses = generator.generate(
            context=context,
            n_hypotheses=3,
            hypothesis_type="exploratory"
        )
        
        assert len(hypotheses) == 3
        for h in hypotheses:
            assert h.statement
            assert h.rationale
            assert 0 <= h.confidence <= 1
            assert h.testable
    
    def test_generate_null_hypotheses(self):
        """Test null hypothesis generation."""
        generator = HypothesisGenerator()
        
        context = ResearchContext(
            domain="statistics",
            problem_statement="Test parameter significance"
        )
        
        hypotheses = generator.generate(
            context=context,
            n_hypotheses=2,
            hypothesis_type="null"
        )
        
        assert len(hypotheses) == 2
        for h in hypotheses:
            assert "no" in h.statement.lower() or "not" in h.statement.lower()
    
    def test_rank_hypotheses(self):
        """Test hypothesis ranking."""
        generator = HypothesisGenerator()
        
        from deepoptimizer.agents.hypothesis_generator import Hypothesis
        
        hypotheses = [
            Hypothesis("H1", "R1", confidence=0.8, priority=3),
            Hypothesis("H2", "R2", confidence=0.5, priority=1),
            Hypothesis("H3", "R3", confidence=0.9, priority=2)
        ]
        
        ranked = generator.rank_hypotheses(hypotheses)
        
        assert len(ranked) == 3
        assert ranked[0][1] > ranked[1][1]  # Scores are descending
        assert ranked[1][1] > ranked[2][1]
    
    def test_validate_hypothesis(self):
        """Test hypothesis validation."""
        generator = HypothesisGenerator()
        
        from deepoptimizer.agents.hypothesis_generator import Hypothesis
        
        hypothesis = Hypothesis(
            "Test hypothesis",
            "Test rationale"
        )
        
        evidence = [
            "This supports the hypothesis",
            "This contradicts the hypothesis",
            "This is neutral evidence"
        ]
        
        validation = generator.validate_hypothesis(hypothesis, evidence)
        
        assert validation["evidence_count"] == 3
        assert validation["supporting"] == 1
        assert validation["contradicting"] == 1
        assert validation["neutral"] == 1


class TestResultAnalyzer:
    """Test cases for ResultAnalyzer."""
    
    @pytest.fixture
    def sample_results(self):
        """Create sample optimization results."""
        trials = []
        scores = [0.8, 0.85, 0.82, 0.87, 0.9, 0.88, 0.91, 0.89, 0.92, 0.93]
        
        for i, score in enumerate(scores):
            trials.append(Trial(
                idx=i,
                parameters={
                    "param1": i * 0.1,
                    "param2": i * 10,
                    "param3": "value_a" if i % 2 == 0 else "value_b"
                },
                score=score
            ))
        
        return OptimizationResult(
            best_parameters={"param1": 0.9, "param2": 90, "param3": "value_b"},
            best_score=0.93,
            all_trials=trials,
            convergence_history=scores
        )
    
    def test_initialization(self):
        """Test ResultAnalyzer initialization."""
        analyzer = ResultAnalyzer()
        
        assert analyzer.config.name == "ResultAnalyzer"
        assert "statistical_analysis" in analyzer.config.capabilities
        assert analyzer.config.temperature == 0.3
    
    def test_summary_analysis(self, sample_results):
        """Test summary analysis."""
        analyzer = ResultAnalyzer()
        
        analysis = analyzer.analyze(
            sample_results,
            analysis_type="summary"
        )
        
        assert "summary" in analysis
        assert "key_findings" in analysis
        assert "best_configuration" in analysis
        assert analysis["best_score"] == 0.93
    
    def test_statistical_analysis(self, sample_results):
        """Test statistical analysis."""
        analyzer = ResultAnalyzer()
        
        stats = analyzer._calculate_statistics(sample_results)
        
        assert "mean_score" in stats
        assert "std_score" in stats
        assert "min_score" in stats
        assert "max_score" in stats
        assert stats["n_trials"] == 10
        assert stats["min_score"] == 0.8
        assert stats["max_score"] == 0.93
    
    def test_pattern_identification(self, sample_results):
        """Test pattern identification."""
        analyzer = ResultAnalyzer()
        
        patterns = analyzer._identify_patterns(sample_results)
        
        assert len(patterns) > 0
        
        # Check for specific pattern types
        pattern_types = [p["type"] for p in patterns]
        assert "convergence_pattern" in pattern_types
        assert "parameter_importance" in pattern_types
        assert "performance_clusters" in pattern_types
    
    def test_insight_generation(self, sample_results):
        """Test insight generation."""
        analyzer = ResultAnalyzer()
        
        insights = analyzer._generate_insights(sample_results)
        
        assert len(insights) > 0
        assert all(isinstance(i, str) for i in insights)
    
    def test_recommendation_generation(self, sample_results):
        """Test recommendation generation."""
        analyzer = ResultAnalyzer()
        
        recommendations = analyzer._generate_recommendations(sample_results)
        
        assert isinstance(recommendations, list)
        assert all(isinstance(r, str) for r in recommendations)
    
    def test_report_generation(self, sample_results):
        """Test report generation."""
        analyzer = ResultAnalyzer()
        
        report = analyzer._generate_report(sample_results)
        
        assert isinstance(report, str)
        assert "Optimization Results Report" in report
        assert "Executive Summary" in report
        assert "Key Insights" in report
        assert "Recommendations" in report


class TestAgentBase:
    """Test base agent functionality."""
    
    def test_agent_message_passing(self):
        """Test agent message passing."""
        config1 = AgentConfig(name="Agent1", role="Test Agent 1")
        config2 = AgentConfig(name="Agent2", role="Test Agent 2")
        
        class TestAgent(Agent):
            async def process(self, input_data):
                return input_data
            
            def get_prompt(self, input_data):
                return str(input_data)
        
        agent1 = TestAgent(config1)
        agent2 = TestAgent(config2)
        
        # Test sending message
        agent1.send_message("Agent2", {"data": "test"}, "info")
        
        assert len(agent1.message_history) == 1
        assert agent1.message_history[0].recipient == "Agent2"
        assert agent1.message_history[0].content == {"data": "test"}
    
    def test_agent_context_management(self):
        """Test agent context management."""
        config = AgentConfig(name="TestAgent", role="Test")
        
        class TestAgent(Agent):
            async def process(self, input_data):
                return input_data
            
            def get_prompt(self, input_data):
                return str(input_data)
        
        agent = TestAgent(config)
        
        # Test context updates
        agent.update_context("key1", "value1")
        agent.update_context("key2", {"nested": "value"})
        
        assert agent.get_context("key1") == "value1"
        assert agent.get_context("key2") == {"nested": "value"}
        assert agent.get_context("nonexistent", "default") == "default"