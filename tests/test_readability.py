"""
Basic tests for the readability module.
"""

import pytest
from prompt508.core.readability import ReadabilityAnalyzer, score_text


def test_readability_analyzer_initialization():
    """Test that ReadabilityAnalyzer initializes correctly."""
    analyzer = ReadabilityAnalyzer(target_grade=8.0)
    assert analyzer.target_grade == 8.0


def test_score_text_simple():
    """Test basic text scoring."""
    text = "The cat sat on the mat. It was a nice day."
    result = score_text(text, target_grade=8.0)
    
    # Check that all expected keys are present
    assert 'flesch_kincaid_grade' in result
    assert 'flesch_reading_ease' in result
    assert 'word_count' in result
    assert 'sentence_count' in result
    assert 'meets_target' in result
    assert 'recommendations' in result
    
    # Check that word count is reasonable
    assert result['word_count'] > 0
    assert result['sentence_count'] == 2


def test_score_text_empty():
    """Test that empty text is handled properly."""
    result = score_text("", target_grade=8.0)
    
    assert result['word_count'] == 0
    assert result['meets_target'] is True
    assert 'Provide text for analysis' in result['recommendations'][0]


def test_complex_text_detection():
    """Test that complex text is flagged."""
    complex_text = """
    The implementation of sophisticated methodologies necessitates 
    the utilization of comprehensive analytical frameworks to facilitate 
    the optimization of subsequent operational procedures.
    """
    
    result = score_text(complex_text, target_grade=8.0)
    
    # Complex text should have high grade level
    assert result['flesch_kincaid_grade'] > 8.0
    assert result['meets_target'] is False
    assert len(result['recommendations']) > 0


def test_simple_text_passes():
    """Test that simple text passes compliance."""
    simple_text = """
    We need to make a chart. Use simple words. Keep it clear and easy to read.
    """
    
    result = score_text(simple_text, target_grade=8.0)
    
    # Simple text should have low grade level
    assert result['flesch_kincaid_grade'] <= 8.0
    assert result['meets_target'] is True


def test_readability_summary():
    """Test that summary generation works."""
    analyzer = ReadabilityAnalyzer(target_grade=8.0)
    text = "The quick brown fox jumps over the lazy dog."
    
    summary = analyzer.get_summary(text)
    
    assert "Readability Analysis" in summary
    assert "Grade Level" in summary
    assert "Recommendations" in summary


def test_is_plain_language():
    """Test plain language detection."""
    analyzer = ReadabilityAnalyzer(target_grade=8.0)
    
    simple_text = "This is easy to read. Short sentences help."
    complex_text = "The implementation necessitates comprehensive evaluation."
    
    assert analyzer.is_plain_language(simple_text) is True
    assert analyzer.is_plain_language(complex_text) is False


def test_is_plain_language_strict():
    """Test strict plain language mode."""
    analyzer = ReadabilityAnalyzer(target_grade=8.0)
    
    # Text that passes grade 8 but not grade 6
    moderate_text = "We need to implement the solution quickly and effectively."
    
    # Should pass normal mode
    assert analyzer.is_plain_language(moderate_text, strict=False) is True
    
    # May not pass strict mode (grade 6)
    # This depends on the actual grade level, so we just test it runs
    result = analyzer.is_plain_language(moderate_text, strict=True)
    assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
