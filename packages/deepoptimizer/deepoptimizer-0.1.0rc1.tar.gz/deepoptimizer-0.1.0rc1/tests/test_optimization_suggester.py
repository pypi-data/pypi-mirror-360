"""
Tests for the optimization suggester agent.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from deepoptimizer.agents.optimization_suggester import OptimizationSuggester
from deepoptimizer.core.models import (
    AnalysisResult,
    OptimizationSuggestion,
    HardwareProfile,
    CodeContext,
    ModelArchitecture,
    Technique
)


class TestOptimizationSuggester:
    """Test the OptimizationSuggester agent."""
    
    @pytest.fixture
    def suggester(self):
        """Create an OptimizationSuggester instance."""
        return OptimizationSuggester()
        
    @pytest.fixture
    def sample_analysis(self):
        """Create a sample analysis result."""
        return AnalysisResult(
            framework="pytorch",
            code_context=CodeContext(
                framework="pytorch",
                version="1.9.0",
                file_path="model.py"
            ),
            model_architecture=ModelArchitecture(
                type="cnn",
                layers=[
                    {"type": "Conv2d", "params": {"in_channels": 3, "out_channels": 64}},
                    {"type": "ReLU"},
                    {"type": "Conv2d", "params": {"in_channels": 64, "out_channels": 128}},
                    {"type": "Linear", "params": {"in_features": 128, "out_features": 10}}
                ],
                total_parameters=1000000,
                input_shape=(3, 224, 224),
                output_shape=(10,)
            ),
            components=[
                Mock(name="model", type="model", complexity=75),
                Mock(name="optimizer", type="optimizer", subtype="Adam"),
                Mock(name="dataloader", type="data", batch_size=32)
            ],
            patterns=[],
            training_config={
                "batch_size": 32,
                "learning_rate": 0.001,
                "epochs": 100
            }
        )
        
    @pytest.fixture
    def hardware_profile(self):
        """Create a sample hardware profile."""
        return HardwareProfile(
            device_type="GPU",
            device_name="NVIDIA V100",
            compute_capability=7.0,
            memory_gb=16,
            memory_bandwidth_gb_s=900,
            fp16_support=True,
            int8_support=True,
            tensor_cores=True
        )
        
    @pytest.fixture
    def cpu_hardware_profile(self):
        """Create a CPU hardware profile."""
        return HardwareProfile(
            device_type="CPU",
            device_name="Intel Xeon",
            compute_capability=None,
            memory_gb=64,
            memory_bandwidth_gb_s=100,
            fp16_support=False,
            int8_support=True,
            tensor_cores=False
        )
        
    def test_suggest_for_gpu(self, suggester, sample_analysis, hardware_profile):
        """Test generating suggestions for GPU hardware."""
        suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            optimization_goals=["speed", "memory"]
        )
        
        assert len(suggestions) > 0
        
        # Should suggest Mixed Precision for V100
        technique_names = [s.technique_name for s in suggestions]
        assert "Mixed Precision Training" in technique_names
        
        # Check suggestion properties
        mp_suggestion = next(s for s in suggestions if s.technique_name == "Mixed Precision Training")
        assert mp_suggestion.expected_improvement > 1.5
        assert mp_suggestion.confidence > 0.7
        assert mp_suggestion.priority <= 3  # High priority
        
    def test_suggest_for_cpu(self, suggester, sample_analysis, cpu_hardware_profile):
        """Test generating suggestions for CPU hardware."""
        suggestions = suggester.suggest(
            sample_analysis,
            cpu_hardware_profile,
            optimization_goals=["speed"]
        )
        
        technique_names = [s.technique_name for s in suggestions]
        
        # Should not suggest Mixed Precision for CPU
        assert "Mixed Precision Training" not in technique_names
        
        # Should suggest CPU-friendly optimizations
        assert any("Quantization" in name for name in technique_names)
        assert any("ONNX" in name or "OpenVINO" in name for name in technique_names)
        
    def test_respect_optimization_goals(self, suggester, sample_analysis, hardware_profile):
        """Test that suggestions respect optimization goals."""
        # Speed only
        speed_suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            optimization_goals=["speed"]
        )
        
        # All suggestions should improve speed
        assert all(s.expected_improvement > 1.0 for s in speed_suggestions)
        
        # Memory only
        memory_suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            optimization_goals=["memory"]
        )
        
        # Should include memory reduction techniques
        technique_names = [s.technique_name for s in memory_suggestions]
        assert any("Pruning" in name or "Quantization" in name for name in technique_names)
        
    def test_detect_already_applied(self, suggester, sample_analysis, hardware_profile):
        """Test detecting already applied optimizations."""
        # Add existing patterns
        sample_analysis.patterns = [
            Mock(name="mixed_precision", confidence=0.9),
            Mock(name="data_parallel", confidence=0.8)
        ]
        
        suggestions = suggester.suggest(sample_analysis, hardware_profile)
        
        # Should not suggest already applied techniques
        technique_names = [s.technique_name for s in suggestions]
        assert "Mixed Precision Training" not in technique_names
        assert all("Data Parallel" not in name for name in technique_names)
        
    def test_model_specific_suggestions(self, suggester, hardware_profile):
        """Test model-specific optimization suggestions."""
        # Transformer model
        transformer_analysis = Mock(
            framework="pytorch",
            model_architecture=Mock(
                type="transformer",
                layers=[
                    {"type": "MultiheadAttention", "params": {"embed_dim": 512, "num_heads": 8}},
                    {"type": "LayerNorm"},
                    {"type": "Linear", "params": {"in_features": 512, "out_features": 512}}
                ],
                total_parameters=100000000
            ),
            patterns=[],
            components=[],
            training_config={"batch_size": 16}
        )
        
        suggestions = suggester.suggest(transformer_analysis, hardware_profile)
        technique_names = [s.technique_name for s in suggestions]
        
        # Should suggest transformer-specific optimizations
        assert any("Flash" in name or "Attention" in name for name in technique_names)
        assert any("Gradient Checkpointing" in name for name in technique_names)
        
    def test_implementation_code_generation(self, suggester, sample_analysis, hardware_profile):
        """Test that suggestions include implementation code."""
        suggestions = suggester.suggest(sample_analysis, hardware_profile)
        
        for suggestion in suggestions:
            assert suggestion.implementation_code is not None
            assert len(suggestion.implementation_code) > 0
            
            # Code should be framework-specific
            if sample_analysis.framework == "pytorch":
                assert "torch" in suggestion.implementation_code or "pytorch" in suggestion.implementation_code.lower()
                
    def test_priority_ordering(self, suggester, sample_analysis, hardware_profile):
        """Test that suggestions are properly prioritized."""
        suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            max_suggestions=10
        )
        
        # Check priority ordering
        priorities = [s.priority for s in suggestions]
        assert priorities == sorted(priorities)  # Should be in ascending order
        
        # High impact suggestions should have lower priority numbers
        high_impact = [s for s in suggestions if s.expected_improvement > 1.5]
        low_impact = [s for s in suggestions if s.expected_improvement <= 1.2]
        
        if high_impact and low_impact:
            assert max(s.priority for s in high_impact) < min(s.priority for s in low_impact)
            
    def test_compatibility_filtering(self, suggester, sample_analysis, hardware_profile):
        """Test filtering out incompatible suggestions."""
        # Set specific framework version
        sample_analysis.code_context.version = "1.5.0"  # Older PyTorch
        
        suggestions = suggester.suggest(sample_analysis, hardware_profile)
        
        # Should not suggest features requiring newer versions
        technique_names = [s.technique_name for s in suggestions]
        assert "torch.compile" not in technique_names  # Requires PyTorch 2.0+
        
    def test_constraint_handling(self, suggester, sample_analysis, hardware_profile):
        """Test handling optimization constraints."""
        constraints = {
            "max_memory_overhead": 0.1,  # Max 10% memory increase
            "min_accuracy": 0.99,  # Must maintain 99% accuracy
            "implementation_time": "low"  # Prefer simple implementations
        }
        
        suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            constraints=constraints
        )
        
        # Should filter based on constraints
        for suggestion in suggestions:
            # Check memory constraint
            if hasattr(suggestion, "memory_overhead"):
                assert suggestion.memory_overhead <= 0.1
                
            # Check complexity constraint
            assert suggestion.implementation_complexity in ["low", "medium"]
            
    def test_batch_size_recommendations(self, suggester, sample_analysis, hardware_profile):
        """Test batch size optimization recommendations."""
        # Small batch size scenario
        sample_analysis.training_config["batch_size"] = 4
        
        suggestions = suggester.suggest(sample_analysis, hardware_profile)
        technique_names = [s.technique_name for s in suggestions]
        
        # Should suggest gradient accumulation for small batches
        assert any("Gradient Accumulation" in name for name in technique_names)
        
        # Large memory GPU should suggest larger batches
        if hardware_profile.memory_gb >= 16:
            assert any("batch" in s.description.lower() for s in suggestions)
            
    def test_distributed_training_suggestions(self, suggester, sample_analysis, hardware_profile):
        """Test distributed training suggestions."""
        # Large model scenario
        sample_analysis.model_architecture.total_parameters = 1000000000  # 1B parameters
        
        suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            optimization_goals=["scale"]
        )
        
        technique_names = [s.technique_name for s in suggestions]
        
        # Should suggest distributed training techniques
        assert any("Data Parallel" in name or "DDP" in name for name in technique_names)
        assert any("Model Parallel" in name or "Pipeline" in name for name in technique_names)
        
    def test_inference_optimization(self, suggester, sample_analysis, hardware_profile):
        """Test inference-specific optimizations."""
        suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            optimization_goals=["inference"]
        )
        
        technique_names = [s.technique_name for s in suggestions]
        
        # Should suggest inference optimizations
        assert any("Quantization" in name for name in technique_names)
        assert any("ONNX" in name or "TorchScript" in name for name in technique_names)
        assert any("Pruning" in name for name in technique_names)
        
        # Should not suggest training-only optimizations
        assert not any("Mixed Precision Training" in name for name in technique_names)
        
    def test_custom_metrics(self, suggester, sample_analysis, hardware_profile):
        """Test suggestions with custom optimization metrics."""
        custom_metrics = {
            "latency_target_ms": 10,
            "throughput_target_qps": 1000,
            "cost_per_inference": 0.001
        }
        
        suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            optimization_goals=["latency", "cost"],
            custom_metrics=custom_metrics
        )
        
        # Should prioritize low-latency optimizations
        high_priority = [s for s in suggestions if s.priority <= 3]
        assert any("Quantization" in s.technique_name for s in high_priority)
        
    def test_explanation_quality(self, suggester, sample_analysis, hardware_profile):
        """Test quality of suggestion explanations."""
        suggestions = suggester.suggest(sample_analysis, hardware_profile)
        
        for suggestion in suggestions:
            assert suggestion.description is not None
            assert len(suggestion.description) > 20  # Meaningful description
            
            assert suggestion.rationale is not None
            assert len(suggestion.rationale) > 50  # Detailed rationale
            
            # Should reference specific benefits
            assert any(
                keyword in suggestion.rationale.lower()
                for keyword in ["speed", "memory", "performance", "efficiency"]
            )
            
    def test_citation_inclusion(self, suggester, sample_analysis, hardware_profile):
        """Test that suggestions include relevant citations."""
        suggestions = suggester.suggest(sample_analysis, hardware_profile)
        
        for suggestion in suggestions:
            if suggestion.references:
                assert len(suggestion.references) > 0
                
                # Check reference format
                for ref in suggestion.references:
                    assert "title" in ref or "url" in ref
                    if "arxiv" in ref.get("url", ""):
                        assert ref["url"].startswith("https://arxiv.org")
                        
    def test_incremental_suggestions(self, suggester, sample_analysis, hardware_profile):
        """Test generating incremental suggestions."""
        # First round
        initial_suggestions = suggester.suggest(sample_analysis, hardware_profile)
        
        # Apply one suggestion (mock)
        applied_technique = initial_suggestions[0].technique_name
        sample_analysis.patterns.append(
            Mock(name=applied_technique.lower().replace(" ", "_"))
        )
        
        # Second round
        new_suggestions = suggester.suggest(
            sample_analysis,
            hardware_profile,
            exclude_applied=True
        )
        
        # Should not repeat applied technique
        new_technique_names = [s.technique_name for s in new_suggestions]
        assert applied_technique not in new_technique_names
        
        # Should consider synergies with applied technique
        if applied_technique == "Mixed Precision Training":
            assert any("Gradient Accumulation" in name for name in new_technique_names)