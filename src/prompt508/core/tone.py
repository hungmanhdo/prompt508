"""
Tone and sentiment analysis module for prompt508.
Uses TextBlob to analyze tone, sentiment, and formality level.
"""

from textblob import TextBlob
from typing import Dict, List
from .utils import clean_text, split_sentences


class ToneAnalyzer:
    """
    Analyzer for text tone and sentiment.
    
    Uses TextBlob to detect sentiment (positive/negative/neutral) and 
    assess whether tone is appropriate for accessible, inclusive content.
    """
    
    def __init__(self, target_tone: str = "neutral"):
        """
        Initialize the tone analyzer.
        
        Args:
            target_tone: Desired tone ("neutral", "positive", "formal", "informal")
        """
        self.target_tone = target_tone
    
    def analyze_tone(self, text: str) -> Dict[str, any]:
        """
        Analyze the tone and sentiment of text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing:
                - sentiment_polarity: Sentiment score (-1 to 1, negative to positive)
                - sentiment_subjectivity: Subjectivity score (0 to 1, objective to subjective)
                - tone_classification: Classification (negative, neutral, positive)
                - is_neutral: Whether tone is appropriately neutral
                - is_subjective: Whether text is too subjective
                - formality_score: Estimated formality level
                - passive_voice_count: Number of passive voice constructions
                - recommendations: List of tone improvement suggestions
        """
        cleaned_text = clean_text(text)
        
        if not cleaned_text:
            return self._empty_result()
        
        # Analyze with TextBlob
        blob = TextBlob(cleaned_text)
        
        # Get sentiment scores
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify tone
        tone_class = self._classify_tone(polarity)
        
        # Check neutrality and subjectivity
        is_neutral = abs(polarity) < 0.1
        is_subjective = subjectivity > 0.5
        
        # Estimate formality
        formality = self._estimate_formality(blob)
        
        # Count passive voice
        passive_count = self._count_passive_voice(text)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            polarity, subjectivity, is_neutral, is_subjective, 
            passive_count, formality
        )
        
        return {
            'sentiment_polarity': round(polarity, 3),
            'sentiment_subjectivity': round(subjectivity, 3),
            'tone_classification': tone_class,
            'is_neutral': is_neutral,
            'is_subjective': is_subjective,
            'formality_score': formality,
            'passive_voice_count': passive_count,
            'recommendations': recommendations,
            'meets_target': self._meets_target(polarity, subjectivity, formality)
        }
    
    def _classify_tone(self, polarity: float) -> str:
        """
        Classify tone based on polarity score.
        
        Args:
            polarity: Sentiment polarity (-1 to 1)
            
        Returns:
            Tone classification string
        """
        if polarity < -0.1:
            return "negative"
        elif polarity > 0.1:
            return "positive"
        else:
            return "neutral"
    
    def _estimate_formality(self, blob: TextBlob) -> str:
        """
        Estimate formality level based on text characteristics.
        
        Args:
            blob: TextBlob object
            
        Returns:
            Formality level ("formal", "neutral", "informal")
        """
        text = str(blob)
        
        # Check for formal indicators
        formal_indicators = [
            'utilize', 'facilitate', 'implement', 'subsequently',
            'therefore', 'furthermore', 'moreover', 'consequently'
        ]
        
        # Check for informal indicators
        informal_indicators = [
            "don't", "can't", "won't", "it's", "that's",
            'gonna', 'wanna', 'gotta'
        ]
        
        formal_count = sum(1 for word in formal_indicators if word in text.lower())
        informal_count = sum(1 for word in informal_indicators if word in text.lower())
        
        if formal_count > informal_count + 2:
            return "formal"
        elif informal_count > formal_count + 2:
            return "informal"
        else:
            return "neutral"
    
    def _count_passive_voice(self, text: str) -> int:
        """
        Count passive voice constructions (simple heuristic).
        
        Args:
            text: Input text
            
        Returns:
            Estimated count of passive voice sentences
        """
        # Simple passive voice indicators
        passive_indicators = [
            'is being', 'was being', 'are being', 'were being',
            'has been', 'have been', 'had been',
            'will be', 'will have been',
            'is done', 'was done', 'are done', 'were done'
        ]
        
        text_lower = text.lower()
        count = sum(1 for indicator in passive_indicators if indicator in text_lower)
        
        return count
    
    def _meets_target(self, polarity: float, subjectivity: float, 
                      formality: str) -> bool:
        """
        Check if tone meets target criteria.
        
        Args:
            polarity: Sentiment polarity
            subjectivity: Subjectivity score
            formality: Formality level
            
        Returns:
            True if tone meets targets
        """
        if self.target_tone == "neutral":
            return abs(polarity) < 0.15 and subjectivity < 0.6
        elif self.target_tone == "positive":
            return polarity > 0.1 and subjectivity < 0.7
        elif self.target_tone == "formal":
            return formality == "formal" and subjectivity < 0.5
        elif self.target_tone == "informal":
            return formality == "informal" or formality == "neutral"
        
        return True
    
    def _generate_recommendations(
        self,
        polarity: float,
        subjectivity: float,
        is_neutral: bool,
        is_subjective: bool,
        passive_count: int,
        formality: str
    ) -> List[str]:
        """
        Generate tone improvement recommendations.
        
        Args:
            polarity: Sentiment polarity
            subjectivity: Subjectivity score
            is_neutral: Whether tone is neutral
            is_subjective: Whether text is subjective
            passive_count: Count of passive voice
            formality: Formality level
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Polarity recommendations
        if polarity < -0.2:
            recommendations.append(
                "Text has negative tone. For accessible content, maintain neutral or "
                "slightly positive tone to be welcoming."
            )
        elif polarity > 0.3:
            recommendations.append(
                "Text has strong positive tone. While positive is good, avoid "
                "overly enthusiastic language that may seem unprofessional."
            )
        
        # Subjectivity recommendations
        if is_subjective:
            recommendations.append(
                f"Text is highly subjective (score: {subjectivity:.2f}). "
                "Use more objective, fact-based language for accessibility compliance."
            )
        
        # Formality recommendations
        if formality == "formal" and self.target_tone != "formal":
            recommendations.append(
                "Text is overly formal. Plain language guidelines recommend "
                "conversational but professional tone. Avoid bureaucratic language."
            )
        elif formality == "informal" and self.target_tone == "formal":
            recommendations.append(
                "Text is too informal. Use more professional language while "
                "maintaining accessibility."
            )
        
        # Passive voice recommendations
        if passive_count > 0:
            recommendations.append(
                f"Found {passive_count} passive voice constructions. "
                "Use active voice for clearer, more direct communication. "
                "Example: Change 'The report was written by...' to 'John wrote the report.'"
            )
        
        # Positive feedback
        if not recommendations:
            recommendations.append(
                f"Tone is appropriate ({self._get_tone_description(polarity)}). "
                "Text maintains professional and accessible language."
            )
        
        return recommendations
    
    def _get_tone_description(self, polarity: float) -> str:
        """Get human-readable tone description."""
        if polarity < -0.3:
            return "very negative"
        elif polarity < -0.1:
            return "slightly negative"
        elif polarity > 0.3:
            return "very positive"
        elif polarity > 0.1:
            return "slightly positive"
        else:
            return "neutral"
    
    def _empty_result(self) -> Dict[str, any]:
        """Return empty result for empty text."""
        return {
            'sentiment_polarity': 0.0,
            'sentiment_subjectivity': 0.0,
            'tone_classification': 'neutral',
            'is_neutral': True,
            'is_subjective': False,
            'formality_score': 'neutral',
            'passive_voice_count': 0,
            'recommendations': ['No text to analyze'],
            'meets_target': True
        }
    
    def get_summary(self, text: str) -> str:
        """
        Get a human-readable summary of tone analysis.
        
        Args:
            text: Input text
            
        Returns:
            Formatted summary string
        """
        result = self.analyze_tone(text)
        
        summary = f"""
Tone Analysis:
  Sentiment: {result['tone_classification'].title()} (polarity: {result['sentiment_polarity']})
  Subjectivity: {result['sentiment_subjectivity']:.2f} {'(Objective)' if result['sentiment_subjectivity'] < 0.5 else '(Subjective)'}
  Formality: {result['formality_score'].title()}
  Passive Voice: {result['passive_voice_count']} instances
  Meets Target: {'Yes' if result['meets_target'] else 'No'}

Recommendations:
"""
        for i, rec in enumerate(result['recommendations'], 1):
            summary += f"  {i}. {rec}\n"
        
        return summary.strip()


def analyze_tone(text: str, target_tone: str = "neutral") -> Dict[str, any]:
    """
    Convenience function to analyze text tone.
    
    Args:
        text: Input text
        target_tone: Desired tone
        
    Returns:
        Tone analysis results
    """
    analyzer = ToneAnalyzer(target_tone=target_tone)
    return analyzer.analyze_tone(text)
