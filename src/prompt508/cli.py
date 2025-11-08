"""
Command-line interface for prompt508.
Provides analyze and optimize commands for prompt accessibility assessment.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from typing import Optional
from pathlib import Path

from .core.advisor import AccessibilityAdvisor

# Create Typer app
app = typer.Typer(
    name="prompt508",
    help="Accessibility & Plain-Language Optimizer for AI Prompts (Section 508 Compliance)",
    add_completion=False,
)

console = Console()


@app.command()
def analyze(
    text: Optional[str] = typer.Argument(None, help="Text to analyze (or use --file)"),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="File containing prompt to analyze"
    ),
    target_grade: float = typer.Option(8.0, "--grade", "-g", help="Target reading grade level"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Use strict analysis mode"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output results as JSON"),
):
    """
    Analyze a prompt for accessibility and plain language compliance.

    Examples:

        prompt508 analyze "Summarize the seismic telemetry data"

        prompt508 analyze --file prompt.txt --grade 6

        prompt508 analyze "Generate a chart" --strict
    """
    # Get text from file or argument
    if file:
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        text = file.read_text(encoding="utf-8")
    elif not text:
        console.print("[red]Error: Provide text to analyze or use --file option[/red]")
        raise typer.Exit(1)

    # Initialize advisor
    try:
        advisor = AccessibilityAdvisor(target_grade=target_grade, strict_mode=strict)
    except Exception as e:
        console.print(f"[red]Error initializing advisor: {e}[/red]")
        console.print("\n[yellow]Note: Make sure spaCy model is installed:[/yellow]")
        console.print("  python -m spacy download en_core_web_sm")
        raise typer.Exit(1)

    # Perform analysis
    with console.status("[bold green]Analyzing prompt..."):
        analysis = advisor.analyze(text)

    # Output results
    if json_output:
        import json

        print(json.dumps(analysis, indent=2))
    else:
        _display_analysis(analysis, text)


@app.command()
def optimize(
    text: Optional[str] = typer.Argument(None, help="Text to optimize (or use --file)"),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="File containing prompt to optimize"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file for optimized prompt"
    ),
    target_grade: float = typer.Option(8.0, "--grade", "-g", help="Target reading grade level"),
    content_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Content type (images, multimedia, documents, links, forms)"
    ),
    strict: bool = typer.Option(False, "--strict", "-s", help="Use strict optimization mode"),
    no_fixes: bool = typer.Option(False, "--no-fixes", help="Skip rule-based text replacements"),
):
    """
    Optimize a prompt for accessibility and plain language compliance.

    Examples:

        prompt508 optimize "Utilize the API to facilitate data transmission"

        prompt508 optimize --file prompt.txt --output optimized.txt

        prompt508 optimize "Generate chart" --type images --strict
    """
    # Get text from file or argument
    if file:
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        text = file.read_text(encoding="utf-8")
    elif not text:
        console.print("[red]Error: Provide text to optimize or use --file option[/red]")
        raise typer.Exit(1)

    # Initialize advisor
    try:
        advisor = AccessibilityAdvisor(target_grade=target_grade, strict_mode=strict)
    except Exception as e:
        console.print(f"[red]Error initializing advisor: {e}[/red]")
        console.print("\n[yellow]Note: Make sure spaCy model is installed:[/yellow]")
        console.print("  python -m spacy download en_core_web_sm")
        raise typer.Exit(1)

    # Optimize prompt
    with console.status("[bold green]Optimizing prompt..."):
        optimized = advisor.optimize(
            text, content_type=content_type, apply_rule_based_fixes=not no_fixes
        )

    # Output results
    if output:
        output.write_text(optimized, encoding="utf-8")
        console.print(f"[green]✓ Optimized prompt saved to: {output}[/green]")
    else:
        console.print("\n[bold cyan]Original Prompt:[/bold cyan]")
        console.print(Panel(text, border_style="blue"))

        console.print("\n[bold green]Optimized Prompt:[/bold green]")
        console.print(Panel(optimized, border_style="green"))

    # Show before/after analysis
    console.print("\n[bold]Analysis Comparison:[/bold]")

    original_analysis = advisor.analyze(text)
    optimized_analysis = advisor.analyze(optimized)

    comparison_table = Table(title="Before vs After")
    comparison_table.add_column("Metric", style="cyan")
    comparison_table.add_column("Original", style="red")
    comparison_table.add_column("Optimized", style="green")

    comparison_table.add_row(
        "Grade Level",
        f"{original_analysis['readability']['flesch_kincaid_grade']}",
        f"{optimized_analysis['readability']['flesch_kincaid_grade']}",
    )
    comparison_table.add_row(
        "Overall Score",
        f"{original_analysis['overall_score']}/100",
        f"{optimized_analysis['overall_score']}/100",
    )
    comparison_table.add_row(
        "Jargon Terms",
        str(original_analysis["jargon"]["jargon_count"]),
        str(optimized_analysis["jargon"]["jargon_count"]),
    )

    console.print(comparison_table)


@app.command()
def rewrite(
    text: Optional[str] = typer.Argument(None, help="Text to rewrite (or use --file)"),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="File containing prompt to rewrite"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file for rewritten prompt"
    ),
    model: str = typer.Option(
        "gpt-4o-mini", "--model", "-m", help="OpenAI model to use (gpt-4o-mini, gpt-4o, etc.)"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"
    ),
    show_analysis: bool = typer.Option(
        True, "--analysis/--no-analysis", help="Show before/after analysis"
    ),
    show_diff: bool = typer.Option(False, "--diff", "-d", help="Show side-by-side comparison"),
):
    """
    Rewrite a prompt using AI for accessibility and plain language compliance.

    Automatically uses OpenAI if API key is available (from env var or .env file),
    otherwise provides rule-based suggestions.

    Examples:

        prompt508 rewrite "Utilize this methodology to facilitate implementation"

        prompt508 rewrite --file prompt.txt --output rewritten.txt

        prompt508 rewrite "Complex text" --model gpt-4o --api-key sk-...

    Setup .env file:
        Create a .env file in your project with:
        OPENAI_API_KEY=sk-proj-your-key-here
    """
    # Get text from file or argument
    if file:
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        text = file.read_text(encoding="utf-8")
    elif not text:
        console.print("[red]Error: Provide text to rewrite or use --file option[/red]")
        raise typer.Exit(1)

    # Initialize advisor
    try:
        advisor = AccessibilityAdvisor()
    except Exception as e:
        console.print(f"[red]Error initializing advisor: {e}[/red]")
        console.print("\n[yellow]Note: Make sure spaCy model is installed:[/yellow]")
        console.print("  python -m spacy download en_core_web_sm")
        raise typer.Exit(1)

    # Rewrite prompt
    with console.status("[bold green]Rewriting prompt..."):
        result = advisor.rewrite_prompt(
            text, api_key=api_key, model=model, analyze_improvement=show_analysis
        )

    # Check if AI mode or rule-based
    if result["mode"] == "ai":
        console.print("\n[bold green]✓ AI Rewriting Complete[/bold green]")
        console.print(f"[dim]Model: {result['model']}[/dim]")
        console.print(f"[dim]Cost: ${result['cost_usd']:.4f}[/dim]")

        # Show original
        console.print("\n[bold cyan]Original:[/bold cyan]")
        console.print(Panel(text, border_style="blue"))

        # Show rewritten
        console.print("\n[bold green]Rewritten:[/bold green]")
        console.print(Panel(result["rewritten"], border_style="green"))

        # Show analysis if requested
        if show_analysis and "improvements" in result:
            _display_improvements(result["improvements"])

        # Save to file if requested
        if output:
            output.write_text(result["rewritten"], encoding="utf-8")
            console.print(f"\n[green]✓ Rewritten prompt saved to: {output}[/green]")

    else:
        # Rule-based mode
        console.print("\n[yellow]ℹ  Using rule-based suggestions[/yellow]")
        console.print(f"[dim]{result.get('message', '')}[/dim]")

        console.print("\n[bold cyan]Original:[/bold cyan]")
        console.print(Panel(text, border_style="blue"))

        if result.get("suggestions"):
            console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            suggestions_table = Table()
            suggestions_table.add_column("Original", style="red")
            suggestions_table.add_column("→", style="dim")
            suggestions_table.add_column("Replacement", style="green")
            suggestions_table.add_column("Reason", style="cyan")

            for suggestion in result["suggestions"][:15]:
                suggestions_table.add_row(
                    suggestion["original"],
                    "→",
                    suggestion["replacement"],
                    suggestion.get("reason", ""),
                )

            console.print(suggestions_table)
        else:
            console.print("\n[green]✓ No issues found![/green]")

        console.print(
            "\n[bold cyan]💡 Tip:[/bold cyan] Set OPENAI_API_KEY in .env for AI-powered rewriting"
        )
        console.print("[dim]Create a .env file with: OPENAI_API_KEY=sk-proj-your-key[/dim]")


@app.command()
def report(
    text: Optional[str] = typer.Argument(None, help="Text to analyze (or use --file)"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File containing prompt"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for report"),
    target_grade: float = typer.Option(8.0, "--grade", "-g", help="Target reading grade level"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Use strict analysis mode"),
):
    """
    Generate a comprehensive accessibility analysis report.

    Examples:

        prompt508 report "Your prompt text here"

        prompt508 report --file prompt.txt --output report.txt
    """
    # Get text from file or argument
    if file:
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        text = file.read_text(encoding="utf-8")
    elif not text:
        console.print("[red]Error: Provide text to analyze or use --file option[/red]")
        raise typer.Exit(1)

    # Initialize advisor
    try:
        advisor = AccessibilityAdvisor(target_grade=target_grade, strict_mode=strict)
    except Exception as e:
        console.print(f"[red]Error initializing advisor: {e}[/red]")
        console.print("\n[yellow]Note: Make sure spaCy model is installed:[/yellow]")
        console.print("  python -m spacy download en_core_web_sm")
        raise typer.Exit(1)

    # Generate report
    with console.status("[bold green]Generating report..."):
        report_text = advisor.get_report(text)

    # Output report
    if output:
        output.write_text(report_text, encoding="utf-8")
        console.print(f"[green]✓ Report saved to: {output}[/green]")
    else:
        console.print(report_text)


@app.command()
def version():
    """Show version information."""
    from . import __version__, __author__

    console.print(f"[bold cyan]prompt508[/bold cyan] version [green]{__version__}[/green]")
    console.print(f"Author: {__author__}")
    console.print("\nSection 508 Accessibility & Plain Language Optimizer for AI Prompts")


def _display_analysis(analysis: dict, text: str) -> None:
    """Display analysis results in a formatted way."""

    # Header
    console.print("\n[bold cyan]━━━ PROMPT508 ANALYSIS RESULTS ━━━[/bold cyan]\n")

    # Overall score panel
    score = analysis["overall_score"]
    status = "✓ PASSES" if analysis["passes_compliance"] else "✗ NEEDS IMPROVEMENT"
    status_color = "green" if analysis["passes_compliance"] else "red"

    console.print(
        Panel(
            f"[bold]{status}[/bold]\nOverall Score: [bold]{score}/100[/bold]",
            title="Compliance Status",
            border_style=status_color,
        )
    )

    # Readability metrics
    readability = analysis["readability"]
    readability_table = Table(title="📖 Readability Metrics", show_header=False)
    readability_table.add_column("Metric", style="cyan")
    readability_table.add_column("Value")

    readability_table.add_row(
        "Grade Level", f"{readability['flesch_kincaid_grade']} - {readability['grade_description']}"
    )
    readability_table.add_row("Target Grade", str(readability["target_grade"]))
    readability_table.add_row("Reading Ease", f"{readability['flesch_reading_ease']}/100")
    readability_table.add_row("Word Count", str(readability["word_count"]))
    readability_table.add_row("Avg Sentence Length", f"{readability['avg_sentence_length']} words")

    console.print(readability_table)

    # Jargon analysis
    jargon = analysis["jargon"]
    if jargon["has_issues"]:
        jargon_table = Table(title="📝 Jargon & Terminology Issues")
        jargon_table.add_column("Term", style="yellow")
        jargon_table.add_column("Suggestion", style="green")

        for term, suggestion in list(jargon["suggestions"].items())[:10]:
            jargon_table.add_row(term, suggestion)

        console.print(jargon_table)

    # Tone analysis
    tone = analysis["tone"]
    tone_info = f"""
Sentiment: {tone['tone_classification'].title()} (polarity: {tone['sentiment_polarity']})
Subjectivity: {tone['sentiment_subjectivity']:.2f}
Formality: {tone['formality_score'].title()}
Passive Voice: {tone['passive_voice_count']} instances
"""
    console.print(Panel(tone_info.strip(), title="🎭 Tone Analysis", border_style="blue"))

    # Issues
    if analysis["issues"]:
        console.print("\n[bold red]⚠️  Issues Found:[/bold red]")
        for i, issue in enumerate(analysis["issues"], 1):
            console.print(f"  {i}. {issue}")

    # Recommendations
    console.print("\n[bold green]💡 Recommendations:[/bold green]")
    for i, rec in enumerate(analysis["recommendations"], 1):
        console.print(f"  {i}. {rec}")

    console.print()


def _display_improvements(improvements: dict) -> None:
    """Display improvement metrics in a formatted table."""
    console.print("\n[bold]📊 Improvements:[/bold]")

    improvements_table = Table()
    improvements_table.add_column("Metric", style="cyan")
    improvements_table.add_column("Before", style="red")
    improvements_table.add_column("After", style="green")
    improvements_table.add_column("Change", style="yellow")

    # Overall score
    score = improvements["overall_score"]
    change_symbol = "+" if score["change"] >= 0 else ""
    improvements_table.add_row(
        "Overall Score",
        f"{score['before']}/100",
        f"{score['after']}/100",
        f"{change_symbol}{score['change']}",
    )

    # Readability grade
    grade = improvements["readability_grade"]
    change_symbol = "-" if grade["change"] < 0 else "+"
    improvements_table.add_row(
        "Reading Grade",
        f"{grade['before']}",
        f"{grade['after']}",
        f"{change_symbol}{abs(grade['change'])}",
    )

    # Jargon count
    jargon = improvements["jargon_count"]
    change_symbol = "" if jargon["change"] >= 0 else ""
    improvements_table.add_row(
        "Jargon Terms", str(jargon["before"]), str(jargon["after"]), str(jargon["change"])
    )

    # Passive voice
    passive = improvements["passive_voice"]
    improvements_table.add_row(
        "Passive Voice",
        str(passive["before"]),
        str(passive["after"]),
        str(passive["change"]),
    )

    console.print(improvements_table)

    if improvements["now_passes_compliance"]:
        console.print("\n[bold green]✓ Now passes Section 508 compliance![/bold green]")


if __name__ == "__main__":
    app()
