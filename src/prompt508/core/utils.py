"""
Utility functions for prompt508 package.
Shared helpers for loading rules, text processing, and configuration.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def get_rules_dir() -> Path:
    """Get the path to the rules directory."""
    return Path(__file__).parent / "rules"


def load_json_rules(filename: str) -> Dict[str, Any]:
    """
    Load a JSON rules file from the rules directory.
    
    Args:
        filename: Name of the JSON file (e.g., 'gov_plain_language.json')
        
    Returns:
        Dictionary containing the rules data
        
    Raises:
        FileNotFoundError: If the rules file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    rules_path = get_rules_dir() / filename
    
    if not rules_path.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def clean_text(text: str) -> str:
    """
    Clean and normalize text for analysis.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text with normalized whitespace
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences using simple heuristics.
    
    Args:
        text: Input text to split
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (can be improved with NLTK if needed)
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of words
    """
    words = text.split()
    return len([w for w in words if w.strip()])


def count_syllables(word: str) -> int:
    """
    Estimate syllable count for a word (simple heuristic).
    
    Args:
        word: Single word
        
    Returns:
        Estimated syllable count
    """
    word = word.lower()
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent e
    if word.endswith('e'):
        syllable_count -= 1
    
    # Ensure at least 1 syllable
    if syllable_count == 0:
        syllable_count = 1
        
    return syllable_count


def find_acronyms(text: str) -> List[str]:
    """
    Find potential acronyms (uppercase sequences) in text.
    
    Args:
        text: Input text
        
    Returns:
        List of found acronyms
    """
    # Match sequences of 2+ uppercase letters
    acronym_pattern = r'\b[A-Z]{2,}\b'
    acronyms = re.findall(acronym_pattern, text)
    return list(set(acronyms))  # Return unique acronyms


def apply_replacements(text: str, replacements: Dict[str, str], 
                       case_sensitive: bool = False) -> str:
    """
    Apply word/phrase replacements to text.
    
    Args:
        text: Input text
        replacements: Dictionary of {old: new} replacements
        case_sensitive: Whether to match case-sensitively
        
    Returns:
        Text with replacements applied
    """
    result = text
    
    for old, new in replacements.items():
        if case_sensitive:
            # Use word boundaries for exact matches
            pattern = r'\b' + re.escape(old) + r'\b'
            result = re.sub(pattern, new, result)
        else:
            # Case-insensitive replacement
            pattern = r'\b' + re.escape(old) + r'\b'
            result = re.sub(pattern, new, result, flags=re.IGNORECASE)
    
    return result


def format_score(score: float, decimal_places: int = 2) -> str:
    """
    Format a numerical score for display.
    
    Args:
        score: Numerical score
        decimal_places: Number of decimal places
        
    Returns:
        Formatted score string
    """
    return f"{score:.{decimal_places}f}"


def get_grade_level_description(grade: float) -> str:
    """
    Convert a numerical grade level to a description.
    
    Args:
        grade: Grade level number
        
    Returns:
        Description of reading level
    """
    if grade <= 5:
        return "Elementary (Easy to read)"
    elif grade <= 8:
        return "Middle School (Plain language target)"
    elif grade <= 12:
        return "High School (Moderately difficult)"
    elif grade <= 16:
        return "College (Difficult)"
    else:
        return "Graduate (Very difficult)"
