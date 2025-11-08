"""
Example of the Two-Stage Accessibility Pipeline

This demonstrates prompt508's complete approach:
Stage 1: Enhance input prompt with Section 508 instructions
Stage 2: Validate and fix output if needed
"""

from prompt508 import AccessibilityAdvisor
from openai import OpenAI


def simple_llm_call(prompt):
    """
    Simple LLM function for testing.
    Replace with your actual LLM integration.
    """
    client = OpenAI()  # Uses OPENAI_API_KEY from env
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def example_complete_pipeline():
    """Example: Complete two-stage pipeline using ensure_compliance()"""
    print("=" * 70)
    print("COMPLETE TWO-STAGE PIPELINE")
    print("=" * 70)

    advisor = AccessibilityAdvisor()

    user_prompt = "Explain how APIs work"

    # Run complete pipeline
    result = advisor.ensure_compliance(prompt=user_prompt, llm_function=simple_llm_call)

    print(f"\nOriginal Prompt:")
    print(f"  {user_prompt}")

    print(f"\nEnhanced Prompt (Stage 1):")
    print(f"  {result['enhanced_prompt'][:100]}...")

    print(f"\nLLM Output:")
    print(f"  {result['llm_output'][:100]}...")

    print(f"\nValidation:")
    print(f"  Score: {result['validation']['score']}/100")
    print(f"  Passes: {result['validation']['passes_compliance']}")

    print(f"\nStages Used:")
    print(f"  Stage 1 (Enhance): {result['stages_used']['stage1_enhance']}")
    print(f"  Stage 2 (Fix): {result['stages_used']['stage2_fix']}")

    print(f"\nFinal Output:")
    print(f"  {result['final_output'][:200]}...")

    if result["was_fixed"]:
        print(f"\n⚠️  Output needed Stage 2 fixing")
        print(f"  Cost: ${result.get('cost_usd', 0):.4f}")
    else:
        print(f"\n✓ Stage 1 instructions were sufficient!")


def example_stage_by_stage():
    """Example: Manual control of each stage"""
    print("\n" + "=" * 70)
    print("MANUAL STAGE-BY-STAGE CONTROL")
    print("=" * 70)

    advisor = AccessibilityAdvisor()

    # STAGE 1: Enhance prompt
    original_prompt = "Explain quantum computing"
    enhanced_prompt = advisor.enhance_prompt_for_508(original_prompt, strict=True)

    print(f"\nStage 1 - Enhanced Prompt:")
    print(enhanced_prompt)

    # Send to LLM
    llm_output = simple_llm_call(enhanced_prompt)
    print(f"\nLLM Output received ({len(llm_output)} characters)")

    # STAGE 2: Validate
    validation = advisor.validate_output(llm_output)

    print(f"\nStage 2 - Validation:")
    print(f"  Score: {validation['score']}/100")
    print(f"  Compliant: {validation['passes_compliance']}")
    print(f"  Needs Fixing: {validation['needs_fixing']}")

    if validation["needs_fixing"]:
        print(f"\n  Issues found:")
        for issue in validation["issues"]:
            print(f"    • {issue}")

        # Fix the output
        fixed = advisor.fix_output(llm_output)

        if fixed["mode"] == "ai":
            print(f"\n  Fixed with AI:")
            print(f"    Before: {llm_output[:80]}...")
            print(f"    After: {fixed['rewritten'][:80]}...")
            print(f"    Cost: ${fixed['cost_usd']:.4f}")
    else:
        print(f"\n✓ Output already compliant!")


def example_individual_methods():
    """Example: Using individual Stage 1 and Stage 2 methods"""
    print("\n" + "=" * 70)
    print("INDIVIDUAL METHOD USAGE")
    print("=" * 70)

    advisor = AccessibilityAdvisor()

    # Stage 1 only - for testing prompt enhancement
    print("\nStage 1 - Enhance Prompt:")
    basic_prompt = "Create a tutorial"
    enhanced = advisor.enhance_prompt_for_508(basic_prompt)
    print(f"  Original: {basic_prompt}")
    print(f"  Enhanced: {enhanced[:100]}...")

    # Stage 2 only - for validating existing text
    print("\nStage 2 - Validate Text:")
    complex_text = "Utilize sophisticated methodologies to facilitate implementation"
    validation = advisor.validate_output(complex_text)
    print(f"  Text: {complex_text}")
    print(f"  Score: {validation['score']}/100")
    print(f"  Compliant: {validation['passes_compliance']}")


def example_comparison():
    """Example: Compare with/without accessibility instructions"""
    print("\n" + "=" * 70)
    print("COMPARISON: WITH vs WITHOUT STAGE 1")
    print("=" * 70)

    advisor = AccessibilityAdvisor()

    prompt = "Explain machine learning"

    # WITHOUT Stage 1
    print("\nWITHOUT Stage 1 instructions:")
    output_without = simple_llm_call(prompt)
    validation_without = advisor.validate_output(output_without)
    print(f"  Score: {validation_without['score']}/100")
    print(f"  Grade: {validation_without['readability_grade']}")
    print(f"  Jargon: {validation_without['jargon_count']} terms")

    # WITH Stage 1
    print("\nWITH Stage 1 instructions:")
    enhanced_prompt = advisor.enhance_prompt_for_508(prompt)
    output_with = simple_llm_call(enhanced_prompt)
    validation_with = advisor.validate_output(output_with)
    print(f"  Score: {validation_with['score']}/100")
    print(f"  Grade: {validation_with['readability_grade']}")
    print(f"  Jargon: {validation_with['jargon_count']} terms")

    print(f"\nImprovement from Stage 1:")
    print(f"  Score: +{validation_with['score'] - validation_without['score']}")
    print(
        f"  Grade: {validation_with['readability_grade'] - validation_without['readability_grade']:.1f}"
    )


def example_custom_llm():
    """Example: Using with different LLM providers"""
    print("\n" + "=" * 70)
    print("CUSTOM LLM INTEGRATION")
    print("=" * 70)

    advisor = AccessibilityAdvisor()

    # Custom LLM function
    def my_custom_llm(prompt):
        """Your custom LLM integration"""
        # Could be Anthropic, local model, etc.
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    # Use with custom LLM
    result = advisor.ensure_compliance(
        prompt="Explain blockchain", llm_function=my_custom_llm
    )

    print(f"Used custom LLM: {result['stages_used']}")
    print(f"Final score: {result['compliance_score']}/100")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "PROMPT508 TWO-STAGE PIPELINE EXAMPLES" + " " * 16 + "║")
    print("╚" + "=" * 68 + "╝")

    print(
        """
The two-stage pipeline ensures AI outputs meet Section 508 compliance:

Stage 1: ENHANCE INPUT
  → Add accessibility instructions to user's prompt
  → Guides LLM to generate compliant content
  → Free, no API costs

Stage 2: VALIDATE & FIX OUTPUT  
  → Check if LLM output is compliant
  → Automatically fix if needed
  → Only costs if fixing required

This "defense in depth" approach maximizes compliance while minimizing costs.
"""
    )

    try:
        # Run examples
        example_complete_pipeline()
        example_stage_by_stage()
        example_individual_methods()
        example_comparison()
        example_custom_llm()

        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        print("\nMake sure OPENAI_API_KEY is set in .env file:")
        print("  echo 'OPENAI_API_KEY=sk-...' > .env")
