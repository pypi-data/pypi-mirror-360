"""
Command Line Interface for EvalX.
"""

import typer
import json
import asyncio
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from .core.suite import EvaluationSuite, MetricSuite, ResearchSuite
from .core.types import EvaluationInput

app = typer.Typer(name="evalx", help="EvalX: Next-Generation LLM Evaluation Framework")
console = Console()


@app.command()
def evaluate(
    instruction: str = typer.Argument(..., help="Natural language instruction for evaluation"),
    data_file: Path = typer.Option(..., "--data", "-d", help="JSON file with evaluation data"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for results"),
    validation_level: str = typer.Option("production", "--level", "-l", help="Validation level (quick/production/research_grade)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Evaluate using natural language instructions.
    
    Example:
        evalx evaluate "Check my chatbot for helpfulness" --data data.json
    """
    console.print(f"🚀 Starting evaluation: [bold]{instruction}[/bold]")
    
    # Load data
    if not data_file.exists():
        console.print(f"[red]Error: Data file {data_file} not found[/red]")
        raise typer.Exit(1)
    
    with open(data_file) as f:
        data = json.load(f)
    
    console.print(f"📊 Loaded {len(data)} samples from {data_file}")
    
    # Run evaluation
    async def run_evaluation():
        suite = EvaluationSuite.from_instruction(
            instruction=instruction,
            validation_level=validation_level
        )
        
        with Progress() as progress:
            task = progress.add_task("Evaluating...", total=len(data))
            results = await suite.evaluate_async(data)
            progress.update(task, completed=len(data))
        
        return results
    
    results = asyncio.run(run_evaluation())
    
    # Display results
    console.print("\n📈 Evaluation Results:")
    console.print(results.summary())
    
    if verbose:
        table = Table(title="Detailed Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Explanation", style="yellow")
        
        for result in results.metric_results:
            explanation = result.explanation[:50] + "..." if result.explanation and len(result.explanation) > 50 else result.explanation or ""
            table.add_row(
                result.metric_name,
                f"{result.numeric_value:.3f}" if result.numeric_value else "N/A",
                explanation
            )
        
        console.print(table)
    
    # Save results
    if output_file:
        output_data = {
            "instruction": instruction,
            "overall_score": results.overall_score,
            "metric_results": [
                {
                    "metric": r.metric_name,
                    "score": r.numeric_value,
                    "explanation": r.explanation
                }
                for r in results.metric_results
            ],
            "interpretation": results.interpretation,
            "recommendations": results.recommendations
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        console.print(f"💾 Results saved to {output_file}")


@app.command()
def metrics(
    list_all: bool = typer.Option(False, "--list", "-l", help="List all available metrics"),
    metric_name: Optional[str] = typer.Option(None, "--info", "-i", help="Get info about a specific metric"),
):
    """
    Manage and explore available metrics.
    """
    if list_all:
        console.print("📋 Available Metrics:")
        
        # Traditional metrics
        console.print("\n[bold]Traditional Metrics:[/bold]")
        traditional = ["bleu_score", "rouge_score", "meteor_score", "semantic_similarity", "bert_score", "exact_match"]
        for metric in traditional:
            console.print(f"  • {metric}")
        
        # LLM-as-judge metrics
        console.print("\n[bold]LLM-as-Judge Metrics:[/bold]")
        llm_judge = ["accuracy", "helpfulness", "coherence", "groundedness", "relevance"]
        for metric in llm_judge:
            console.print(f"  • {metric}")
    
    elif metric_name:
        console.print(f"ℹ️  Information for metric: [bold]{metric_name}[/bold]")
        # TODO: Add detailed metric information
        console.print("Detailed metric information coming soon!")
    
    else:
        console.print("Use --list to see all metrics or --info <metric_name> for details")


@app.command()
def research(
    data_file: Path = typer.Option(..., "--data", "-d", help="JSON file with evaluation data"),
    metrics: List[str] = typer.Option(["accuracy", "helpfulness"], "--metrics", "-m", help="Metrics to evaluate"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for research report"),
    confidence_level: float = typer.Option(0.95, "--confidence", help="Confidence level for statistics"),
):
    """
    Run research-grade evaluation with statistical analysis.
    """
    console.print("🔬 Starting research-grade evaluation...")
    
    # Load data
    with open(data_file) as f:
        data = json.load(f)
    
    console.print(f"📊 Loaded {len(data)} samples")
    
    # Run research evaluation
    async def run_research():
        suite = ResearchSuite(
            metrics=metrics,
            statistical_tests=["t_test", "bootstrap"],
            human_validation=False
        )
        
        return await suite.evaluate_research_grade(data)
    
    results = asyncio.run(run_research())
    
    # Display results
    console.print("\n📈 Research Results:")
    console.print(f"Overall Score: {results.overall_score:.3f}")
    
    # Statistical results table
    if results.statistical_results:
        table = Table(title="Statistical Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Mean ± Std", style="green")
        table.add_column("95% CI", style="yellow")
        table.add_column("Effect Size", style="magenta")
        
        for metric_name, stats in results.statistical_results.items():
            ci_str = f"[{stats.confidence_interval[0]:.3f}, {stats.confidence_interval[1]:.3f}]"
            effect_str = f"{stats.effect_size:.3f}" if stats.effect_size else "N/A"
            table.add_row(
                metric_name,
                f"{stats.mean:.3f} ± {stats.std:.3f}",
                ci_str,
                effect_str
            )
        
        console.print(table)
    
    # Generate and save research report
    if output_file:
        from .core.suite import ResearchSuite
        report = results.metadata.get("research_report", "No report available")
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        console.print(f"📄 Research report saved to {output_file}")


@app.command()
def version():
    """Show EvalX version information."""
    from . import __version__, __author__
    console.print(f"EvalX version {__version__}")
    console.print(f"By {__author__}")


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main() 