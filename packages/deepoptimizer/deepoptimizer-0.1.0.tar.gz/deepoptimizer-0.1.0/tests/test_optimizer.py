"""Tests for the Optimizer class."""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from deepoptimizer.core.optimizer import Optimizer, OptimizationAlgorithm
from deepoptimizer.core.models import (
    Experiment, HyperParameter, Objective,
    HyperParameterType, ObjectiveType
)


@pytest.fixture
def sample_experiment():
    """Create a sample experiment for testing."""
    return Experiment(
        name="Test Experiment",
        description="A test experiment",
        hyperparameters=[
            HyperParameter(
                name="learning_rate",
                type=HyperParameterType.FLOAT,
                min_value=0.001,
                max_value=0.1
            ),
            HyperParameter(
                name="batch_size",
                type=HyperParameterType.INT,
                min_value=16,
                max_value=128
            ),
            HyperParameter(
                name="optimizer",
                type=HyperParameterType.CATEGORICAL,
                choices=["adam", "sgd", "rmsprop"]
            )
        ],
        objectives=[
            Objective(
                name="accuracy",
                type=ObjectiveType.MAXIMIZE
            )
        ]
    )


@pytest.fixture
def optimizer():
    """Create an optimizer instance for testing."""
    return Optimizer(
        api_key="test_key",
        model="gpt-4",
        algorithm=OptimizationAlgorithm.RANDOM,
        verbose=False
    )


class TestOptimizer:
    """Test cases for Optimizer class."""
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        opt = Optimizer(
            api_key="test_key",
            model="gpt-4",
            algorithm="bayesian"
        )
        
        assert opt.config.api_key == "test_key"
        assert opt.config.model == "gpt-4"
        assert opt.config.algorithm == OptimizationAlgorithm.BAYESIAN
    
    def test_optimize_with_random_search(self, optimizer, sample_experiment):
        """Test optimization with random search."""
        results = optimizer.optimize(
            sample_experiment,
            n_trials=10,
            optimization_algorithm="random"
        )
        
        assert len(results.all_trials) == 10
        assert results.best_score is not None
        assert results.best_parameters is not None
        assert len(results.convergence_history) == 10
    
    def test_optimize_with_callbacks(self, optimizer, sample_experiment):
        """Test optimization with callbacks."""
        callback_called = []
        
        def test_callback(trial, trials):
            callback_called.append(trial.idx)
        
        results = optimizer.optimize(
            sample_experiment,
            n_trials=5,
            callbacks=[test_callback]
        )
        
        assert len(callback_called) == 5
        assert callback_called == [0, 1, 2, 3, 4]
    
    def test_invalid_algorithm(self, optimizer, sample_experiment):
        """Test with invalid optimization algorithm."""
        with pytest.raises(ValueError, match="Unknown optimization algorithm"):
            optimizer.optimize(
                sample_experiment,
                n_trials=5,
                optimization_algorithm="invalid_algorithm"
            )
    
    def test_parameter_generation(self, optimizer, sample_experiment):
        """Test parameter generation for different types."""
        params = optimizer._random_search(sample_experiment, [])
        
        assert "learning_rate" in params
        assert "batch_size" in params
        assert "optimizer" in params
        
        assert isinstance(params["learning_rate"], float)
        assert 0.001 <= params["learning_rate"] <= 0.1
        
        assert isinstance(params["batch_size"], int)
        assert 16 <= params["batch_size"] <= 128
        
        assert params["optimizer"] in ["adam", "sgd", "rmsprop"]
    
    def test_convergence_tracking(self, optimizer, sample_experiment):
        """Test that convergence is properly tracked."""
        results = optimizer.optimize(sample_experiment, n_trials=20)
        
        # Check convergence history
        assert len(results.convergence_history) == 20
        
        # Check that best score is in the history
        assert min(results.convergence_history) == results.best_score
    
    def test_empty_experiment(self, optimizer):
        """Test optimization with empty experiment."""
        empty_experiment = Experiment(
            name="Empty",
            hyperparameters=[],
            objectives=[]
        )
        
        results = optimizer.optimize(empty_experiment, n_trials=5)
        
        assert len(results.all_trials) == 5
        assert results.best_parameters == {}


class TestOptimizationAlgorithms:
    """Test different optimization algorithms."""
    
    @pytest.mark.parametrize("algorithm", [
        "random", "grid", "bayesian", "evolutionary", "gradient_based", "hybrid"
    ])
    def test_algorithm_execution(self, sample_experiment, algorithm):
        """Test that all algorithms can execute."""
        opt = Optimizer(
            api_key="test_key",
            model="gpt-4",
            algorithm=algorithm
        )
        
        results = opt.optimize(sample_experiment, n_trials=5)
        
        assert len(results.all_trials) == 5
        assert results.metadata["algorithm"] == algorithm