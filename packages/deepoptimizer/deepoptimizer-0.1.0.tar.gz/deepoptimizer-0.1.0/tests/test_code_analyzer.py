"""
Tests for the code analyzer agent.
"""

import pytest
from pathlib import Path
import tempfile
from deepoptimizer.agents.code_analyzer import CodeAnalyzer
from deepoptimizer.core.models import AnalysisResult


class TestCodeAnalyzer:
    """Test the CodeAnalyzer agent."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a CodeAnalyzer instance."""
        return CodeAnalyzer()
        
    @pytest.fixture
    def sample_pytorch_code(self):
        """Sample PyTorch code for testing."""
        return '''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

class CustomDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

class SimpleModel(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=256, output_dim=10):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Training configuration
model = SimpleModel()
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Data loading
train_dataset = CustomDataset(train_data, train_labels)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Training loop
for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
'''
        
    @pytest.fixture
    def sample_tensorflow_code(self):
        """Sample TensorFlow code for testing."""
        return '''
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Build model
model = keras.Sequential([
    layers.Dense(256, activation='relu', input_shape=(784,)),
    layers.Dropout(0.2),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(10, activation='softmax')
])

# Compile model
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Prepare data
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
x_train = x_train.reshape(-1, 784).astype('float32') / 255.0
x_test = x_test.reshape(-1, 784).astype('float32') / 255.0

# Train model
history = model.fit(
    x_train, y_train,
    batch_size=32,
    epochs=10,
    validation_split=0.1,
    callbacks=[
        keras.callbacks.EarlyStopping(patience=3),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2)
    ]
)
'''
        
    def test_analyze_pytorch_code(self, analyzer, sample_pytorch_code):
        """Test analyzing PyTorch code."""
        result = analyzer.analyze(sample_pytorch_code)
        
        assert isinstance(result, AnalysisResult)
        assert result.framework == 'pytorch'
        assert result.code_context.framework == 'pytorch'
        
        # Check model architecture detection
        assert result.model_architecture is not None
        assert result.model_architecture.type == 'feedforward'
        assert len(result.model_architecture.layers) > 0
        
        # Check component detection
        assert any(c.name == 'SimpleModel' for c in result.components)
        assert any(c.type == 'model' for c in result.components)
        assert any(c.type == 'optimizer' for c in result.components)
        assert any(c.type == 'dataset' for c in result.components)
        
    def test_analyze_tensorflow_code(self, analyzer, sample_tensorflow_code):
        """Test analyzing TensorFlow code."""
        result = analyzer.analyze(sample_tensorflow_code)
        
        assert result.framework == 'tensorflow'
        assert result.model_architecture is not None
        assert result.model_architecture.type == 'sequential'
        
        # Check optimization patterns
        assert any(p.name == 'callbacks' for p in result.patterns)
        
    def test_detect_optimization_patterns(self, analyzer):
        """Test detection of existing optimization patterns."""
        code_with_optimizations = '''
import torch
from torch.cuda.amp import autocast, GradScaler

model = torch.nn.Linear(10, 10)
optimizer = torch.optim.Adam(model.parameters())
scaler = GradScaler()

# Mixed precision training
for data, target in dataloader:
    optimizer.zero_grad()
    
    with autocast():
        output = model(data)
        loss = criterion(output, target)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    
# Model compilation
model = torch.compile(model, mode='reduce-overhead')

# Gradient accumulation
accumulation_steps = 4
for i, (data, target) in enumerate(dataloader):
    output = model(data)
    loss = criterion(output, target) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
'''
        
        result = analyzer.analyze(code_with_optimizations)
        
        pattern_names = [p.name for p in result.patterns]
        assert 'mixed_precision' in pattern_names
        assert 'torch_compile' in pattern_names
        assert 'gradient_accumulation' in pattern_names
        
    def test_analyze_file(self, analyzer, sample_pytorch_code):
        """Test analyzing code from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_pytorch_code)
            temp_path = f.name
            
        try:
            result = analyzer.analyze(temp_path)
            assert result.framework == 'pytorch'
            assert Path(result.file_path) == Path(temp_path)
        finally:
            Path(temp_path).unlink()
            
    def test_analyze_directory(self, analyzer):
        """Test analyzing a directory of code files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple Python files
            model_file = Path(temp_dir) / 'model.py'
            model_file.write_text('''
import torch.nn as nn

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 10)
''')
            
            train_file = Path(temp_dir) / 'train.py'
            train_file.write_text('''
import torch
from model import Model

model = Model()
optimizer = torch.optim.Adam(model.parameters())
''')
            
            result = analyzer.analyze(temp_dir)
            
            assert result.framework == 'pytorch'
            assert len(result.components) >= 2
            assert any(c.file_path.endswith('model.py') for c in result.components)
            assert any(c.file_path.endswith('train.py') for c in result.components)
            
    def test_extract_model_architecture(self, analyzer, sample_pytorch_code):
        """Test extracting detailed model architecture."""
        result = analyzer.analyze(sample_pytorch_code)
        arch = result.model_architecture
        
        assert arch.type == 'feedforward'
        assert arch.input_shape == (784,)
        assert arch.output_shape == (10,)
        
        # Check layer details
        layer_types = [layer.type for layer in arch.layers]
        assert 'Linear' in layer_types
        assert 'ReLU' in layer_types
        assert 'Dropout' in layer_types
        
        # Check parameter count
        assert arch.total_parameters > 0
        
    def test_detect_data_pipeline(self, analyzer, sample_pytorch_code):
        """Test detecting data loading and preprocessing."""
        result = analyzer.analyze(sample_pytorch_code)
        
        assert result.data_pipeline is not None
        assert result.data_pipeline.batch_size == 32
        assert result.data_pipeline.shuffle is True
        assert 'CustomDataset' in result.data_pipeline.dataset_type
        
    def test_detect_training_configuration(self, analyzer, sample_pytorch_code):
        """Test detecting training configuration."""
        result = analyzer.analyze(sample_pytorch_code)
        
        training_config = result.training_config
        assert training_config is not None
        assert training_config['optimizer'] == 'Adam'
        assert training_config['learning_rate'] == 0.001
        assert training_config['loss_function'] == 'CrossEntropyLoss'
        assert training_config['epochs'] == 10
        
    def test_complexity_analysis(self, analyzer):
        """Test code complexity analysis."""
        complex_code = '''
import torch
import torch.nn as nn

class ComplexModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, 3),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 3),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 3, 3),
            nn.Sigmoid()
        )
        
        self.attention = nn.MultiheadAttention(128, 8)
        
    def forward(self, x):
        encoded = self.encoder(x)
        
        # Complex branching
        if self.training:
            noise = torch.randn_like(encoded) * 0.1
            encoded = encoded + noise
            
        # Attention mechanism
        batch_size, channels, h, w = encoded.shape
        encoded_flat = encoded.view(batch_size, channels, -1).permute(2, 0, 1)
        attended, _ = self.attention(encoded_flat, encoded_flat, encoded_flat)
        attended = attended.permute(1, 2, 0).view(batch_size, channels, h, w)
        
        decoded = self.decoder(attended)
        return decoded
'''
        
        result = analyzer.analyze(complex_code)
        
        # Should detect higher complexity
        model_component = next(c for c in result.components if c.type == 'model')
        assert model_component.complexity > 50  # Arbitrary threshold
        
        # Should detect attention pattern
        assert any(p.name == 'attention' for p in result.patterns)
        
    def test_import_analysis(self, analyzer):
        """Test analyzing imports and dependencies."""
        code = '''
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
from transformers import BertModel, BertTokenizer
import custom_module
'''
        
        result = analyzer.analyze(code)
        
        dependencies = result.dependencies
        assert 'torch' in dependencies
        assert 'numpy' in dependencies
        assert 'transformers' in dependencies
        assert 'custom_module' in dependencies
        
        # Should identify external vs internal dependencies
        assert dependencies['torch']['type'] == 'external'
        assert dependencies['custom_module']['type'] == 'internal'
        
    def test_gpu_usage_detection(self, analyzer):
        """Test detecting GPU usage patterns."""
        gpu_code = '''
import torch

# GPU device selection
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = Model().to(device)
model = nn.DataParallel(model)

# Mixed precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

# CUDA operations
data = data.cuda()
with torch.cuda.stream(stream):
    output = model(data)
'''
        
        result = analyzer.analyze(gpu_code)
        
        assert result.hardware_usage is not None
        assert result.hardware_usage['gpu_required'] is True
        assert result.hardware_usage['multi_gpu'] is True
        assert 'mixed_precision' in result.hardware_usage['features']
        
    def test_memory_usage_estimation(self, analyzer, sample_pytorch_code):
        """Test estimating memory usage."""
        result = analyzer.analyze(sample_pytorch_code)
        
        memory_estimate = result.estimated_memory_usage
        assert memory_estimate is not None
        assert memory_estimate['model_size'] > 0
        assert memory_estimate['activation_memory'] > 0
        assert memory_estimate['optimizer_memory'] > 0
        
    def test_error_handling(self, analyzer):
        """Test handling of invalid code."""
        invalid_code = '''
import torch

# Syntax error
def model(
    return nn.Linear(10, 10)
'''
        
        with pytest.raises(SyntaxError):
            analyzer.analyze(invalid_code)
            
    def test_partial_analysis(self, analyzer):
        """Test analyzing incomplete code."""
        partial_code = '''
# Just imports, no model definition
import torch
import torch.nn as nn

# Configuration only
learning_rate = 0.001
batch_size = 32
'''
        
        result = analyzer.analyze(partial_code)
        
        assert result.framework == 'pytorch'
        assert result.model_architecture is None  # No model found
        assert len(result.components) == 0  # No major components
        
        # Should still extract configuration
        assert result.configuration is not None
        assert result.configuration['learning_rate'] == 0.001
        assert result.configuration['batch_size'] == 32
        
    def test_multi_model_detection(self, analyzer):
        """Test detecting multiple models in code."""
        multi_model_code = '''
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(100, 784)
        
class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(784, 1)
        
# GAN setup
G = Generator()
D = Discriminator()
'''
        
        result = analyzer.analyze(multi_model_code)
        
        models = [c for c in result.components if c.type == 'model']
        assert len(models) == 2
        assert any(m.name == 'Generator' for m in models)
        assert any(m.name == 'Discriminator' for m in models)
        
        # Should detect GAN pattern
        assert any(p.name == 'gan' for p in result.patterns)