"""
prompt508: Accessibility & Plain-Language Optimizer for AI Prompts
Section 508 Compliance for AI Systems

A Python library for analyzing and optimizing AI prompts to ensure they meet
U.S. Section 508 accessibility and plain-language compliance standards.
"""

__version__ = "0.1.0"
__author__ = "Hung Manh Do"
__license__ = "MIT"

# Import main classes for convenience
from .core.advisor import AccessibilityAdvisor
from .core.readability import ReadabilityAnalyzer, score_text
from .core.jargon import JargonDetector, detect_jargon
from .core.tone import ToneAnalyzer, analyze_tone
from .core.accessibility import AccessibilityInjector, inject_accessibility_hints

# Define public API
__all__ = [
    # Main advisor class
    "AccessibilityAdvisor",
    
    # Individual analyzers
    "ReadabilityAnalyzer",
    "JargonDetector",
    "ToneAnalyzer",
    "AccessibilityInjector",
    
    # Convenience functions
    "score_text",
    "detect_jargon",
    "analyze_tone",
    "inject_accessibility_hints",
]
