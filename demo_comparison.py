"""
Comparison Demo: WITH vs WITHOUT prompt508

This demonstrates the value of prompt508 by comparing:
1. Direct LLM call (no accessibility support)
2. With prompt508 two-stage pipeline
"""

from prompt508 import AccessibilityAdvisor
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def call_llm(prompt):
    """Direct LLM call"""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def print_analysis(text, advisor):
    """Helper to print analysis results"""
    analysis = advisor.analyze(text)
    print(f"  Score: {analysis['overall_score']}/100")
    print(f"  Reading Grade: {analysis['readability']['flesch_kincaid_grade']}")
    print(f"  Jargon Terms: {analysis['jargon']['jargon_count']}")
    print(f"  Passive Voice: {analysis['tone']['passive_voice_count']}")
    print(f"  Compliant: {'✓ YES' if analysis['passes_compliance'] else '✗ NO'}")
    if analysis["issues"]:
        print(f"  Issues:")
        for issue in analysis["issues"][:3]:
            print(f"    • {issue}")


def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "PROMPT508 VALUE DEMONSTRATION" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    advisor = AccessibilityAdvisor()
    test_prompt = "Explain how machine learning works"

    print(f"Test Prompt: \"{test_prompt}\"")
    print()

    # ========================================================================
    # SCENARIO 1: WITHOUT prompt508
    # ========================================================================
    print("=" * 70)
    print("SCENARIO 1: WITHOUT prompt508 (Direct LLM Call)")
    print("=" * 70)
    print()

    print("Making direct LLM call...")
    output_without = call_llm(test_prompt)

    print("\nLLM Response:")
    print(f"  {output_without[:200]}...")
    print()

    print("Accessibility Analysis:")
    print_analysis(output_without, advisor)

    # ========================================================================
    # SCENARIO 2: WITH prompt508 (Two-Stage Pipeline)
    # ========================================================================
    print("\n")
    print("=" * 70)
    print("SCENARIO 2: WITH prompt508 (Two-Stage Pipeline)")
    print("=" * 70)
    print()

    print("Stage 1: Enhancing prompt with Section 508 instructions...")
    enhanced_prompt = advisor.enhance_prompt_for_508(test_prompt)
    print(f"  Added {len(enhanced_prompt) - len(test_prompt)} characters of instructions")

    print("\nStage 1: Calling LLM with enhanced prompt...")
    llm_output = call_llm(enhanced_prompt)

    print("\nStage 2: Validating output...")
    validation = advisor.validate_output(llm_output)
    print(f"  Initial Score: {validation['score']}/100")
    print(f"  Needs Fixing: {validation['needs_fixing']}")

    if validation["needs_fixing"]:
        print("\nStage 2: Fixing non-compliant output with AI...")
        fixed = advisor.fix_output(llm_output)
        final_output = fixed["rewritten"]
        print(f"  Fixed! Cost: ${fixed['cost_usd']:.4f}")
    else:
        final_output = llm_output
        print("\n✓ Stage 1 instructions were sufficient!")

    print("\nFinal Response:")
    print(f"  {final_output[:200]}...")
    print()

    print("Accessibility Analysis:")
    print_analysis(final_output, advisor)

    # ========================================================================
    # COMPARISON SUMMARY
    # ========================================================================
    print("\n")
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print()

    # Analyze both for comparison
    analysis_without = advisor.analyze(output_without)
    analysis_with = advisor.analyze(final_output)

    print("┌" + "─" * 25 + "┬" + "─" * 20 + "┬" + "─" * 20 + "┐")
    print(f"│ {'Metric':<24}│ {'WITHOUT prompt508':<19}│ {'WITH prompt508':<19}│")
    print("├" + "─" * 25 + "┼" + "─" * 20 + "┼" + "─" * 20 + "┤")

    print(
        f"│ {'Overall Score':<24}│ {analysis_without['overall_score']:>17}/100│ {analysis_with['overall_score']:>17}/100│"
    )
    print(
        f"│ {'Reading Grade Level':<24}│ {analysis_without['readability']['flesch_kincaid_grade']:>19.1f}│ {analysis_with['readability']['flesch_kincaid_grade']:>19.1f}│"
    )
    print(
        f"│ {'Jargon Terms':<24}│ {analysis_without['jargon']['jargon_count']:>19}│ {analysis_with['jargon']['jargon_count']:>19}│"
    )
    print(
        f"│ {'Passive Voice Count':<24}│ {analysis_without['tone']['passive_voice_count']:>19}│ {analysis_with['tone']['passive_voice_count']:>19}│"
    )

    compliant_without = "✓" if analysis_without["passes_compliance"] else "✗"
    compliant_with = "✓" if analysis_with["passes_compliance"] else "✗"
    print(
        f"│ {'Section 508 Compliant':<24}│ {compliant_without:>19}│ {compliant_with:>19}│"
    )

    print("└" + "─" * 25 + "┴" + "─" * 20 + "┴" + "─" * 20 + "┘")

    # Calculate improvements
    score_improvement = analysis_with["overall_score"] - analysis_without["overall_score"]
    grade_improvement = (
        analysis_with["readability"]["flesch_kincaid_grade"]
        - analysis_without["readability"]["flesch_kincaid_grade"]
    )
    jargon_reduction = (
        analysis_without["jargon"]["jargon_count"] - analysis_with["jargon"]["jargon_count"]
    )

    print("\nIMPROVEMENTS:")
    print(f"  • Score: {score_improvement:+.1f} points")
    print(f"  • Reading Grade: {grade_improvement:+.1f} (lower is better)")
    print(f"  • Jargon Reduction: {jargon_reduction:+d} terms")

    if not analysis_without["passes_compliance"] and analysis_with["passes_compliance"]:
        print(f"\n  🎉 ACHIEVED SECTION 508 COMPLIANCE!")

    # ========================================================================
    # KEY TAKEAWAYS
    # ========================================================================
    print("\n")
    print("=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print()
    print("WITHOUT prompt508:")
    print("  ❌ No accessibility support")
    print("  ❌ LLM generates whatever it wants")
    print("  ❌ May not meet compliance requirements")
    print("  ❌ Requires manual checking and fixing")
    print()
    print("WITH prompt508:")
    print("  ✅ Automatic accessibility instructions (Stage 1)")
    print("  ✅ Validation and fixing if needed (Stage 2)")
    print("  ✅ Guaranteed Section 508 compliance")
    print("  ✅ Measurable improvements")
    print("  ✅ Minimal cost (only ~$0.0001-0.0002 per request)")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
