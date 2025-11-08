"""
Readability analysis module for prompt508.
Computes Flesch-Kincaid grade level and other readability metrics using textstat.
"""

import textstat
from typing import Dict, Optional
from .utils import clean_text, split_sentences, count_words, get_grade_level_description


class ReadabilityAnalyzer:
    """
    Analyzer for text readability metrics.

    Uses multiple readability formulas to assess text complexity and
    determine if text meets plain language guidelines (target: 8th grade level).
    """

    def __init__(self, target_grade: float = 8.0):
        """
        Initialize the readability analyzer.

        Args:
            target_grade: Target reading grade level (default: 8.0 for plain language)
        """
        self.target_grade = target_grade

    def score_text(self, text: str) -> Dict[str, any]:
        """
        Compute comprehensive readability scores for text.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing:
                - flesch_kincaid_grade: Flesch-Kincaid Grade Level
                - flesch_reading_ease: Flesch Reading Ease score (0-100)
                - gunning_fog: Gunning Fog Index
                - smog_index: SMOG Index
                - coleman_liau: Coleman-Liau Index
                - automated_readability: Automated Readability Index
                - word_count: Total words
                - sentence_count: Total sentences
                - avg_sentence_length: Average words per sentence
                - meets_target: Whether text meets target grade level
                - grade_description: Human-readable grade level description
                - recommendations: List of improvement suggestions
        """
        # Clean the text
        cleaned_text = clean_text(text)

        if not cleaned_text:
            return self._empty_result()

        # Compute various readability metrics
        fk_grade = textstat.flesch_kincaid_grade(cleaned_text)
        flesch_ease = textstat.flesch_reading_ease(cleaned_text)
        gunning_fog = textstat.gunning_fog(cleaned_text)
        smog = textstat.smog_index(cleaned_text)
        coleman_liau = textstat.coleman_liau_index(cleaned_text)
        ari = textstat.automated_readability_index(cleaned_text)

        # Get text statistics
        word_count = textstat.lexicon_count(cleaned_text, removepunct=True)
        sentence_count = textstat.sentence_count(cleaned_text)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Determine if text meets target
        meets_target = fk_grade <= self.target_grade

        # Generate recommendations
        recommendations = self._generate_recommendations(
            fk_grade, flesch_ease, avg_sentence_length, word_count
        )

        return {
            "flesch_kincaid_grade": round(fk_grade, 2),
            "flesch_reading_ease": round(flesch_ease, 2),
            "gunning_fog": round(gunning_fog, 2),
            "smog_index": round(smog, 2),
            "coleman_liau": round(coleman_liau, 2),
            "automated_readability": round(ari, 2),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "meets_target": meets_target,
            "target_grade": self.target_grade,
            "grade_description": get_grade_level_description(fk_grade),
            "recommendations": recommendations,
        }

    def _empty_result(self) -> Dict[str, any]:
        """Return empty/default results for empty text."""
        return {
            "flesch_kincaid_grade": 0.0,
            "flesch_reading_ease": 100.0,
            "gunning_fog": 0.0,
            "smog_index": 0.0,
            "coleman_liau": 0.0,
            "automated_readability": 0.0,
            "word_count": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0.0,
            "meets_target": True,
            "target_grade": self.target_grade,
            "grade_description": "No text to analyze",
            "recommendations": ["Provide text for analysis"],
        }

    def _generate_recommendations(
        self, fk_grade: float, flesch_ease: float, avg_sentence_length: float, word_count: int
    ) -> list:
        """
        Generate actionable recommendations based on readability scores.

        Args:
            fk_grade: Flesch-Kincaid grade level
            flesch_ease: Flesch Reading Ease score
            avg_sentence_length: Average sentence length
            word_count: Total word count

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Grade level recommendations
        if fk_grade > self.target_grade:
            diff = fk_grade - self.target_grade
            recommendations.append(
                f"Text is {diff:.1f} grade levels above target ({self.target_grade}). "
                "Simplify vocabulary and sentence structure."
            )
        elif fk_grade > self.target_grade + 2:
            recommendations.append(
                "Text is significantly above target reading level. "
                "Consider breaking into shorter sentences and using simpler words."
            )

        # Reading ease recommendations
        if flesch_ease < 60:
            recommendations.append(
                "Text is difficult to read (Flesch Reading Ease < 60). "
                "Use shorter words and sentences."
            )
        elif flesch_ease < 70:
            recommendations.append("Text is fairly difficult to read. Consider simplifying.")

        # Sentence length recommendations
        if avg_sentence_length > 20:
            recommendations.append(
                f"Average sentence length ({avg_sentence_length:.1f} words) exceeds "
                "recommended maximum of 20 words. Break long sentences into shorter ones."
            )
        elif avg_sentence_length > 25:
            recommendations.append("Sentences are too long. Aim for 15-20 words per sentence.")

        # Positive feedback if all is well
        if not recommendations:
            recommendations.append(
                f"Text meets plain language guidelines (Grade {fk_grade:.1f}, "
                f"target: {self.target_grade}). Good readability!"
            )

        return recommendations

    def is_plain_language(self, text: str, strict: bool = False) -> bool:
        """
        Check if text meets plain language criteria.

        Args:
            text: Input text
            strict: If True, use stricter criteria (grade 6 instead of 8)

        Returns:
            True if text meets plain language standards
        """
        result = self.score_text(text)
        threshold = 6.0 if strict else self.target_grade
        return result["flesch_kincaid_grade"] <= threshold

    def get_summary(self, text: str) -> str:
        """
        Get a human-readable summary of readability analysis.

        Args:
            text: Input text

        Returns:
            Formatted summary string
        """
        result = self.score_text(text)

        summary = f"""
Readability Analysis:
  Grade Level: {result['flesch_kincaid_grade']} ({result['grade_description']})
  Target Grade: {result['target_grade']}
  Meets Target: {'Yes' if result['meets_target'] else 'No'}
  
  Reading Ease: {result['flesch_reading_ease']}/100
  Word Count: {result['word_count']}
  Sentence Count: {result['sentence_count']}
  Avg Sentence Length: {result['avg_sentence_length']} words

Recommendations:
"""
        for i, rec in enumerate(result["recommendations"], 1):
            summary += f"  {i}. {rec}\n"

        return summary.strip()


def score_text(text: str, target_grade: float = 8.0) -> Dict[str, any]:
    """
    Convenience function to score text readability.

    Args:
        text: Input text
        target_grade: Target reading grade level

    Returns:
        Readability analysis results
    """
    analyzer = ReadabilityAnalyzer(target_grade=target_grade)
    return analyzer.score_text(text)
