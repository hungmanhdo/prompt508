"""
Basic usage example for prompt508.
Demonstrates how to use the AccessibilityAdvisor to analyze and optimize prompts.
"""

from prompt508 import AccessibilityAdvisor

def main():
    # Initialize the advisor with target grade level 8 (plain language standard)
    advisor = AccessibilityAdvisor(
        target_grade=8.0,
        include_alt_text=True,
        include_captions=True,
        include_structure=True
    )
    
    # Example 1: Analyze a prompt with accessibility issues
    print("=" * 70)
    print("EXAMPLE 1: Analyzing a Prompt with Issues")
    print("=" * 70)
    
    problematic_prompt = """
    Utilize the seismic telemetry API to facilitate the transmission of 
    earthquake data. Subsequently, implement visualization methodologies 
    to demonstrate the magnitude distribution.
    """
    
    print("\nOriginal Prompt:")
    print(problematic_prompt)
    
    # Analyze the prompt
    analysis = advisor.analyze(problematic_prompt)
    
    print(f"\nOverall Score: {analysis['overall_score']}/100")
    print(f"Passes Compliance: {analysis['passes_compliance']}")
    print(f"Grade Level: {analysis['readability']['flesch_kincaid_grade']}")
    print(f"Jargon Terms: {analysis['jargon']['jargon_count']}")
    
    print("\nIssues Found:")
    for issue in analysis['issues']:
        print(f"  - {issue}")
    
    print("\nRecommendations:")
    for rec in analysis['recommendations'][:3]:
        print(f"  - {rec}")
    
    # Example 2: Optimize the prompt
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Optimizing the Prompt")
    print("=" * 70)
    
    optimized = advisor.optimize(problematic_prompt, content_type="images")
    
    print("\nOptimized Prompt:")
    print(optimized)
    
    # Analyze optimized version
    optimized_analysis = advisor.analyze(optimized)
    print(f"\nImproved Score: {optimized_analysis['overall_score']}/100")
    print(f"Improved Grade Level: {optimized_analysis['readability']['flesch_kincaid_grade']}")
    
    # Example 3: Generate a comprehensive report
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Comprehensive Report")
    print("=" * 70)
    
    report = advisor.get_report(problematic_prompt)
    print(report)
    
    # Example 4: Working with clean, accessible prompt
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Well-Written Prompt")
    print("=" * 70)
    
    good_prompt = """
    Create a simple chart showing earthquake data for the past week. 
    Use clear labels and include alt text describing the data trends.
    Make sure the chart is easy to read.
    """
    
    print("\nPrompt:")
    print(good_prompt)
    
    good_analysis = advisor.analyze(good_prompt)
    print(f"\nScore: {good_analysis['overall_score']}/100")
    print(f"Passes Compliance: {good_analysis['passes_compliance']}")
    print(f"Grade Level: {good_analysis['readability']['flesch_kincaid_grade']}")
    

if __name__ == "__main__":
    print("\n🔍 Prompt508 - Basic Usage Examples\n")
    print("This script demonstrates how to use prompt508 to analyze and optimize")
    print("AI prompts for Section 508 accessibility compliance.\n")
    
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have installed the required dependencies:")
        print("  pip install prompt508")
        print("  python -m spacy download en_core_web_sm")
