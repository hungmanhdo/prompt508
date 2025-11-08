"""
Example usage of prompt508's AI-powered rewriter.

This example shows how to use the AI rewriter to automatically improve
prompts for Section 508 compliance and plain language.
"""

from prompt508 import PromptAdvisor

# Example text with accessibility issues
complex_text = """
Utilize this sophisticated methodology to facilitate the implementation of your
comprehensive solution. The API will enable you to instantiate the repository
and iterate through the parameters. Pursuant to the documentation, you should
authenticate with valid credentials prior to commencing the workflow.
"""


def example_ai_rewriting():
    """Example of AI-powered rewriting with OpenAI."""
    print("=" * 70)
    print("AI-POWERED REWRITING EXAMPLE")
    print("=" * 70)

    # Initialize advisor
    advisor = PromptAdvisor()

    # Rewrite with AI (requires OPENAI_API_KEY in .env or environment)
    print("\nOriginal text:")
    print(complex_text)

    result = advisor.rewrite_prompt(complex_text)

    if result["mode"] == "ai":
        print("\n" + "=" * 70)
        print("AI REWRITING SUCCESSFUL")
        print("=" * 70)
        print(f"\nModel used: {result['model']}")
        print(f"Cost: ${result['cost_usd']:.4f}")

        print("\nRewritten text:")
        print(result["rewritten"])

        # Show improvements
        if "improvements" in result:
            print("\n" + "=" * 70)
            print("IMPROVEMENTS")
            print("=" * 70)

            improvements = result["improvements"]
            print(
                f"\nOverall Score: {improvements['overall_score']['before']}/100 "
                f"→ {improvements['overall_score']['after']}/100 "
                f"({improvements['overall_score']['change']:+.1f})"
            )

            print(
                f"Reading Grade: {improvements['readability_grade']['before']} "
                f"→ {improvements['readability_grade']['after']} "
                f"({improvements['readability_grade']['change']:+.1f})"
            )

            print(
                f"Jargon Terms: {improvements['jargon_count']['before']} "
                f"→ {improvements['jargon_count']['after']} "
                f"({improvements['jargon_count']['change']:+d})"
            )

            if improvements["now_passes_compliance"]:
                print("\n✓ Now passes Section 508 compliance!")

    else:
        # Rule-based fallback
        print("\n" + "=" * 70)
        print("RULE-BASED SUGGESTIONS (No API key found)")
        print("=" * 70)
        print(f"\n{result.get('message', '')}")

        if result.get("suggestions"):
            print("\nSuggestions:")
            for suggestion in result["suggestions"][:10]:
                print(f"  • {suggestion['original']} → {suggestion['replacement']}")


def example_custom_instructions():
    """Example with custom instructions for the AI."""
    print("\n" + "=" * 70)
    print("CUSTOM INSTRUCTIONS EXAMPLE")
    print("=" * 70)

    advisor = PromptAdvisor()

    text = "Generate a comprehensive report on the fiscal year's performance metrics."

    # Add custom instructions for specific context
    custom_instructions = """
    This is for a general audience report.
    - Use very simple language (6th grade level)
    - Explain all financial terms
    - Use bullet points where possible
    """

    result = advisor.rewrite_prompt(text, custom_instructions=custom_instructions)

    if result["mode"] == "ai":
        print("\nOriginal:")
        print(text)
        print("\nRewritten with custom instructions:")
        print(result["rewritten"])
    else:
        print(f"\n{result.get('message', '')}")


def example_comparison():
    """Compare AI rewriting with rule-based optimization."""
    print("\n" + "=" * 70)
    print("COMPARISON: AI vs RULE-BASED")
    print("=" * 70)

    advisor = PromptAdvisor()

    text = "Utilize the API to facilitate data transmission."

    # Rule-based optimization
    print("\n1. Rule-based optimization:")
    optimized = advisor.optimize(text)
    print(f"   {optimized}")

    # AI rewriting
    print("\n2. AI rewriting:")
    result = advisor.rewrite_prompt(text, analyze_improvement=False)
    if result["mode"] == "ai":
        print(f"   {result['rewritten']}")
    else:
        print(f"   (No API key - would use AI rewriting)")


if __name__ == "__main__":
    # Run examples
    example_ai_rewriting()

    # Uncomment to run other examples:
    # example_custom_instructions()
    # example_comparison()

    print("\n" + "=" * 70)
    print("SETUP INSTRUCTIONS")
    print("=" * 70)
    print(
        """
To use AI-powered rewriting:

1. Get an OpenAI API key from: https://platform.openai.com/api-keys

2. Create a .env file in your project:
   echo "OPENAI_API_KEY=sk-proj-your-key-here" > .env

3. Run this example:
   python ai_rewriter_example.py

4. Or use in your code:
   from prompt508 import PromptAdvisor
   advisor = PromptAdvisor()
   result = advisor.rewrite_prompt("Your text here")
"""
    )
