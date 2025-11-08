"""Quick test of two-stage pipeline"""
from prompt508 import AccessibilityAdvisor
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def my_llm(prompt):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# Test the pipeline
advisor = AccessibilityAdvisor()

print("Testing Two-Stage Pipeline...")
print("=" * 70)

result = advisor.ensure_compliance(
    prompt="Explain how APIs work", llm_function=my_llm
)

print(f"\n✓ Pipeline completed")
print(f"Stages used: {result['stages_used']}")
print(f"Was fixed: {result['was_fixed']}")
print(f"Final score: {result['compliance_score']}/100")
print(f"\nFinal output preview:")
print(result["final_output"][:150] + "...")

print("\n" + "=" * 70)
print("✓ Test successful!")
