"""
Utility functions for DeepOptimizer.
"""
import ast
import re
import sys
import os
from pathlib import Path
from typing import List, Optional, Set


def find_python_files(directory: Path, 
                     include_patterns: List[str] = None,
                     exclude_patterns: List[str] = None) -> List[Path]:
    """
    Find Python files in a directory based on patterns.
    
    Args:
        directory: Root directory to search
        include_patterns: Glob patterns to include (default: ['**/*.py'])
        exclude_patterns: Glob patterns to exclude
        
    Returns:
        List of Python file paths
    """
    if include_patterns is None:
        include_patterns = ['**/*.py']
    
    if exclude_patterns is None:
        exclude_patterns = [
            '**/venv/**', '**/env/**', '**/.venv/**',
            '**/__pycache__/**', '**/site-packages/**',
            '**/node_modules/**', '**/.git/**',
            '**/build/**', '**/dist/**'
        ]
    
    files = set()
    
    # Find files matching include patterns
    for pattern in include_patterns:
        files.update(directory.glob(pattern))
    
    # Filter out excluded patterns
    filtered_files = []
    for file_path in files:
        excluded = False
        for exclude_pattern in exclude_patterns:
            if file_path.match(exclude_pattern):
                excluded = True
                break
        
        if not excluded and file_path.is_file():
            filtered_files.append(file_path)
    
    return sorted(filtered_files)


def extract_imports(code: str) -> List[str]:
    """Extract imported modules from Python code."""
    imports = []
    
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])
    except Exception:
        # Fallback to regex if AST parsing fails
        import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            imports.extend(matches)
    
    return list(set(imports))


def detect_framework(code: str) -> str:
    """Detect which ML framework is being used."""
    imports = extract_imports(code)
    
    # Check for frameworks in order of specificity
    framework_indicators = {
        'torch': 'PyTorch',
        'pytorch': 'PyTorch',
        'tensorflow': 'TensorFlow',
        'tf': 'TensorFlow',
        'keras': 'TensorFlow/Keras',
        'jax': 'JAX',
        'flax': 'JAX/Flax',
        'sklearn': 'scikit-learn',
        'xgboost': 'XGBoost',
        'lightgbm': 'LightGBM',
        'mxnet': 'MXNet',
        'paddle': 'PaddlePaddle'
    }
    
    for module, framework in framework_indicators.items():
        if module in imports:
            return framework
    
    # Check code content as fallback
    code_lower = code.lower()
    if 'torch' in code_lower or 'pytorch' in code_lower:
        return 'PyTorch'
    elif 'tensorflow' in code_lower or 'keras' in code_lower:
        return 'TensorFlow'
    elif 'jax' in code_lower:
        return 'JAX'
    
    return 'Unknown'


def estimate_model_size(code: str) -> Optional[int]:
    """Estimate model parameter count from code."""
    # This is a rough estimation based on layer definitions
    param_count = 0
    
    # PyTorch patterns
    pytorch_patterns = [
        (r'nn\.Linear\((\d+),\s*(\d+)\)', lambda m: int(m[1]) * int(m[2])),
        (r'nn\.Conv2d\((\d+),\s*(\d+),\s*(\d+)', lambda m: int(m[1]) * int(m[2]) * int(m[3]) * int(m[3])),
        (r'nn\.Embedding\((\d+),\s*(\d+)\)', lambda m: int(m[1]) * int(m[2]))
    ]
    
    for pattern, calc_func in pytorch_patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            try:
                param_count += calc_func(match.groups())
            except Exception:
                pass
    
    return param_count if param_count > 0 else None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def is_test_file(file_path: Path) -> bool:
    """Check if a file is likely a test file."""
    name = file_path.name.lower()
    
    test_patterns = [
        'test_', '_test.py', 'tests.py',
        'spec_', '_spec.py',
        'conftest.py', 'pytest'
    ]
    
    return any(pattern in name for pattern in test_patterns)


def is_ml_code(code: str) -> bool:
    """Check if code likely contains ML/DL logic."""
    ml_indicators = [
        # Frameworks
        'torch', 'tensorflow', 'keras', 'jax', 'sklearn',
        
        # Common ML terms
        'model', 'train', 'optimizer', 'loss', 'accuracy',
        'dataset', 'dataloader', 'epoch', 'batch',
        
        # Layer types
        'conv2d', 'linear', 'lstm', 'embedding', 'attention',
        'dense', 'dropout', 'batchnorm', 'layernorm',
        
        # Operations
        'forward', 'backward', 'gradient', 'backprop'
    ]
    
    code_lower = code.lower()
    matches = sum(1 for indicator in ml_indicators if indicator in code_lower)
    
    # Consider it ML code if we find at least 3 indicators
    return matches >= 3


def extract_code_snippet(code: str, line_number: int, context_lines: int = 3) -> str:
    """Extract a code snippet around a specific line number."""
    lines = code.split('\n')
    
    if line_number < 1 or line_number > len(lines):
        return ""
    
    # Calculate range (1-indexed to 0-indexed)
    start = max(0, line_number - 1 - context_lines)
    end = min(len(lines), line_number + context_lines)
    
    # Extract lines with line numbers
    snippet_lines = []
    for i in range(start, end):
        line_num = i + 1
        prefix = ">>> " if line_num == line_number else "    "
        snippet_lines.append(f"{line_num:4d} {prefix}{lines[i]}")
    
    return '\n'.join(snippet_lines)


def parse_config_file(config_path: Path) -> dict:
    """Parse .deepoptimizer configuration file."""
    config = {
        'api_key': None,
        'analysis': {
            'use_llm': True,
            'output_format': 'rich',
            'include_patterns': ['**/*.py'],
            'exclude_patterns': ['**/venv/**', '**/__pycache__/**'],
            'severity_filter': 'all'
        },
        'performance': {
            'max_workers': 4,
            'llm_timeout': 30
        }
    }
    
    if not config_path.exists():
        return config
    
    try:
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)
        
        # Update config with parsed values
        if 'DEFAULT' in parser and 'api_key' in parser['DEFAULT']:
            config['api_key'] = parser['DEFAULT']['api_key']
        
        if 'analysis' in parser:
            for key, value in parser['analysis'].items():
                if key in ['include_patterns', 'exclude_patterns']:
                    # Parse list values
                    config['analysis'][key] = [
                        v.strip() for v in value.split(',')
                    ]
                elif key == 'use_llm':
                    config['analysis'][key] = parser.getboolean('analysis', key)
                else:
                    config['analysis'][key] = value
        
        if 'performance' in parser:
            for key, value in parser['performance'].items():
                if key in ['max_workers', 'llm_timeout']:
                    config['performance'][key] = int(value)
                    
    except Exception as e:
        # Error parsing config file
        pass
    
    return config


def create_diff(original: str, modified: str, file_path: str = "file") -> str:
    """Create a unified diff between two strings."""
    import difflib
    
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"{file_path} (original)",
        tofile=f"{file_path} (fixed)",
        lineterm=''
    )
    
    return ''.join(diff)


def safe_print(text: str) -> str:
    """
    Make text safe for Windows console output by removing Unicode characters.
    
    Args:
        text: Text that may contain Unicode/emoji characters
        
    Returns:
        Text with emojis replaced by ASCII equivalents
    """
    # Only apply replacements on Windows without Unicode support
    if sys.platform == 'win32' and not supports_unicode():
        # Map of emojis to ASCII replacements
        replacements = {
            '🏥': '[DOCTOR]',
            '✅': '[OK]',
            '❌': '[FAIL]',
            '⚠️': '[WARN]',
            '🔍': '[SEARCH]',
            '📦': '[PACKAGE]',
            '🎯': '[TARGET]',
            '💡': '[TIP]',
            '🚀': '[ROCKET]',
            '📊': '[STATS]',
            '🧠': '[BRAIN]',
            '📝': '[NOTE]',
            '🛠️': '[TOOLS]',
            '🔧': '[WRENCH]',
            '🐛': '[BUG]',
            '⚡': '[PERF]',
            '📚': '[DOCS]',
            '🔴': '[RED]',
            '🟡': '[YELLOW]',
            '🟢': '[GREEN]',
            '📁': '[FOLDER]',
            '📄': '[FILE]',
            '🚨': '[ERROR]',
            'ℹ️': '[INFO]',
            '🏗️': '[ARCH]',
            '🚫': '[ANTI]',
            '🔗': '[COMPAT]',
            '✨': '[STAR]',
            '💻': '[CODE]',
        }
        
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
    
    return text


def is_windows_terminal() -> bool:
    """Check if running in Windows Terminal (which supports Unicode)."""
    # Windows Terminal sets this environment variable
    return os.environ.get('WT_SESSION') is not None


def supports_unicode() -> bool:
    """Check if the current terminal supports Unicode output."""
    if sys.platform != 'win32':
        return True
    
    # Check if Windows Terminal
    if is_windows_terminal():
        return True
    
    # Check if UTF-8 mode is enabled
    try:
        return sys.stdout.encoding.lower() in ('utf-8', 'utf8', 'utf_8')
    except:
        return False