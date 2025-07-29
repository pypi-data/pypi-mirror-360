# DeepOptimizer: Pre-flight Checks for ML Code ✈️

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Created by [Willy Nilsson](https://willynilsson.com)

Inspired by how pilots use checklists to ensure safety, DeepOptimizer provides systematic analysis of ML code before training. It combines fast pattern detection with Gemini AI insights to catch issues and suggest optimizations.

## 🚀 Project Components

### 1. CLI Tool (`deepoptimizer/`)
A command-line tool that analyzes Python ML code:
- Fast rule-based detection of common ML bugs
- Gemini AI-powered deep analysis
- 70+ optimization techniques in knowledge base
- Beautiful terminal output with multiple export formats

### 2. Web Interface (`website/`)
Static showcase site with:
- Project overview and installation guide
- Interactive technique demonstrations
- Examples of detected issues
- Author information

## 📦 Quick Start

### CLI Tool (Recommended for developers)

```bash
# Install from TestPyPI (release candidate)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ deepoptimizer==0.1.0rc1

# Or install from source
git clone https://github.com/willynilsson/deepoptimizer.git
cd deepoptimizer
pip install -e .

# Set up API key
echo 'GEMINI_API_KEY=your-api-key-here' > .env

# Analyze code
deepoptimizer analyze model.py
deepoptimizer analyze ./my_project --no-llm  # Fast, rule-based only
deepoptimizer techniques --search attention   # Browse optimization techniques
```

### Web Documentation

Visit [willynilsson.github.io/deepoptimizer](https://willynilsson.github.io/deepoptimizer) for project documentation and examples.

### Development Setup

```bash
# Clone repository
git clone https://github.com/willynilsson/deepoptimizer.git
cd deepoptimizer

# CLI development
pip install -e ".[dev]"
pytest  # Run tests

# Website development
cd website
npm install
npm run dev  # Start dev server at localhost:5173
```

## 🎯 What It Does

DeepOptimizer helps ML engineers by:

1. **Finding Bugs**: Detects common issues like missing `model.eval()`, memory leaks, wrong loss functions
2. **Improving Performance**: Suggests optimizations like mixed precision, better batch sizes, efficient attention
3. **Teaching Best Practices**: Provides research-backed suggestions with implementation examples
4. **Saving Time**: Automated analysis that would take hours to do manually

### Example Issues Detected

```python
# ❌ Missing model.eval() during validation
def validate(model, dataloader):
    for batch in dataloader:  # model still in training mode!
        output = model(batch)

# ❌ Memory leak from accumulating tensors
total_loss = 0
for batch in dataloader:
    loss = criterion(model(batch), target)
    total_loss += loss  # Keeps computation graph!

# ❌ Wrong loss function
loss = F.mse_loss(output, labels)  # MSE for classification!

# ✅ DeepOptimizer detects these and provides fixes
```

## 📊 Features

### CLI Features
- **Multi-severity analysis**: Errors, warnings, and suggestions
- **Project-wide analysis**: Analyze entire codebases
- **Export formats**: Terminal, JSON, Markdown
- **Configuration files**: `.deepoptimizer` for project settings
- **Offline mode**: Use `--no-llm` for fast rule-based analysis

### Detection Capabilities
- Training/validation bugs (missing eval mode, no_grad)
- Memory leaks and inefficiencies
- Wrong loss functions for tasks
- Suboptimal hyperparameters
- Missing optimizations (mixed precision, etc.)
- Architecture issues (no skip connections, etc.)

### Knowledge Base
- 55+ optimization techniques
- Conflict detection between techniques
- Framework-specific implementations
- Hardware-specific optimizations
- Research paper citations

## 🛠️ Architecture

```
DeepOptimizer/
├── deepoptimizer/          # CLI tool (main package)
│   ├── analyzer.py         # Main analysis orchestrator
│   ├── llm_analyzer.py     # Gemini AI integration
│   ├── rule_detector.py    # Fast pattern matching
│   ├── knowledge_base.py   # Optimization techniques
│   └── fixtures/           # 55+ ML optimization techniques
└── website/                # Static React showcase site
    └── src/components/     # Interactive demos
```

The CLI tool runs completely standalone with user-provided Gemini API keys.

## 💡 Use Cases

1. **Code Reviews**: Automatically catch ML-specific issues
2. **Performance Tuning**: Get suggestions for faster training/inference
3. **Learning**: Understand optimization techniques with examples
4. **CI/CD Integration**: Add to pipelines for automated checks

## 🤝 Contributing

This is a portfolio project, but contributions are welcome! Areas of interest:
- Adding more detection rules
- Expanding the knowledge base
- Improving LLM prompts
- Adding support for more frameworks

## 📝 License

Apache License 2.0 - see [LICENSE](LICENSE) file. Created by Willy Nilsson.

This license provides patent protection and ensures proper attribution while remaining business-friendly and open source.

## 🧠 About the Author

Built by [Willy Nilsson](https://willynilsson.com). The concept was inspired by aviation psychology - how pilots use checklists to manage complex systems safely. My background in psychology and programming led to applying these principles to ML development.

Currently seeking opportunities in AI/ML tooling development.

- Personal Site: [willynilsson.com](https://willynilsson.com)
- GitHub: [@willynilsson](https://github.com/willynilsson)
- LinkedIn: [linkedin.com/in/willynilsson](https://linkedin.com/in/willynilsson)