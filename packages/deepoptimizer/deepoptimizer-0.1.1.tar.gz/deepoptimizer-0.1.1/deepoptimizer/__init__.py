"""
DeepOptimizer - AI-powered ML code analysis and optimization suggestions.
"""

__version__ = "0.1.1"

from .analyzer import DeepOptimizer
from .llm_analyzer import GeminiAnalyzer

__all__ = ['DeepOptimizer', 'GeminiAnalyzer']