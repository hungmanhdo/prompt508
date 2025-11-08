"""
Main AccessibilityAdvisor class for prompt508.
Orchestrates all analyzers and provides the primary API for prompt optimization.
"""

from typing import Dict, List, Optional, Any
from .readability import ReadabilityAnalyzer
from .jargon import JargonDetector
from .tone import ToneAnalyzer
from .accessibility import AccessibilityInjector
from .utils import load_json_rules, apply_replacements, clean_text


class AccessibilityAdvisor:
    """
    Main advisor class that orchestrates all accessibility and plain language analysis.

    Combines readability scoring, jargon detection, tone analysis, and accessibility
    hint injection to provide comprehensive prompt optimization for Section 508 compliance.
    """

    def __init__(
        self,
        target_grade: float = 8.0,
        include_alt_text: bool = True,
        include_captions: bool = True,
        include_structure: bool = True,
        strict_mode: bool = False,
        spacy_model: str = "en_core_web_sm",
    ):
        """
        Initialize the AccessibilityAdvisor with all sub-analyzers.

        Args:
            target_grade: Target reading grade level (default: 8.0 for plain language)
            include_alt_text: Include alt text reminders in optimization
            include_captions: Include caption reminders
            include_structure: Include structure reminders
            strict_mode: Use stricter analysis and more detailed instructions
            spacy_model: spaCy model to use for NLP (default: en_core_web_sm)
        """
        self.target_grade = target_grade
        self.strict_mode = strict_mode

        # Initialize all analyzers
        self.readability_analyzer = ReadabilityAnalyzer(target_grade=target_grade)
        self.jargon_detector = JargonDetector(model_name=spacy_model)
        self.tone_analyzer = ToneAnalyzer(target_tone="neutral")
        self.accessibility_injector = AccessibilityInjector(
            include_alt_text=include_alt_text,
            include_captions=include_captions,
            include_structure=include_structure,
            strict_mode=strict_mode,
        )

        # Load rules
        self._load_rules()

    def _load_rules(self) -> None:
        """Load all rule files."""
        try:
            self.plain_language_rules = load_json_rules("gov_plain_language.json")
            self.section508_rules = load_json_rules("section508.json")
            self.replacement_rules = load_json_rules("replacements.json")
        except Exception as e:
            # Set empty defaults if rules can't be loaded
            self.plain_language_rules = {}
            self.section508_rules = {}
            self.replacement_rules = {}

    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Perform comprehensive accessibility analysis on a prompt.

        Args:
            prompt: Input prompt to analyze

        Returns:
            Dictionary containing:
                - readability: Readability analysis results
                - jargon: Jargon detection results
                - tone: Tone analysis results
                - overall_score: Overall compliance score (0-100)
                - passes_compliance: Whether prompt meets all targets
                - issues: List of identified issues
                - recommendations: Consolidated recommendations
        """
        cleaned_prompt = clean_text(prompt)

        if not cleaned_prompt:
            return self._empty_analysis()

        # Run all analyzers
        readability_result = self.readability_analyzer.score_text(cleaned_prompt)
        jargon_result = self.jargon_detector.detect_jargon(cleaned_prompt)
        tone_result = self.tone_analyzer.analyze_tone(cleaned_prompt)

        # Calculate overall compliance
        overall_score = self._calculate_overall_score(
            readability_result, jargon_result, tone_result
        )

        # Determine if passes compliance
        passes = self._check_compliance(readability_result, jargon_result, tone_result)

        # Identify issues
        issues = self._identify_issues(readability_result, jargon_result, tone_result)

        # Consolidate recommendations
        recommendations = self._consolidate_recommendations(
            readability_result, jargon_result, tone_result
        )

        return {
            "readability": readability_result,
            "jargon": jargon_result,
            "tone": tone_result,
            "overall_score": overall_score,
            "passes_compliance": passes,
            "issues": issues,
            "recommendations": recommendations,
        }

    def optimize(
        self, prompt: str, content_type: Optional[str] = None, apply_rule_based_fixes: bool = True
    ) -> str:
        """
        Optimize a prompt for accessibility and plain language compliance.

        This applies rule-based transformations:
        1. Replace jargon with plain language
        2. Expand undefined acronyms
        3. Inject accessibility hints

        Args:
            prompt: Input prompt to optimize
            content_type: Expected content type for targeted accessibility hints
            apply_rule_based_fixes: Whether to apply rule-based text replacements

        Returns:
            Optimized prompt with accessibility improvements
        """
        optimized = clean_text(prompt)

        if not optimized:
            return prompt

        # Step 1: Apply plain language replacements
        if apply_rule_based_fixes:
            replacements = self.plain_language_rules.get("replacements", {})
            optimized = apply_replacements(optimized, replacements, case_sensitive=False)

            # Apply technical simplifications
            tech_replacements = self.replacement_rules.get("technical_simplifications", {})
            optimized = apply_replacements(optimized, tech_replacements, case_sensitive=False)

        # Step 2: Inject accessibility hints
        optimized = self.accessibility_injector.inject_hints(optimized, content_type)

        return optimized

    def rewrite_with_llm(
        self,
        prompt: str,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Rewrite a prompt using LLM for enhanced naturalness (optional feature).

        Note: This requires the 'openai' package and API credentials.

        Args:
            prompt: Input prompt to rewrite
            provider: LLM provider ("openai", "azure", "bedrock")
            model: Model to use
            api_key: API key (if not in environment)
            **kwargs: Additional provider-specific arguments

        Returns:
            LLM-rewritten prompt optimized for accessibility

        Raises:
            ImportError: If openai package not installed
            ValueError: If provider not supported
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "LLM rewriting requires the 'openai' package. "
                "Install with: pip install 'prompt508[llm]'"
            )

        # Analyze original prompt to guide rewriting
        analysis = self.analyze(prompt)

        # Build rewriting instructions based on analysis
        instructions = self._build_llm_instructions(analysis)

        # Create rewriting prompt
        system_prompt = """You are an accessibility and plain language expert specializing 
in Section 508 compliance. Rewrite the user's prompt to meet these requirements while 
preserving the original intent and functionality."""

        user_prompt = f"""Original Prompt:
{prompt}

Requirements:
{instructions}

Please rewrite this prompt to meet these requirements while maintaining its purpose and effectiveness."""

        # Call LLM (simplified - real implementation would handle different providers)
        if api_key:
            openai.api_key = api_key

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                **kwargs,
            )
            rewritten = response.choices[0].message.content
            return rewritten
        except Exception as e:
            # Fall back to rule-based optimization if LLM fails
            return self.optimize(prompt)

    def _calculate_overall_score(self, readability: Dict, jargon: Dict, tone: Dict) -> float:
        """
        Calculate overall compliance score (0-100).

        Args:
            readability: Readability analysis results
            jargon: Jargon detection results
            tone: Tone analysis results

        Returns:
            Overall score from 0-100
        """
        score = 100.0

        # Readability penalty (max -40 points)
        grade_diff = max(0, readability["flesch_kincaid_grade"] - self.target_grade)
        readability_penalty = min(40, grade_diff * 10)
        score -= readability_penalty

        # Jargon penalty (max -30 points)
        jargon_penalty = min(30, jargon["jargon_ratio"])
        score -= jargon_penalty

        # Tone penalty (max -15 points)
        if not tone["is_neutral"]:
            score -= 10
        if tone["is_subjective"]:
            score -= 5

        # Passive voice penalty (max -15 points)
        passive_penalty = min(15, tone["passive_voice_count"] * 3)
        score -= passive_penalty

        return max(0, round(score, 1))

    def _check_compliance(self, readability: Dict, jargon: Dict, tone: Dict) -> bool:
        """Check if prompt meets all compliance targets."""
        return readability["meets_target"] and not jargon["has_issues"] and tone["meets_target"]

    def _identify_issues(self, readability: Dict, jargon: Dict, tone: Dict) -> List[str]:
        """Identify specific compliance issues."""
        issues = []

        if not readability["meets_target"]:
            issues.append(
                f"Reading level too high: Grade {readability['flesch_kincaid_grade']} "
                f"(target: {self.target_grade})"
            )

        if jargon["jargon_count"] > 0:
            issues.append(f"Found {jargon['jargon_count']} jargon terms")

        if jargon["undefined_acronyms"]:
            issues.append(f"{len(jargon['undefined_acronyms'])} undefined acronyms")

        if not tone["is_neutral"]:
            issues.append(f"Tone is {tone['tone_classification']} (should be neutral)")

        if tone["is_subjective"]:
            issues.append("Text is too subjective")

        if tone["passive_voice_count"] > 0:
            issues.append(f"{tone['passive_voice_count']} passive voice instances")

        return issues

    def _consolidate_recommendations(
        self, readability: Dict, jargon: Dict, tone: Dict
    ) -> List[str]:
        """Consolidate recommendations from all analyzers."""
        all_recommendations = []

        # Add top recommendations from each analyzer
        all_recommendations.extend(readability["recommendations"][:2])

        if jargon["has_issues"]:
            all_recommendations.append(
                f"Replace jargon terms with plain language. "
                f"See suggestions: {list(jargon['suggestions'].keys())[:3]}"
            )

        all_recommendations.extend(tone["recommendations"][:2])

        return all_recommendations

    def _build_llm_instructions(self, analysis: Dict) -> str:
        """Build LLM rewriting instructions based on analysis."""
        instructions = []

        instructions.append(
            f"- Target reading level: Grade {self.target_grade} (use simple vocabulary)"
        )

        if analysis["jargon"]["jargon_count"] > 0:
            instructions.append("- Replace technical jargon with plain language")

        if analysis["tone"]["passive_voice_count"] > 0:
            instructions.append("- Use active voice")

        instructions.append("- Include accessibility reminders (alt text, captions, structure)")
        instructions.append("- Maintain neutral, professional tone")

        return "\n".join(instructions)

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis for empty input."""
        return {
            "readability": {},
            "jargon": {},
            "tone": {},
            "overall_score": 0,
            "passes_compliance": False,
            "issues": ["No text provided"],
            "recommendations": ["Provide text to analyze"],
        }

    def get_report(self, prompt: str) -> str:
        """
        Generate a comprehensive accessibility report for a prompt.

        Args:
            prompt: Input prompt

        Returns:
            Formatted report string
        """
        analysis = self.analyze(prompt)

        report = f"""
{'='*70}
PROMPT508 ACCESSIBILITY ANALYSIS REPORT
{'='*70}

Overall Score: {analysis['overall_score']}/100
Compliance Status: {'✓ PASSES' if analysis['passes_compliance'] else '✗ NEEDS IMPROVEMENT'}

{'-'*70}
READABILITY
{'-'*70}
{self.readability_analyzer.get_summary(prompt)}

{'-'*70}
JARGON & TERMINOLOGY
{'-'*70}
{self.jargon_detector.get_summary(prompt)}

{'-'*70}
TONE & SENTIMENT
{'-'*70}
{self.tone_analyzer.get_summary(prompt)}

{'-'*70}
IDENTIFIED ISSUES
{'-'*70}
"""
        if analysis["issues"]:
            for i, issue in enumerate(analysis["issues"], 1):
                report += f"{i}. {issue}\n"
        else:
            report += "No issues found. Prompt meets all compliance targets.\n"

        report += f"""
{'-'*70}
RECOMMENDATIONS
{'-'*70}
"""
        for i, rec in enumerate(analysis["recommendations"], 1):
            report += f"{i}. {rec}\n"

        report += f"\n{'='*70}\n"

        return report
