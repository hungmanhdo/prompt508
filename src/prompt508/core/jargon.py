"""
Jargon detection module for prompt508.
Uses spaCy to detect uncommon terms, undefined acronyms, and technical jargon.
"""

import spacy
from typing import Dict, List, Set, Optional
from collections import Counter
from .utils import load_json_rules, find_acronyms, clean_text


class JargonDetector:
    """
    Detector for technical jargon, undefined acronyms, and complex terminology.
    
    Uses spaCy for NLP analysis and rule-based detection from gov_plain_language.json
    to identify terms that should be simplified or defined.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the jargon detector.
        
        Args:
            model_name: spaCy model to use (default: en_core_web_sm)
        
        Note:
            Requires spaCy model to be installed:
            python -m spacy download en_core_web_sm
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()
        self._load_rules()
    
    def _load_model(self) -> None:
        """Load the spaCy model, providing helpful error if not installed."""
        try:
            self.nlp = spacy.load(self.model_name)
        except OSError:
            raise OSError(
                f"spaCy model '{self.model_name}' not found. "
                f"Please install it with: python -m spacy download {self.model_name}"
            )
    
    def _load_rules(self) -> None:
        """Load jargon rules from JSON files."""
        try:
            plain_lang_rules = load_json_rules("gov_plain_language.json")
            self.jargon_replacements = plain_lang_rules.get("replacements", {})
            self.acronym_expansions = plain_lang_rules.get("acronym_expansions", {})
            
            replacement_rules = load_json_rules("replacements.json")
            self.tech_simplifications = replacement_rules.get("technical_simplifications", {})
        except Exception as e:
            # Fallback to empty dicts if rules can't be loaded
            self.jargon_replacements = {}
            self.acronym_expansions = {}
            self.tech_simplifications = {}
    
    def detect_jargon(self, text: str) -> Dict[str, any]:
        """
        Detect jargon and complex terminology in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing:
                - jargon_words: List of detected jargon terms
                - jargon_count: Total number of jargon instances
                - undefined_acronyms: Acronyms without definitions
                - acronym_count: Total number of acronyms
                - complex_words: Words with 3+ syllables
                - suggestions: Dictionary mapping jargon to plain language alternatives
                - jargon_ratio: Percentage of words that are jargon
                - has_issues: Whether jargon issues were found
        """
        cleaned_text = clean_text(text)
        
        if not cleaned_text:
            return self._empty_result()
        
        # Process text with spaCy
        doc = self.nlp(cleaned_text)
        
        # Find jargon terms
        jargon_words = self._find_jargon_terms(doc)
        
        # Find acronyms
        acronyms = find_acronyms(text)
        undefined_acronyms = [
            acr for acr in acronyms 
            if acr not in self.acronym_expansions
        ]
        
        # Find complex words (3+ syllables, not proper nouns)
        complex_words = self._find_complex_words(doc)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(jargon_words, undefined_acronyms)
        
        # Calculate jargon ratio
        total_words = len([token for token in doc if token.is_alpha])
        jargon_count = len(jargon_words)
        jargon_ratio = (jargon_count / total_words * 100) if total_words > 0 else 0.0
        
        return {
            'jargon_words': sorted(list(set(jargon_words))),
            'jargon_count': jargon_count,
            'undefined_acronyms': sorted(undefined_acronyms),
            'acronym_count': len(acronyms),
            'complex_words': sorted(list(set(complex_words))),
            'suggestions': suggestions,
            'jargon_ratio': round(jargon_ratio, 2),
            'has_issues': jargon_count > 0 or len(undefined_acronyms) > 0
        }
    
    def _find_jargon_terms(self, doc) -> List[str]:
        """
        Find jargon terms in the document.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of jargon terms found
        """
        jargon = []
        
        for token in doc:
            # Skip punctuation and short words
            if not token.is_alpha or len(token.text) < 4:
                continue
            
            word_lower = token.text.lower()
            
            # Check against known jargon replacements
            if word_lower in self.jargon_replacements:
                jargon.append(token.text)
            
            # Check against technical simplifications
            elif word_lower in self.tech_simplifications:
                jargon.append(token.text)
            
            # Check for words with Latin/Greek roots (common in jargon)
            elif self._is_likely_jargon(token):
                jargon.append(token.text)
        
        return jargon
    
    def _is_likely_jargon(self, token) -> bool:
        """
        Heuristic to detect likely jargon based on word characteristics.
        
        Args:
            token: spaCy Token object
            
        Returns:
            True if token is likely jargon
        """
        text = token.text.lower()
        
        # Common jargon suffixes
        jargon_suffixes = ['ize', 'ization', 'tion', 'ment', 'ance', 'ence', 'ity', 'ology']
        
        # Check for jargon suffixes on longer words
        if len(text) > 8:
            for suffix in jargon_suffixes:
                if text.endswith(suffix):
                    return True
        
        # Words with unusual letter combinations
        if any(combo in text for combo in ['ph', 'sch', 'tch', 'dge']):
            if len(text) > 10:
                return True
        
        return False
    
    def _find_complex_words(self, doc) -> List[str]:
        """
        Find words with 3 or more syllables (typically more difficult).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of complex words
        """
        complex_words = []
        
        for token in doc:
            if not token.is_alpha or len(token.text) < 3:
                continue
            
            # Simple syllable counting heuristic
            if self._count_syllables(token.text) >= 3:
                # Exclude proper nouns and common words
                if not token.pos_ == "PROPN":
                    complex_words.append(token.text)
        
        return complex_words
    
    def _count_syllables(self, word: str) -> int:
        """
        Simple syllable counting (vowel groups).
        
        Args:
            word: Word to count syllables in
            
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
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _generate_suggestions(self, jargon_words: List[str], 
                             undefined_acronyms: List[str]) -> Dict[str, str]:
        """
        Generate plain language suggestions for jargon.
        
        Args:
            jargon_words: List of jargon terms
            undefined_acronyms: List of undefined acronyms
            
        Returns:
            Dictionary mapping jargon to suggestions
        """
        suggestions = {}
        
        # Add suggestions for jargon words
        for word in jargon_words:
            word_lower = word.lower()
            
            if word_lower in self.jargon_replacements:
                suggestions[word] = self.jargon_replacements[word_lower]
            elif word_lower in self.tech_simplifications:
                suggestions[word] = self.tech_simplifications[word_lower]
        
        # Add suggestions for undefined acronyms
        for acronym in undefined_acronyms:
            if acronym in self.acronym_expansions:
                suggestions[acronym] = self.acronym_expansions[acronym]
            else:
                suggestions[acronym] = f"Define '{acronym}' on first use"
        
        return suggestions
    
    def _empty_result(self) -> Dict[str, any]:
        """Return empty result for empty text."""
        return {
            'jargon_words': [],
            'jargon_count': 0,
            'undefined_acronyms': [],
            'acronym_count': 0,
            'complex_words': [],
            'suggestions': {},
            'jargon_ratio': 0.0,
            'has_issues': False
        }
    
    def get_summary(self, text: str) -> str:
        """
        Get a human-readable summary of jargon analysis.
        
        Args:
            text: Input text
            
        Returns:
            Formatted summary string
        """
        result = self.detect_jargon(text)
        
        summary = f"""
Jargon Analysis:
  Jargon Terms Found: {result['jargon_count']}
  Jargon Ratio: {result['jargon_ratio']}%
  Undefined Acronyms: {len(result['undefined_acronyms'])}
  Complex Words: {len(result['complex_words'])}

"""
        
        if result['jargon_words']:
            summary += "Jargon Terms:\n"
            for word in result['jargon_words'][:10]:  # Show first 10
                suggestion = result['suggestions'].get(word, "Consider simplifying")
                summary += f"  - {word} → {suggestion}\n"
        
        if result['undefined_acronyms']:
            summary += "\nUndefined Acronyms:\n"
            for acronym in result['undefined_acronyms']:
                summary += f"  - {acronym} (define on first use)\n"
        
        if not result['has_issues']:
            summary += "\nNo significant jargon issues detected."
        
        return summary.strip()


def detect_jargon(text: str, model_name: str = "en_core_web_sm") -> Dict[str, any]:
    """
    Convenience function to detect jargon in text.
    
    Args:
        text: Input text
        model_name: spaCy model to use
        
    Returns:
        Jargon analysis results
    """
    detector = JargonDetector(model_name=model_name)
    return detector.detect_jargon(text)
