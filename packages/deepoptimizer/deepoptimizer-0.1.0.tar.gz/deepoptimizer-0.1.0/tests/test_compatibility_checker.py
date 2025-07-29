"""
Tests for the compatibility checker agent.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from deepoptimizer.agents.compatibility_checker import CompatibilityChecker
from deepoptimizer.core.models import (
    Technique,
    AnalysisResult,
    HardwareProfile,
    Compatibility,
    CodeContext,
    ModelArchitecture
)


class TestCompatibilityChecker:
    """Test the CompatibilityChecker agent."""
    
    @pytest.fixture
    def checker(self):
        """Create a CompatibilityChecker instance."""
        return CompatibilityChecker()
        
    @pytest.fixture
    def mixed_precision_technique(self):
        """Create Mixed Precision technique."""
        return Technique(
            name="Mixed Precision Training",
            category="training",
            frameworks=["pytorch", "tensorflow"],
            hardware_requirements=["gpu"],
            min_compute_capability=7.0,
            requires_tensor_cores=True,
            min_framework_version={"pytorch": "1.6.0", "tensorflow": "2.4.0"}
        )
        
    @pytest.fixture
    def quantization_technique(self):
        """Create Quantization technique."""
        return Technique(
            name="INT8 Quantization",
            category="compression",
            frameworks=["pytorch", "tensorflow", "onnx"],
            hardware_requirements=["cpu", "gpu"],
            min_compute_capability=6.1,
            requires_int8_support=True
        )
        
    @pytest.fixture
    def pruning_technique(self):
        """Create Pruning technique."""
        return Technique(
            name="Magnitude Pruning",
            category="compression",
            frameworks=["pytorch", "tensorflow"],
            hardware_requirements=["cpu", "gpu"],
            accuracy_impact=-0.02,  # 2% accuracy loss
            conflicts_with=["INT8 Quantization"]  # Can conflict with quantization
        )
        
    @pytest.fixture
    def sample_analysis(self):
        """Create sample analysis result."""
        return AnalysisResult(
            framework="pytorch",
            code_context=CodeContext(
                framework="pytorch",
                version="1.9.0",
                imports=["torch", "torch.nn", "torch.optim"]
            ),
            model_architecture=ModelArchitecture(
                type="cnn",
                layers=[
                    {"type": "Conv2d", "params": {"in_channels": 3}},
                    {"type": "Linear", "params": {"in_features": 1024}}
                ],
                total_parameters=10000000
            ),
            patterns=[],
            components=[]
        )
        
    @pytest.fixture
    def gpu_hardware(self):
        """Create GPU hardware profile."""
        return HardwareProfile(
            device_type="GPU",
            device_name="NVIDIA V100",
            compute_capability=7.0,
            memory_gb=16,
            fp16_support=True,
            int8_support=True,
            tensor_cores=True
        )
        
    @pytest.fixture
    def cpu_hardware(self):
        """Create CPU hardware profile."""
        return HardwareProfile(
            device_type="CPU",
            device_name="Intel Xeon",
            memory_gb=64,
            int8_support=True,
            fp16_support=False,
            tensor_cores=False
        )
        
    def test_check_framework_compatibility(self, checker, mixed_precision_technique, sample_analysis, gpu_hardware):
        """Test framework compatibility checking."""
        compatibility = checker.check(
            mixed_precision_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert isinstance(compatibility, Compatibility)
        assert compatibility.is_compatible is True
        assert compatibility.framework_compatible is True
        assert "PyTorch 1.9.0 supports this technique" in compatibility.reason
        
    def test_check_hardware_compatibility(self, checker, mixed_precision_technique, sample_analysis, gpu_hardware, cpu_hardware):
        """Test hardware compatibility checking."""
        # GPU should be compatible
        gpu_compat = checker.check(
            mixed_precision_technique,
            sample_analysis,
            gpu_hardware
        )
        assert gpu_compat.hardware_compatible is True
        assert gpu_compat.is_compatible is True
        
        # CPU should not be compatible
        cpu_compat = checker.check(
            mixed_precision_technique,
            sample_analysis,
            cpu_hardware
        )
        assert cpu_compat.hardware_compatible is False
        assert cpu_compat.is_compatible is False
        assert "GPU required" in cpu_compat.reason
        
    def test_check_compute_capability(self, checker, mixed_precision_technique, sample_analysis):
        """Test compute capability requirements."""
        # Old GPU
        old_gpu = HardwareProfile(
            device_type="GPU",
            device_name="NVIDIA GTX 1080",
            compute_capability=6.1,
            fp16_support=True,
            tensor_cores=False
        )
        
        compatibility = checker.check(
            mixed_precision_technique,
            sample_analysis,
            old_gpu
        )
        
        assert compatibility.is_compatible is False
        assert "Requires compute capability >= 7.0" in compatibility.reason
        assert "Requires Tensor Cores" in compatibility.reason
        
    def test_check_version_requirements(self, checker, mixed_precision_technique, gpu_hardware):
        """Test framework version requirements."""
        # Old PyTorch version
        old_analysis = AnalysisResult(
            framework="pytorch",
            code_context=CodeContext(
                framework="pytorch",
                version="1.5.0"
            ),
            model_architecture=None,
            patterns=[],
            components=[]
        )
        
        compatibility = checker.check(
            mixed_precision_technique,
            old_analysis,
            gpu_hardware
        )
        
        assert compatibility.is_compatible is False
        assert compatibility.framework_compatible is False
        assert "Requires PyTorch >= 1.6.0" in compatibility.reason
        
    def test_check_model_compatibility(self, checker, quantization_technique, gpu_hardware):
        """Test model architecture compatibility."""
        # Model with unsupported layers
        analysis_with_custom = AnalysisResult(
            framework="pytorch",
            code_context=CodeContext(framework="pytorch", version="1.9.0"),
            model_architecture=ModelArchitecture(
                type="custom",
                layers=[
                    {"type": "CustomAttention", "params": {}},
                    {"type": "DynamicConv", "params": {}}
                ],
                has_dynamic_shapes=True
            ),
            patterns=[],
            components=[]
        )
        
        compatibility = checker.check(
            quantization_technique,
            analysis_with_custom,
            gpu_hardware
        )
        
        assert compatibility.confidence < 1.0  # Lower confidence for custom layers
        assert "custom layers" in compatibility.warnings[0].lower()
        
    def test_check_conflict_detection(self, checker, quantization_technique, pruning_technique, sample_analysis, gpu_hardware):
        """Test technique conflict detection."""
        # Apply quantization first
        sample_analysis.patterns = [
            Mock(name="int8_quantization", technique="INT8 Quantization")
        ]
        
        # Check if pruning is compatible
        compatibility = checker.check(
            pruning_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert compatibility.is_compatible is False
        assert "Conflicts with INT8 Quantization" in compatibility.reason
        assert compatibility.conflicts_with == ["INT8 Quantization"]
        
    def test_check_synergy_detection(self, checker, sample_analysis, gpu_hardware):
        """Test technique synergy detection."""
        # Gradient accumulation technique
        grad_accum = Technique(
            name="Gradient Accumulation",
            category="training",
            frameworks=["pytorch", "tensorflow"],
            synergizes_with=["Mixed Precision Training"]
        )
        
        # Apply mixed precision first
        sample_analysis.patterns = [
            Mock(name="mixed_precision", technique="Mixed Precision Training")
        ]
        
        compatibility = checker.check(
            grad_accum,
            sample_analysis,
            gpu_hardware
        )
        
        assert compatibility.is_compatible is True
        assert compatibility.synergizes_with == ["Mixed Precision Training"]
        assert "Works well with Mixed Precision" in compatibility.reason
        
    def test_check_memory_requirements(self, checker, sample_analysis):
        """Test memory requirement checking."""
        # Large model technique
        model_parallel = Technique(
            name="Model Parallelism",
            category="distributed",
            frameworks=["pytorch"],
            min_memory_gb=32,
            hardware_requirements=["gpu"]
        )
        
        # Small GPU
        small_gpu = HardwareProfile(
            device_type="GPU",
            device_name="NVIDIA GTX 1660",
            compute_capability=7.5,
            memory_gb=6
        )
        
        compatibility = checker.check(
            model_parallel,
            sample_analysis,
            small_gpu
        )
        
        assert compatibility.is_compatible is False
        assert "Requires at least 32GB memory" in compatibility.reason
        
    def test_check_data_type_support(self, checker, sample_analysis):
        """Test data type support checking."""
        # BF16 technique
        bf16_technique = Technique(
            name="BFloat16 Training",
            category="training",
            frameworks=["pytorch"],
            requires_bf16_support=True,
            hardware_requirements=["gpu"]
        )
        
        # GPU without BF16
        gpu_no_bf16 = HardwareProfile(
            device_type="GPU",
            device_name="NVIDIA V100",
            compute_capability=7.0,
            bf16_support=False,
            fp16_support=True
        )
        
        compatibility = checker.check(
            bf16_technique,
            sample_analysis,
            gpu_no_bf16
        )
        
        assert compatibility.is_compatible is False
        assert "BFloat16 support required" in compatibility.reason
        
    def test_batch_compatibility_check(self, checker, sample_analysis, gpu_hardware):
        """Test checking multiple techniques at once."""
        techniques = [
            Technique(name="Tech1", frameworks=["pytorch"]),
            Technique(name="Tech2", frameworks=["pytorch"], conflicts_with=["Tech1"]),
            Technique(name="Tech3", frameworks=["pytorch"], requires=["Tech1"])
        ]
        
        results = checker.check_batch(
            techniques,
            sample_analysis,
            gpu_hardware
        )
        
        assert len(results) == 3
        assert results["Tech1"].is_compatible is True
        assert results["Tech2"].is_compatible is False  # Conflicts with Tech1
        assert results["Tech3"].is_compatible is True  # Requires Tech1 which is compatible
        
    def test_compatibility_score(self, checker, mixed_precision_technique, sample_analysis, gpu_hardware):
        """Test compatibility scoring."""
        compatibility = checker.check(
            mixed_precision_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert 0 <= compatibility.confidence <= 1.0
        assert compatibility.confidence > 0.8  # High confidence for good match
        
        # Test partial compatibility
        sample_analysis.model_architecture.has_custom_ops = True
        compatibility_partial = checker.check(
            mixed_precision_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert compatibility_partial.confidence < compatibility.confidence
        
    def test_prerequisite_checking(self, checker, sample_analysis, gpu_hardware):
        """Test checking technique prerequisites."""
        # Technique with prerequisites
        advanced_technique = Technique(
            name="Advanced Optimization",
            category="training",
            frameworks=["pytorch"],
            prerequisites=["Basic Optimization", "CUDA Toolkit >= 11.0"]
        )
        
        compatibility = checker.check(
            advanced_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert len(compatibility.missing_prerequisites) > 0
        assert "Basic Optimization" in compatibility.missing_prerequisites
        
    def test_performance_impact_estimation(self, checker, quantization_technique, sample_analysis, gpu_hardware):
        """Test estimating performance impact."""
        compatibility = checker.check(
            quantization_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert compatibility.estimated_speedup > 0
        assert compatibility.estimated_memory_reduction > 0
        
        # Should adjust based on hardware
        cpu_compat = checker.check(
            quantization_technique,
            sample_analysis,
            Mock(device_type="CPU", int8_support=True)
        )
        
        # CPU might have different performance characteristics
        assert cpu_compat.estimated_speedup != compatibility.estimated_speedup
        
    def test_implementation_difficulty(self, checker, mixed_precision_technique, sample_analysis, gpu_hardware):
        """Test assessing implementation difficulty."""
        compatibility = checker.check(
            mixed_precision_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert compatibility.implementation_difficulty in ["easy", "medium", "hard"]
        assert compatibility.estimated_hours > 0
        
        # Complex model should increase difficulty
        sample_analysis.model_architecture.complexity_score = 0.9
        compatibility_complex = checker.check(
            mixed_precision_technique,
            sample_analysis,
            gpu_hardware
        )
        
        assert compatibility_complex.implementation_difficulty == "medium" or "hard"
        assert compatibility_complex.estimated_hours > compatibility.estimated_hours