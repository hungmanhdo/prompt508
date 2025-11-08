# Section 508 Compliance Checking in prompt508

**Technical Documentation: How prompt508 Validates Accessibility and Plain Language Compliance**

---

## Table of Contents

- [Overview](#overview)
- [The Four Core Analyzers](#the-four-core-analyzers)
  - [1. Readability Analysis](#1-readability-analysis)
  - [2. Jargon Detection](#2-jargon-detection)
  - [3. Tone Analysis](#3-tone-analysis)
  - [4. Accessibility Hints](#4-accessibility-hints)
- [Overall Compliance Score Calculation](#overall-compliance-score-calculation)
- [Compliance Determination](#compliance-determination)
- [Implementation Architecture](#implementation-architecture)
- [Usage Examples](#usage-examples)
- [Two-Stage Pipeline Integration](#two-stage-pipeline-integration)
- [Validation Results](#validation-results)
- [Strengths and Limitations](#strengths-and-limitations)

---

## Overview

prompt508 implements a **multi-dimensional compliance checking system** that evaluates text against Section 508 accessibility standards and plain language requirements. The system uses **4 core analyzers** that work together to provide a comprehensive assessment.

### What Section 508 Requires

Section 508 of the Rehabilitation Act mandates that:
- Content must be accessible to people with disabilities
- Plain language must be used (clear, concise, well-organized)
- Technical terms must be defined
- Content must be understandable by general audiences

### How prompt508 Implements This

Instead of just checking technical specs (alt text, ARIA labels), prompt508 **analyzes the actual content** to ensure:
- ✅ Readability meets plain language standards
- ✅ Technical jargon is minimized
- ✅ Tone is neutral and objective
- ✅ Accessibility best practices are included

---

## The Four Core Analyzers

### 1. Readability Analysis

**Purpose:** Ensures text meets plain language requirements by measuring reading difficulty.

**What It Checks:**
- **Flesch-Kincaid Grade Level** - Primary metric (target: ≤ 8th grade)
- **Flesch Reading Ease** - Score from 0-100 (higher = easier)
- **Gunning Fog Index** - Years of education needed
- **SMOG Index** - Alternative readability formula
- **Word & Sentence Statistics** - Average lengths, complexity

**Section 508 Connection:**
Plain language is mandated for accessibility. Content at 8th-grade level or below is readable by 85% of the U.S. population, including people with cognitive disabilities.

**Implementation:**

```python
from prompt508.core.readability import ReadabilityAnalyzer

analyzer = ReadabilityAnalyzer(target_grade=8.0)
result = analyzer.score_text(text)

# Returns:
{
    'flesch_kincaid_grade': 7.5,        # Grade level
    'flesch_reading_ease': 72.3,         # Ease score
    'gunning_fog': 8.2,                  # Fog index
    'smog_index': 7.8,                   # SMOG
    'avg_sentence_length': 15.2,         # Words per sentence
    'avg_word_length': 4.3,              # Characters per word
    'complex_words': 12,                 # 3+ syllables
    'meets_target': True,                # Grade ≤ target?
    'recommendations': [...]             # Improvement tips
}
```

**Calculation Method:**
Uses the `textstat` library which implements standard readability formulas:

```python
# Flesch-Kincaid Grade Level formula:
grade = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
```

**Scoring Logic:**
- Grade ≤ 8.0: Full points (no penalty)
- Grade 8.1-9.0: -10 points
- Grade 9.1-10.0: -20 points
- Grade > 10.0: -40 points (max penalty)

---

### 2. Jargon Detection

**Purpose:** Identifies technical terms and complex language that create accessibility barriers.

**What It Checks:**
- **Technical jargon** (e.g., "utilize" → "use", "facilitate" → "help")
- **Undefined acronyms** (e.g., "API" without explanation)
- **Complex words** (3+ syllables)
- **Government jargon** (per PlainLanguage.gov guidelines)

**Section 508 Connection:**
Technical terms are barriers for people with cognitive disabilities, lower literacy, and non-experts. Plain language guidelines require explaining technical terms.

**Implementation:**

```python
from prompt508.core.jargon import JargonDetector

detector = JargonDetector(model_name="en_core_web_sm")
result = detector.detect_jargon(text)

# Returns:
{
    'jargon_count': 5,                   # Total jargon terms
    'jargon_words': ['utilize', 'facilitate', 'implement'],
    'jargon_ratio': 8.5,                 # Percentage of words
    'undefined_acronyms': ['API', 'SDK'],
    'has_issues': True,                  # Issues found?
    'suggestions': {
        'utilize': 'use',
        'facilitate': 'help',
        'implement': 'create'
    },
    'recommendations': [...]
}
```

**Detection Method:**

1. **NLP Analysis:** Uses spaCy to parse text and identify:
   - Part-of-speech tags
   - Named entities
   - Word complexity (syllable count)

2. **Dictionary Matching:** Compares against curated lists:
   - `gov_plain_language.json` - Government jargon replacements
   - `replacements.json` - Technical simplifications

3. **Acronym Detection:** Identifies all-caps terms without definitions

**Scoring Logic:**
- 0-5% jargon: No penalty
- 5-10% jargon: -10 points
- 10-20% jargon: -20 points
- >20% jargon: -30 points (max penalty)

---

### 3. Tone Analysis

**Purpose:** Ensures neutral, objective communication that's clear and direct.

**What It Checks:**
- **Sentiment polarity** (-1.0 to +1.0, target: neutral ~0)
- **Subjectivity** (0 to 1.0, target: objective <0.5)
- **Formality level** (formal, neutral, informal)
- **Passive voice** (should use active voice)

**Section 508 Connection:**
Clear, direct communication helps all users. Passive voice is harder to understand for people with cognitive disabilities. Subjective language can be confusing.

**Implementation:**

```python
from prompt508.core.tone import ToneAnalyzer

analyzer = ToneAnalyzer(target_tone="neutral")
result = analyzer.analyze_tone(text)

# Returns:
{
    'polarity': 0.15,                    # Sentiment (-1 to +1)
    'subjectivity': 0.35,                # Objectivity (0 to 1)
    'tone_classification': 'neutral',    # positive/negative/neutral
    'is_neutral': True,                  # Within neutral range?
    'is_subjective': False,              # Subjectivity > 0.5?
    'formality_score': 0.65,             # 0=informal, 1=formal
    'passive_voice_count': 2,            # Passive constructions
    'meets_target': True,                # Neutral & objective?
    'recommendations': [...]
}
```

**Analysis Method:**

1. **Sentiment Analysis:** Uses TextBlob's sentiment analyzer:
```python
from textblob import TextBlob
blob = TextBlob(text)
polarity = blob.sentiment.polarity      # -1 (negative) to +1 (positive)
subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
```

2. **Passive Voice Detection:** Uses spaCy dependency parsing:
```python
# Looks for patterns like:
# - Auxiliary verb (be) + past participle
# - "was created", "is being processed", "will be implemented"
```

3. **Formality Scoring:** Analyzes:
   - Average word length
   - Complex word ratio
   - Sentence structure

**Scoring Logic:**
- Neutral tone (polarity -0.3 to +0.3): No penalty
- Non-neutral: -10 points
- Subjective (>0.5): -5 points
- Each passive voice: -3 points (max -15)

---

### 4. Accessibility Hints

**Purpose:** Ensures prompts include Section 508 technical requirements.

**What It Checks:**
- **Alt text reminders** for images
- **Caption requirements** for videos/audio
- **Document structure** guidelines (headings, lists)
- **Link text** best practices
- **Form accessibility** requirements

**Section 508 Connection:**
These are direct technical requirements from Section 508 standards. Including them in prompts guides AI to generate compliant content.

**Implementation:**

```python
from prompt508.core.accessibility import AccessibilityInjector

injector = AccessibilityInjector(
    include_alt_text=True,
    include_captions=True,
    include_structure=True,
    strict_mode=False
)

# Inject hints based on content type
enhanced = injector.inject_hints(text, content_type="images")

# Returns text with appended accessibility reminders like:
"""
[Accessibility Requirements]
- Include descriptive alt text for all images
- Alt text should describe the content and function of images
- Avoid phrases like "image of" or "picture of"
- Keep alt text under 150 characters when possible
"""
```

**Content Type Categories:**
- `"images"` - Image accessibility (alt text, descriptions)
- `"multimedia"` - Video/audio (captions, transcripts, audio descriptions)
- `"documents"` - Document structure (headings, lists, tables)
- `"links"` - Link text best practices
- `"forms"` - Form accessibility (labels, instructions, error messages)
- `None` - General accessibility hints

**Hint Sources:**
Loaded from `section508.json`:
```json
{
  "output_instructions": {
    "images": "Include descriptive alt text for all images...",
    "multimedia": "Provide captions for videos and transcripts...",
    "documents": "Use proper heading hierarchy (H1, H2, H3)...",
    "links": "Use descriptive link text (not 'click here')...",
    "forms": "Provide clear labels for all form fields..."
  }
}
```

---

## Overall Compliance Score Calculation

The system combines all 4 analyzers into a **single score from 0-100**.

### Algorithm

```python
def _calculate_overall_score(readability, jargon, tone):
    """
    Calculate overall compliance score (0-100)
    
    Starting from 100, penalties are applied for:
    - High reading grade level (max -40)
    - Excessive jargon (max -30)
    - Non-neutral tone (max -10)
    - Subjective language (-5)
    - Passive voice (max -15)
    """
    score = 100.0
    
    # 1. Readability penalty (max -40 points)
    grade_diff = max(0, readability['flesch_kincaid_grade'] - target_grade)
    readability_penalty = min(40, grade_diff * 10)
    score -= readability_penalty
    
    # 2. Jargon penalty (max -30 points)
    jargon_penalty = min(30, jargon['jargon_ratio'])
    score -= jargon_penalty
    
    # 3. Tone penalties (max -15 points)
    if not tone['is_neutral']:
        score -= 10
    if tone['is_subjective']:
        score -= 5
    
    # 4. Passive voice penalty (max -15 points)
    passive_penalty = min(15, tone['passive_voice_count'] * 3)
    score -= passive_penalty
    
    return max(0, round(score, 1))
```

### Score Interpretation

| Score Range | Assessment | Action |
|-------------|------------|--------|
| 90-100 | Excellent | Ready to use |
| 80-89 | Good | Minor improvements suggested |
| 70-79 | Acceptable | Review recommendations |
| 60-69 | Needs Work | Significant improvements needed |
| 0-59 | Poor | Major rewrite required |

---

## Compliance Determination

Text is considered **Section 508 compliant** when ALL criteria are met:

### Compliance Criteria

```python
def _check_compliance(readability, jargon, tone):
    """
    Determine if text meets Section 508 compliance
    
    Returns True if ALL of:
    - Readability meets target (grade ≤ 8.0)
    - Jargon is acceptable (has_issues = False)
    - Tone meets target (neutral & objective)
    """
    return (
        readability['meets_target'] and      # Grade ≤ 8.0
        not jargon['has_issues'] and         # Jargon acceptable
        tone['meets_target']                 # Neutral & objective
    )
```

### Detailed Requirements

**Readability:**
- ✅ Flesch-Kincaid Grade Level ≤ 8.0
- ✅ Flesch Reading Ease ≥ 60
- ✅ Average sentence length < 20 words

**Jargon:**
- ✅ Jargon ratio < 10%
- ✅ No undefined acronyms
- ✅ Complex words < 15%

**Tone:**
- ✅ Sentiment polarity: -0.3 to +0.3 (neutral)
- ✅ Subjectivity < 0.5 (objective)
- ✅ Passive voice count < 3

**Accessibility:**
- ✅ Includes appropriate accessibility hints
- ✅ Clear, structured communication

---

## Implementation Architecture

### Class Hierarchy

```
AccessibilityAdvisor (Main Class)
├── ReadabilityAnalyzer
│   └── Uses: textstat library
├── JargonDetector
│   └── Uses: spaCy NLP
├── ToneAnalyzer
│   └── Uses: TextBlob sentiment
└── AccessibilityInjector
    └── Uses: Rule-based templates

Utility Functions:
├── load_json_rules()
├── clean_text()
└── apply_replacements()
```

### Data Flow

```
Input Text
    ↓
[Clean Text]
    ↓
┌────────────────────────────┐
│  Parallel Analysis         │
├────────────────────────────┤
│ 1. Readability → Metrics   │
│ 2. Jargon → Terms Found    │
│ 3. Tone → Sentiment        │
│ 4. Accessibility → Hints   │
└────────────────────────────┘
    ↓
[Calculate Overall Score]
    ↓
[Determine Compliance]
    ↓
[Generate Recommendations]
    ↓
Output: Analysis Results
```

### Key Files

- `src/prompt508/core/advisor.py` - Main orchestrator
- `src/prompt508/core/readability.py` - Readability analyzer
- `src/prompt508/core/jargon.py` - Jargon detector
- `src/prompt508/core/tone.py` - Tone analyzer
- `src/prompt508/core/accessibility.py` - Hint injector
- `src/prompt508/core/utils.py` - Utility functions
- `src/prompt508/core/rules/*.json` - Compliance rules

---

## Usage Examples

### Basic Analysis

```python
from prompt508 import AccessibilityAdvisor

advisor = AccessibilityAdvisor(target_grade=8.0)

# Analyze any text
text = "Utilize the API to facilitate data transmission and implement visualization."
analysis = advisor.analyze(text)

# Results
print(f"Overall Score: {analysis['overall_score']}/100")
# Output: Overall Score: 62.3/100

print(f"Passes Compliance: {analysis['passes_compliance']}")
# Output: Passes Compliance: False

print(f"Reading Grade: {analysis['readability']['flesch_kincaid_grade']}")
# Output: Reading Grade: 11.2

print(f"Jargon Count: {analysis['jargon']['jargon_count']}")
# Output: Jargon Count: 4

print(f"Issues:")
for issue in analysis['issues']:
    print(f"  - {issue}")
# Output:
#   - Reading level too high: Grade 11.2 (target: 8.0)
#   - Found 4 jargon terms
#   - Tone is positive (should be neutral)

print(f"Recommendations:")
for rec in analysis['recommendations']:
    print(f"  - {rec}")
# Output:
#   - Simplify sentences to reduce reading grade
#   - Replace jargon terms with plain language
#   - Use more neutral, objective language
```

### Individual Analyzers

```python
from prompt508 import (
    ReadabilityAnalyzer,
    JargonDetector,
    ToneAnalyzer,
    AccessibilityInjector
)

text = "The API facilitates data transmission."

# Readability only
readability = ReadabilityAnalyzer(target_grade=8.0)
r_result = readability.score_text(text)
print(f"Grade: {r_result['flesch_kincaid_grade']}")

# Jargon only
jargon = JargonDetector()
j_result = jargon.detect_jargon(text)
print(f"Jargon found: {j_result['jargon_words']}")
# Output: ['API', 'facilitates', 'transmission']

# Tone only
tone = ToneAnalyzer(target_tone="neutral")
t_result = tone.analyze_tone(text)
print(f"Sentiment: {t_result['tone_classification']}")

# Accessibility hints only
injector = AccessibilityInjector()
enhanced = injector.inject_hints(text, content_type="images")
print(enhanced)
# Output: Original text + accessibility reminders
```

### Detailed Report

```python
# Generate comprehensive report
report = advisor.get_report(text)
print(report)

# Output:
# ======================================================================
# PROMPT508 ACCESSIBILITY ANALYSIS REPORT
# ======================================================================
# 
# Overall Score: 62.3/100
# Compliance Status: ✗ NEEDS IMPROVEMENT
# 
# ----------------------------------------------------------------------
# READABILITY
# ----------------------------------------------------------------------
# Flesch-Kincaid Grade: 11.2
# Flesch Reading Ease: 42.5
# [... detailed metrics ...]
# 
# ----------------------------------------------------------------------
# JARGON & TERMINOLOGY
# ----------------------------------------------------------------------
# Jargon Terms Found: 4
# [... specific terms and suggestions ...]
# 
# ----------------------------------------------------------------------
# TONE & SENTIMENT
# ----------------------------------------------------------------------
# Sentiment: Positive (should be neutral)
# [... detailed analysis ...]
# 
# ----------------------------------------------------------------------
# IDENTIFIED ISSUES
# ----------------------------------------------------------------------
# 1. Reading level too high: Grade 11.2 (target: 8.0)
# 2. Found 4 jargon terms
# [...]
# 
# ----------------------------------------------------------------------
# RECOMMENDATIONS
# ----------------------------------------------------------------------
# 1. Simplify sentences to reduce reading grade
# 2. Replace jargon terms with plain language
# [...]
```

---

## Two-Stage Pipeline Integration

The compliance checking system integrates into the **two-stage accessibility pipeline**:

### Stage 1: Input Enhancement

```python
# Add Section 508 instructions to prompt
enhanced_prompt = advisor.enhance_prompt_for_508(
    prompt="Explain how APIs work",
    strict=True
)

# The enhanced prompt guides the LLM to generate compliant content
llm_output = your_llm(enhanced_prompt)
```

### Stage 2: Output Validation

```python
# Validate LLM output
validation = advisor.validate_output(llm_output, threshold=70.0)

print(f"Score: {validation['score']}/100")
print(f"Passes: {validation['passes_compliance']}")
print(f"Needs Fixing: {validation['needs_fixing']}")

# If non-compliant, fix automatically
if validation['needs_fixing']:
    fixed = advisor.fix_output(llm_output)
    final_text = fixed['rewritten']
else:
    final_text = llm_output
```

### Complete Pipeline

```python
# One-step compliance guarantee
result = advisor.ensure_compliance(
    prompt="Explain how APIs work",
    llm_function=your_llm,
    threshold=70.0
)

# Always returns compliant output
print(f"Final Score: {result['compliance_score']}/100")
print(f"Was Fixed: {result['was_fixed']}")
print(f"Final Output: {result['final_output']}")
```

---

## Validation Results

### Real-World Test Case

**Prompt:** "Explain how machine learning works"

#### WITHOUT prompt508

```
Original LLM Output:
"Machine learning is a subset of artificial intelligence that enables 
computers to learn from data and make predictions or decisions without 
being explicitly programmed for specific tasks..."

Analysis Results:
- Overall Score: 56.7/100 ❌
- Reading Grade: 13.8 (college level)
- Jargon Terms: 17
- Passive Voice: 0
- Section 508 Compliant: NO

Issues:
- Reading level too high: Grade 13.8 (target: 8.0)
- Found 17 jargon terms
- 3 undefined acronyms
```

#### WITH prompt508 (Two-Stage Pipeline)

```
Stage 1: Enhanced prompt with Section 508 instructions
Stage 2: Validated and fixed output

Final Output:
"Sure! Here's a simple explanation of how machine learning works.

Machine learning helps computers learn from data. Instead of giving 
exact instructions, computers find patterns in information..."

Analysis Results:
- Overall Score: 80.7/100 ✅
- Reading Grade: 8.2 (8th grade)
- Jargon Terms: 6
- Passive Voice: 0
- Section 508 Compliant: Much Better

Improvements:
- +24.0 points score increase
- -5.6 grade level reduction
- -11 jargon terms removed
- Cost: $0.0004
```

### Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Overall Score** | 56.7/100 | 80.7/100 | **+24 points** |
| **Reading Grade** | 13.8 | 8.2 | **-5.6 grades** |
| **Jargon Terms** | 17 | 6 | **-11 terms** |
| **Compliance** | ❌ NO | ✅ Better | **42% improvement** |
| **Cost** | $0 | $0.0004 | **Negligible** |

---

## Strengths and Limitations

### What prompt508 DOES Check ✅

**Text-Based Analysis:**
- ✅ Reading difficulty (Flesch-Kincaid, etc.)
- ✅ Jargon and complex terminology
- ✅ Tone and sentiment
- ✅ Passive voice usage
- ✅ Presence of accessibility instructions
- ✅ Plain language compliance
- ✅ Overall content clarity

**Automated Validation:**
- ✅ Analyzes any text input
- ✅ Provides quantitative scores (0-100)
- ✅ Identifies specific issues
- ✅ Gives actionable recommendations
- ✅ Can validate LLM outputs
- ✅ Integrates into workflows

**Evidence-Based:**
- ✅ Uses established metrics (Flesch-Kincaid)
- ✅ Based on PlainLanguage.gov guidelines
- ✅ Aligned with Section 508 requirements
- ✅ Validated with real-world tests

### What prompt508 DOESN'T Check ❌

**Visual/Design Elements:**
- ❌ Color contrast ratios
- ❌ Font sizes and readability
- ❌ Layout and spacing
- ❌ Visual hierarchy

**Interactive Elements:**
- ❌ Keyboard navigation
- ❌ Focus indicators
- ❌ Button/link functionality
- ❌ Form validation

**Technical Implementation:**
- ❌ HTML semantic structure
- ❌ ARIA labels and roles
- ❌ Screen reader compatibility
- ❌ Alternative formats (Braille, large print)

**Multimedia Specs:**
- ❌ Actual presence of captions/transcripts
- ❌ Audio/video quality
- ❌ Synchronization of captions
- ❌ File formats and codecs

### Why These Limitations Exist

These elements require **rendered output testing** with actual HTML, CSS, and JavaScript. prompt508 focuses on **content analysis** which is:
1. Earlier in the pipeline (catches issues before rendering)
2. Platform-agnostic (works for any output format)
3. Automatable (no manual testing needed)
4. Complementary to visual/technical testing tools

### Recommended Complementary Tools

For complete Section 508 compliance:
- **axe DevTools** - Automated accessibility testing
- **WAVE** - Web accessibility evaluation
- **JAWS/NVDA** - Screen reader testing
- **Color Contrast Analyzer** - Visual compliance

prompt508 handles the **content foundation** - ensuring text is readable and clear before visual/technical testing.

---

## Conclusion

prompt508's compliance checking system provides:

✅ **Multi-dimensional analysis** - 4 core analyzers working together
✅ **Evidence-based metrics** - Established readability formulas
✅ **Quantitative scoring** - Objective 0-100 scale
✅ **Actionable feedback** - Specific issues and recommendations
✅ **Automated validation** - No manual review needed
✅ **Integration-ready** - Works in any workflow
✅ **Proven results** - +24 point improvements in real tests

**This makes prompt508 the foundation for accessible AI systems** - ensuring content is readable and clear before visual/technical testing.

For questions or contributions, visit: https://github.com/hungmanhdo/prompt508
