# prompt508

**Accessibility & Plain-Language Optimizer for AI Prompts**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🎯 Section 508 Compliance for AI Systems

`prompt508` is an open-source Python library that analyzes and optimizes AI prompts to ensure they meet U.S. Section 508 accessibility and plain-language compliance standards. It helps developers, government agencies, and enterprises create AI systems that produce readable, inclusive, and compliant responses by design.

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [Python API](#python-api)
  - [Command Line](#command-line)
- [Core Capabilities](#-core-capabilities)
- [Examples](#-examples)
- [Configuration](#-configuration)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Analysis & Optimization
- **📊 Readability Analysis** - Computes Flesch-Kincaid grade level and multiple readability metrics
- **📝 Jargon Detection** - Identifies technical terms, undefined acronyms, and complex language
- **🎭 Tone Analysis** - Analyzes sentiment, formality, and passive voice usage
- **♿ Accessibility Hints** - Injects Section 508 compliance reminders (alt text, captions, structure)
- **🔧 Rule-Based Optimization** - Automatically rewrites prompts using plain language guidelines

### 🆕 Two-Stage AI Pipeline (NEW!)
- **Stage 1: INPUT Enhancement** - Automatically adds Section 508 instructions to prompts (free)
- **Stage 2: OUTPUT Validation & Fixing** - Checks and rewrites LLM outputs for compliance
- **🤖 AI-Powered Rewriting** - Uses OpenAI to intelligently improve accessibility
- **💰 Cost-Efficient** - Only ~$0.0001-0.0004 per request
- **📈 Proven Results** - +24 point score improvements, 5.6 grade level reduction

### Additional Features
- **🖥️ CLI Interface** - Easy command-line tools for analysis, optimization, and rewriting
- **🔒 Offline-First** - Works without external APIs by default (FedRAMP/Zero Trust ready)
- **🔄 Smart Fallback** - Gracefully falls back to rule-based mode when no API key available

## 📦 Installation

### Basic Installation

```bash
pip install prompt508
```

### Install with LLM Support (Optional)

```bash
pip install prompt508[llm]
```

### Install for Development

```bash
pip install prompt508[dev]
```

### Post-Installation: spaCy Model

After installation, download the required spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Quick Start

### Python API

```python
from prompt508 import AccessibilityAdvisor

# Initialize the advisor
advisor = AccessibilityAdvisor(target_grade=8.0, include_alt_text=True)

# Analyze a prompt
prompt = "Utilize the API to facilitate data transmission and implement visualization."
analysis = advisor.analyze(prompt)

print(f"Overall Score: {analysis['overall_score']}/100")
print(f"Grade Level: {analysis['readability']['flesch_kincaid_grade']}")
print(f"Issues: {len(analysis['issues'])}")

# Optimize the prompt
optimized = advisor.optimize(prompt)
print(f"Optimized: {optimized}")
```

### Command Line

```bash
# Analyze a prompt
prompt508 analyze "Your prompt text here"

# Optimize a prompt
prompt508 optimize "Utilize the API to facilitate transmission" --type images

# Generate a detailed report
prompt508 report --file prompt.txt --output report.txt
```

## 📖 Usage

### Python API

#### Basic Analysis

```python
from prompt508 import AccessibilityAdvisor

advisor = AccessibilityAdvisor(target_grade=8.0)

prompt = "Generate a comprehensive visualization of seismic telemetry data."
analysis = advisor.analyze(prompt)

# Access detailed results
print(f"Readability Grade: {analysis['readability']['flesch_kincaid_grade']}")
print(f"Jargon Count: {analysis['jargon']['jargon_count']}")
print(f"Tone: {analysis['tone']['tone_classification']}")
print(f"Passes Compliance: {analysis['passes_compliance']}")
```

#### Prompt Optimization

```python
# Basic optimization
optimized = advisor.optimize(prompt)

# Optimization with content type hints
optimized = advisor.optimize(
    prompt,
    content_type="images",  # Adds image-specific accessibility hints
    apply_rule_based_fixes=True
)

# Generate comprehensive report
report = advisor.get_report(prompt)
print(report)
```

#### Individual Analyzers

```python
from prompt508 import ReadabilityAnalyzer, JargonDetector, ToneAnalyzer

# Readability only
readability = ReadabilityAnalyzer(target_grade=8.0)
scores = readability.score_text("Your text here")

# Jargon detection only
jargon = JargonDetector()
issues = jargon.detect_jargon("Your text here")

# Tone analysis only
tone = ToneAnalyzer(target_tone="neutral")
sentiment = tone.analyze_tone("Your text here")
```

### Command Line

#### Analyze Command

```bash
# Analyze text directly
prompt508 analyze "Your prompt text"

# Analyze from file
prompt508 analyze --file prompt.txt

# Set custom grade level target
prompt508 analyze "Your text" --grade 6

# Use strict mode
prompt508 analyze "Your text" --strict

# Output as JSON
prompt508 analyze "Your text" --json
```

#### Optimize Command

```bash
# Optimize text
prompt508 optimize "Utilize the API to facilitate transmission"

# Optimize with file input/output
prompt508 optimize --file input.txt --output optimized.txt

# Specify content type for targeted hints
prompt508 optimize "Generate chart" --type images

# Skip rule-based replacements
prompt508 optimize "Your text" --no-fixes

# Strict mode with grade 6 target
prompt508 optimize "Your text" --grade 6 --strict
```

#### Report Command

```bash
# Generate detailed report
prompt508 report "Your prompt text"

# Save report to file
prompt508 report --file prompt.txt --output report.txt
```

#### Rewrite Command (NEW!)

```bash
# AI-powered rewriting (requires OPENAI_API_KEY in environment or .env)
prompt508 rewrite "Utilize sophisticated methodology to facilitate implementation"

# Rewrite from file
prompt508 rewrite --file input.txt --output rewritten.txt

# Use specific OpenAI model
prompt508 rewrite "Complex text" --model gpt-4o

# Provide API key directly
prompt508 rewrite "Text" --api-key sk-proj-...

# Skip analysis comparison
prompt508 rewrite "Text" --no-analysis

# Setup .env file for API key
echo "OPENAI_API_KEY=sk-proj-your-key-here" > .env
```

## 🔍 Core Capabilities

### 1. Readability Analysis

Computes multiple readability metrics:
- **Flesch-Kincaid Grade Level** - Target: 8th grade or below
- **Flesch Reading Ease** - Score: 60-100 (easier to read)
- **Gunning Fog Index** - Estimates years of education needed
- **SMOG Index** - Alternative readability formula
- **Word & Sentence Statistics** - Length and complexity metrics

### 2. Jargon Detection

Identifies problematic terminology:
- **Technical jargon** with plain language alternatives
- **Undefined acronyms** requiring expansion
- **Complex words** (3+ syllables)
- **Government jargon** per PlainLanguage.gov guidelines

### 3. Tone & Sentiment Analysis

Assesses communication style:
- **Sentiment polarity** - Negative, neutral, or positive
- **Subjectivity** - Objective vs. subjective language
- **Formality level** - Formal, neutral, or informal
- **Passive voice detection** - Encourages active voice

### 4. Accessibility Injection

Adds Section 508 compliance hints:
- **Alt text reminders** for images
- **Caption requirements** for multimedia
- **Document structure** guidelines (headings, lists)
- **Link text** best practices
- **Plain language** reminders

### 5. Rule-Based Optimization

Automatically improves prompts:
- Replaces jargon with plain language
- Expands common acronyms
- Simplifies complex phrases
- Injects accessibility instructions

## 💡 Examples

### Example 1: Government Documentation

```python
from prompt508 import AccessibilityAdvisor

advisor = AccessibilityAdvisor(target_grade=8.0, strict_mode=True)

# Original problematic prompt
original = """
Pursuant to Section 508 requirements, utilize the API to facilitate 
transmission of telemetry data. Subsequently, implement visualization 
methodologies to demonstrate magnitude distributions.
"""

# Analyze
analysis = advisor.analyze(original)
print(f"Issues: {analysis['issues']}")
# Output: ['Reading level too high: Grade 15.2 (target: 8.0)', 
#          'Found 4 jargon terms', ...]

# Optimize
optimized = advisor.optimize(original, content_type="images")
print(optimized)
# Output: "Following Section 508 requirements, use the API to send 
#          earthquake data. Then, create charts to show the size patterns.
#
#          [Accessibility Requirements]
#          - Include descriptive alt text for all images
#          - Describe the content and function of images..."
```

### Example 2: Enterprise AI System

```python
# Check if AI prompts meet compliance before deployment
prompts_to_check = [
    "Generate a summary of the quarterly financial report",
    "Create visualization showing customer satisfaction metrics",
    "Analyze sentiment in customer feedback data"
]

advisor = AccessibilityAdvisor(target_grade=8.0)

for prompt in prompts_to_check:
    analysis = advisor.analyze(prompt)
    if not analysis['passes_compliance']:
        print(f"❌ Prompt needs improvement: {prompt}")
        print(f"   Issues: {analysis['issues']}")
        optimized = advisor.optimize(prompt)
        print(f"   Suggested: {optimized}\n")
    else:
        print(f"✅ Prompt passes compliance: {prompt}\n")
```

### Example 3: Two-Stage AI Pipeline (NEW!)

```python
from prompt508 import AccessibilityAdvisor
from openai import OpenAI

# Your LLM function
def my_llm(prompt):
    client = OpenAI()  # Uses OPENAI_API_KEY from environment
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

advisor = AccessibilityAdvisor()

# Complete two-stage pipeline
result = advisor.ensure_compliance(
    prompt="Explain how APIs work",
    llm_function=my_llm
)

print(f"Stages used: {result['stages_used']}")
# Output: {'stage1_enhance': True, 'stage2_fix': True}

print(f"Was fixed: {result['was_fixed']}")
# Output: True (if Stage 2 fixing was needed)

print(f"Final score: {result['compliance_score']}/100")
# Output: 85.3/100

print(f"Final output: {result['final_output']}")
# Output: Clean, accessible text meeting Section 508 standards
```

**Manual stage-by-stage control:**

```python
# Stage 1: Enhance prompt with Section 508 instructions
enhanced_prompt = advisor.enhance_prompt_for_508("Explain quantum computing")

# Send to your LLM
llm_output = my_llm(enhanced_prompt)

# Stage 2: Validate the output
validation = advisor.validate_output(llm_output)
print(f"Score: {validation['score']}/100")
print(f"Needs fixing: {validation['needs_fixing']}")

# Stage 2: Fix if needed
if validation['needs_fixing']:
    fixed = advisor.fix_output(llm_output)
    final_text = fixed['rewritten']
    print(f"Cost: ${fixed['cost_usd']:.4f}")
else:
    final_text = llm_output

print(f"Final: {final_text}")
```

### Example 4: AI-Powered Rewriting

```python
# Rewrite any text for accessibility (requires OpenAI API key)
advisor = AccessibilityAdvisor()

complex_text = "Utilize sophisticated methodology to facilitate implementation"

result = advisor.rewrite_prompt(complex_text)

if result['mode'] == 'ai':
    print(f"Rewritten: {result['rewritten']}")
    # Output: "Use this simple method to help with implementation"
    
    print(f"Improvements:")
    print(f"  Score: {result['improvements']['overall_score']['before']} → "
          f"{result['improvements']['overall_score']['after']}")
    print(f"  Grade: {result['improvements']['readability_grade']['before']} → "
          f"{result['improvements']['readability_grade']['after']}")
    print(f"  Cost: ${result['cost_usd']:.4f}")
```

### Example 5: Individual Module Usage

```python
from prompt508 import score_text, detect_jargon, analyze_tone

text = "Implement comprehensive accessibility features"

# Quick readability check
readability = score_text(text)
print(f"Grade Level: {readability['flesch_kincaid_grade']}")

# Quick jargon check
jargon = detect_jargon(text)
print(f"Jargon terms: {jargon['jargon_words']}")
print(f"Suggestions: {jargon['suggestions']}")

# Quick tone check
tone = analyze_tone(text)
print(f"Sentiment: {tone['tone_classification']}")
print(f"Formality: {tone['formality_score']}")
```

### Example 6: Comparison Demo

**See the VALUE_PROPOSITION.md file for a complete comparison showing:**
- **WITHOUT prompt508**: Score 56.7/100, Grade 13.8, 17 jargon terms
- **WITH prompt508**: Score 80.7/100, Grade 8.2, 6 jargon terms
- **Improvement**: +24 points, -5.6 grades, -11 jargon terms
- **Cost**: Only $0.0004 per request

Run the demo:
```bash
python demo_comparison.py
```

## ⚙️ Configuration

### AccessibilityAdvisor Parameters

```python
advisor = AccessibilityAdvisor(
    target_grade=8.0,              # Target reading grade level (default: 8.0)
    include_alt_text=True,         # Include alt text reminders
    include_captions=True,          # Include caption reminders
    include_structure=True,         # Include structure reminders
    strict_mode=False,             # Use stricter analysis
    spacy_model="en_core_web_sm"   # spaCy model for NLP
)
```

### Content Types

When optimizing, specify content type for targeted hints:
- `"images"` - Image alt text and descriptions
- `"multimedia"` - Video captions and transcripts
- `"documents"` - Document structure and headings
- `"links"` - Link text best practices
- `"forms"` - Form accessibility
- `None` - General accessibility hints

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/hungmanhdo/prompt508.git
cd prompt508

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=prompt508 --cov-report=html

# Run specific test file
pytest tests/test_readability.py -v
```

### Code Quality

```bash
# Format code with black
black src/

# Check code style with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PlainLanguage.gov** - Federal plain language guidelines
- **Section 508** - U.S. accessibility standards (29 U.S.C. § 794d)
- **WCAG 2.1** - Web Content Accessibility Guidelines
- **textstat** - Readability calculations
- **spaCy** - Natural language processing
- **TextBlob** - Sentiment analysis

## 📚 Resources

- [Section 508 Standards](https://www.section508.gov/)
- [PlainLanguage.gov](https://www.plainlanguage.gov/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Federal Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/hungmanhdo/prompt508/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hungmanhdo/prompt508/discussions)

---

Made with ❤️ for accessibility and inclusion
