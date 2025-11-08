"""
Core analysis modules for prompt508.
Contains all analyzers and utilities for accessibility assessment.
"""

from .advisor import AccessibilityAdvisor
from .readability import ReadabilityAnalyzer
from .jargon import JargonDetector
from .tone import ToneAnalyzer
from .accessibility import AccessibilityInjector

__all__ = [
    "AccessibilityAdvisor",
    "ReadabilityAnalyzer",
    "JargonDetector",
    "ToneAnalyzer",
    "AccessibilityInjector",
]
