# Contributing to prompt508

Thank you for your interest in contributing to prompt508! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Detailed steps to reproduce the bug
- Expected behavior vs actual behavior
- Your environment (OS, Python version, prompt508 version)
- Relevant code samples or error messages

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- The problem it solves
- Example use cases
- Any relevant implementation ideas

### Pull Requests

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Update documentation** if needed
5. **Ensure all tests pass** locally
6. **Submit a pull request** with a clear description

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/prompt508.git
cd prompt508

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Download required spaCy model
python -m spacy download en_core_web_sm
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=prompt508 --cov-report=html

# Run specific test file
pytest tests/test_readability.py -v
```

## 📝 Code Style

We follow PEP 8 guidelines with some modifications:

```bash
# Format code with black
black src/

# Check with flake8
flake8 src/ --max-line-length=100
```

### Code Standards

- **Line length**: 100 characters maximum
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Include type hints where appropriate
- **Comments**: Write clear, concise comments for complex logic

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions/classes
- Include usage examples for new features
- Update CHANGELOG.md (if we add one)

## 🏗️ Project Structure

```
prompt508/
├── src/prompt508/           # Main package
│   ├── core/               # Core analysis modules
│   │   ├── rules/          # JSON rule files
│   │   ├── advisor.py      # Main orchestrator
│   │   ├── readability.py  # Readability analysis
│   │   ├── jargon.py       # Jargon detection
│   │   ├── tone.py         # Tone analysis
│   │   └── accessibility.py # Accessibility hints
│   ├── examples/           # Usage examples
│   └── cli.py             # CLI interface
├── tests/                  # Test suite
└── docs/                   # Documentation (if added)
```

## ✅ Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated as needed
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes
- [ ] No merge conflicts with main branch

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

- **Additional rule files** - More jargon/plain language mappings
- **New analyzers** - Additional accessibility checks
- **Language support** - Non-English language support
- **Performance improvements** - Optimization of analysis speed
- **Documentation** - Tutorials, guides, examples
- **Tests** - Expanding test coverage
- **Bug fixes** - Any identified issues

## 📧 Questions?

If you have questions about contributing, feel free to:
- Open a discussion on GitHub Discussions
- Comment on relevant issues
- Reach out to the maintainers

## 📜 License

By contributing to prompt508, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make AI more accessible! 🎉
