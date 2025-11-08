
# Prompt508 – Accessibility & Plain-Language Optimizer for AI Prompts

## 📘 Project Overview
Prompt508 is an open-source Python library that analyzes and optimizes AI prompts to ensure they meet
U.S. Section 508 accessibility and plain-language compliance. It helps developers, government agencies,
and enterprises create AI systems that produce readable, inclusive, and compliant responses by design.

## 🧭 Goals
- Analyze and score readability (grade level, complexity)
- Detect jargon and undefined acronyms
- Analyze tone and sentiment
- Inject accessibility & plain-language hints into prompts
- Rewrite prompts deterministically (rule-based)
- Optionally rewrite prompts using LLM for enhanced naturalness
- Provide CLI and Python API
- Work offline by default (FedRAMP/Zero Trust ready)

## 🧩 Core Functionalities
1. **Readability Analyzer** – Computes Flesch-Kincaid grade level, word/sentence stats.
2. **Jargon Detector** – Uses spaCy to detect uncommon or undefined terms.
3. **Tone Analyzer** – Uses TextBlob to detect sentiment and neutrality.
4. **Accessibility Injector** – Adds reminders (alt text, captions, structure hints).
5. **AccessibilityAdvisor** – Orchestrates all analyses and outputs optimized prompts.
6. **CLI Interface** – Commands: `prompt508 analyze` and `prompt508 optimize`.
7. **LLM-Assisted Mode (Optional)** – Uses Azure OpenAI or Bedrock via provider_config.yaml.

## 🧱 Architecture

prompt508/
│
├── __init__.py
├── core/
│   ├── advisor.py           # main class combining all analyzers
│   ├── readability.py       # readability scoring (textstat)
│   ├── jargon.py            # jargon detection (spaCy)
│   ├── tone.py              # tone & sentiment analysis (TextBlob)
│   ├── accessibility.py     # hint injection
│   ├── utils.py             # shared utilities
│   └── rules/
│       ├── gov_plain_language.json
│       ├── section508.json
│       └── replacements.json
│
├── cli.py                   # CLI via Typer
├── examples/
│   ├── optimize_prompt.py
│   └── integrate_langchain.py
├── tests/
│   ├── test_advisor.py
│   ├── test_readability.py
│   ├── test_jargon.py
│   └── test_cli.py
├── pyproject.toml
├── README.md
└── LICENSE

## ⚙️ Dependencies
- textstat
- spacy
- textblob
- typer
Optional (for LLM mode): openai

## 🧰 Example Usage

```python
from prompt508 import AccessibilityAdvisor

advisor = AccessibilityAdvisor(target_grade=8, include_alt_text=True)

prompt = "Summarize the seismic telemetry datasets retrieved from the USGS API."
optimized = advisor.optimize(prompt)

print(optimized)
```

### CLI Example
```
$ prompt508 analyze "Explain the earthquake telemetry process"
$ prompt508 optimize "Generate a chart of earthquake data"
```

## 🧠 Architecture Flow
User Prompt → Analyzer Modules → Rule-based Optimizer → (Optional) LLM Rewriter → Output

## 🧱 Deliverables
- Full Python package with rule-based logic
- CLI interface
- Unit tests
- Example scripts
- MIT license and documentation

## 🧰 Initial Development Plan (for Cline)
1. Scaffold folder structure and pyproject.toml
2. Implement `score_text()` in readability.py
3. Implement `detect_jargon()` in jargon.py
4. Implement `analyze_tone()` in tone.py
5. Implement `AccessibilityAdvisor.optimize()` (rule-based)
6. Implement CLI commands
7. Add tests and examples

## 🧠 Optional Extensions
- `rewrite_with_llm()` method (uses provider_config.yaml)
- CMS (Drupal/WordPress) ingestion pre-check
- Continuous “Prompt Linter” CI/CD plugin

## 📄 License
MIT

---
This file contains all project specifications for AI pair-programming tools like Cline to understand
the entire scope and start implementing the `prompt508` library.
