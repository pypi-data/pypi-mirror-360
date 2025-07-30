"""Command-line interface for AlexScan domain analyzer."""

import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .analyzers import (
    BlocklistAnalyzer,
    CrawlerAnalyzer,
    DGAAnalyzer,
    DNSAnalyzer,
    HeadersAnalyzer,
    HierarchicalClassificationAnalyzer,
    LLMSummaryAnalyzer,
    PortScannerAnalyzer,
    ReportGenerator,
    ScreenshotAnalyzer,
    SSLAnalyzer,
    WhitelistAnalyzer,
    WHOISAnalyzer,
    calculate_domain_safety_rating,
)
from .utils.cache_manager import CacheManager

app = typer.Typer()
console = Console()


@app.command()
def analyze(
    domain: str = typer.Argument(..., help="Domain to analyze"),
    analyzers: Optional[List[str]] = typer.Argument(
        None,
        help="Specific analyzers to run (dns, whois, ssl, blocklist, whitelist, dga, crawler, headers, ports, screenshot, llm_summary, hierarchical_classification)",
    ),
    all: bool = typer.Option(False, "--all", help="Run all analyzers"),
    dns: bool = typer.Option(False, "--dns", help="Run DNS analysis"),
    whois: bool = typer.Option(False, "--whois", help="Run WHOIS analysis"),
    ssl: bool = typer.Option(False, "--ssl", help="Run SSL analysis"),
    blocklist: bool = typer.Option(False, "--blocklist", help="Run blocklist analysis"),
    whitelist: bool = typer.Option(False, "--whitelist", help="Run whitelist analysis"),
    dga: bool = typer.Option(False, "--dga", help="Run DGA analysis"),
    crawler: bool = typer.Option(False, "--crawler", help="Run web crawler analysis"),
    headers: bool = typer.Option(False, "--headers", help="Run HTTP headers analysis"),
    ports: bool = typer.Option(False, "--ports", help="Run port scanning analysis"),
    screenshot: bool = typer.Option(False, "--screenshot", help="Run screenshot analysis"),
    llm_summary: bool = typer.Option(False, "--llm-summary", help="Run LLM summary analysis"),
    categorize: bool = typer.Option(
        False, "--categorize", help="Categorize domain using LLM-powered content classification"
    ),
    report: bool = typer.Option(False, "--report", help="Generate markdown report"),
    pdf: bool = typer.Option(False, "--pdf", help="Also generate PDF report (requires markdown-pdf)"),
    cache_stats: bool = typer.Option(False, "--cache-stats", help="Show cache statistics"),
):
    """Analyze a domain for security and infrastructure information."""

    # Initialize cache manager
    cache_manager = CacheManager()

    if cache_stats:
        stats = cache_manager.get_cache_stats()
        console.print(
            f"📊 Cache Stats: {stats['total_keys']} keys, {stats['hit_rate']:.1%} hit rate, {stats['memory_used']} memory used"
        )
        return

    # Determine which analyzers to run
    analyzers_to_run = []

    # If report is requested, always run all analyzers for comprehensive report
    if report:
        analyzers_to_run = [
            "dns",
            "whois",
            "ssl",
            "blocklist",
            "whitelist",
            "dga",
            "crawler",
            "headers",
            "ports",
            "screenshot",
            "llm_summary",
            "hierarchical_classification",
        ]
        console.print("📄 Report mode: Running all analyzers for comprehensive analysis")
    elif all:
        analyzers_to_run = [
            "dns",
            "whois",
            "ssl",
            "blocklist",
            "whitelist",
            "dga",
            "crawler",
            "headers",
            "ports",
            "screenshot",
            "llm_summary",
            "hierarchical_classification",
        ]
    elif analyzers:
        analyzers_to_run = analyzers
    else:
        # Check individual flags
        if dns:
            analyzers_to_run.append("dns")
        if whois:
            analyzers_to_run.append("whois")
        if ssl:
            analyzers_to_run.append("ssl")
        if blocklist:
            analyzers_to_run.append("blocklist")
        if whitelist:
            analyzers_to_run.append("whitelist")
        if dga:
            analyzers_to_run.append("dga")
        if crawler:
            analyzers_to_run.append("crawler")
        if headers:
            analyzers_to_run.append("headers")
        if ports:
            analyzers_to_run.append("ports")
        if screenshot:
            analyzers_to_run.append("screenshot")
        if llm_summary:
            analyzers_to_run.append("llm_summary")
        if categorize:
            analyzers_to_run.append("hierarchical_classification")

        # Default analyzers if none specified
        if not analyzers_to_run:
            analyzers_to_run = ["dns", "whois", "ssl", "blocklist", "whitelist", "dga"]

    # Initialize analyzers
    analyzer_instances = {
        "dns": DNSAnalyzer(),
        "whois": WHOISAnalyzer(),
        "ssl": SSLAnalyzer(),
        "blocklist": BlocklistAnalyzer(),
        "whitelist": WhitelistAnalyzer(),
        "dga": DGAAnalyzer(),
        "crawler": CrawlerAnalyzer(),
        "headers": HeadersAnalyzer(),
        "ports": PortScannerAnalyzer(),
        "screenshot": ScreenshotAnalyzer(),
        "llm_summary": LLMSummaryAnalyzer(),
        "hierarchical_classification": HierarchicalClassificationAnalyzer(),
    }

    # Store results
    results = {}
    website_content = None

    # Run analyzers
    for analyzer_name in analyzers_to_run:
        if analyzer_name not in analyzer_instances:
            console.print(f"⚠️ Unknown analyzer: {analyzer_name}")
            continue

        analyzer = analyzer_instances[analyzer_name]

        # Check cache first
        cached_result = cache_manager.get_cached_result(domain, analyzer_name)
        if cached_result:
            console.print(f"✨ Using cached result for {analyzer_name}")
            results[f"{analyzer_name}_results"] = cached_result
            continue

        console.print(f"🔍 Running {analyzer_name} analysis...")

        try:
            result = analyzer.analyze(domain)
            # DO NOT print analyzer-specific output here. All output is handled by the CLI after all analyzers complete.
            # This ensures the safety rating is always shown, even for a single analyzer.
            if analyzer_name == "crawler" and result.get("crawler_data", {}).get("success"):
                website_content = result["crawler_data"].get("content", "")
            results[f"{analyzer_name}_results"] = result
            cache_manager.set_cached_result(domain, analyzer_name, result)
        except Exception as e:
            console.print(f"❌ Error running {analyzer_name} analyzer: {str(e)}")
            results[f"{analyzer_name}_results"] = {"errors": [str(e)]}

    # Define analyzers that should be ignored for safety assessment
    ignored_for_safety = {"hierarchical_classification", "llm_summary"}

    # Check if only ignored analyzers are being run
    security_analyzers = [name for name in analyzers_to_run if name not in ignored_for_safety]

    # Only show safety assessment if security-relevant analyzers are being run
    if security_analyzers:
        try:
            console.print("\n" + "🔒" + "=" * 78 + "🔒")
            safety_rating = calculate_domain_safety_rating(results)
            console.print(
                Panel(
                    f"[bold white]DOMAIN SAFETY ASSESSMENT[/bold white]\n\n"
                    f"[bold cyan]Domain:[/bold cyan] [bold]{domain}[/bold]\n"
                    f"[bold cyan]Analyzers Run:[/bold cyan] {len(results)}/{len(analyzers_to_run)}\n\n"
                    f"[bold yellow]OVERALL SAFETY SCORE:[/bold yellow] [bold white]{safety_rating['overall_score']}/10[/bold white] "
                    f"([bold white]{safety_rating['percentage_score']}%[/bold white])\n"
                    f"[bold yellow]CLASSIFICATION:[/bold yellow] [bold white]{safety_rating['classification']}[/bold white]",
                    title="[bold red]🔒 SECURITY RATING 🔒[/bold red]",
                    border_style="red",
                    padding=(1, 2),
                )
            )
            if safety_rating["component_scores"]:
                console.print("\n[bold cyan]COMPONENT SAFETY SCORES:[/bold cyan]")
                score_table = Table(
                    title="[bold]Individual Analyzer Safety Scores[/bold]",
                    show_header=True,
                    header_style="bold magenta",
                    border_style="blue",
                )
                score_table.add_column("Analyzer", style="cyan", width=20)
                score_table.add_column("Safety Score", style="green", width=15)
                score_table.add_column("Status", style="yellow", width=20)
                for analyzer, score in safety_rating["component_scores"].items():
                    analyzer_name = analyzer.replace("_", " ").title()
                    if score >= 7.0:
                        status = "✅ Good"
                    elif score >= 5.0:
                        status = "⚠️ Moderate"
                    elif score >= 3.0:
                        status = "❌ Poor"
                    else:
                        status = "🚨 Critical"
                    score_table.add_row(analyzer_name, f"{score}/10", status)
                console.print(score_table)
            else:
                console.print("\n[bold yellow]⚠️ No component scores available[/bold yellow]")
            console.print("🔒" + "=" * 78 + "🔒\n")
        except Exception as e:
            console.print(f"\n❌ Error calculating safety rating: {str(e)}")
            console.print(f"Results keys: {list(results.keys())}")
            console.print("🔒" + "=" * 78 + "🔒\n")
    else:
        # Show a simple completion message for non-security analyzers
        console.print(f"\n✅ Analysis completed for {domain}")
        console.print(
            f"📊 Analyzers run: {', '.join(analyzers_to_run).replace('hierarchical_classification', 'categorize')}"
        )

        # Show hierarchical classification results if available
        if "hierarchical_classification" in analyzers_to_run:
            classification_result = results.get("hierarchical_classification_results", {})
            if classification_result and not classification_result.get("errors"):
                classification = classification_result.get("classification", {})
                if classification:
                    console.print("\n" + "🔍" + "=" * 78 + "🔍")
                    console.print(
                        Panel(
                            f"[bold white]DOMAIN CATEGORIZATION[/bold white]\n\n"
                            f"[bold cyan]Domain:[/bold cyan] [bold]{domain}[/bold]\n\n"
                            f"[bold yellow]Primary Category:[/bold yellow] [bold white]{classification.get('primary_category', 'Unknown')}[/bold white]\n"
                            f"[bold yellow]Subcategory:[/bold yellow] [bold white]{classification.get('subcategory', 'Unknown')}[/bold white]\n"
                            f"[bold yellow]Confidence:[/bold yellow] [bold white]{classification.get('confidence', 0)}%[/bold white]\n\n"
                            f"[bold cyan]Evidence:[/bold cyan]\n{classification.get('evidence', 'No evidence provided')}",
                            title="[bold blue]🔍 CATEGORIZATION RESULTS 🔍[/bold blue]",
                            border_style="blue",
                            padding=(1, 2),
                        )
                    )
                    console.print("🔍" + "=" * 78 + "🔍\n")

    # Run LLM summary if requested (after safety rating display)
    if "llm_summary" in analyzers_to_run:
        console.print("🤖 Running LLM Summary Analysis...")
        try:
            llm_analyzer = analyzer_instances["llm_summary"]
            llm_result = llm_analyzer.analyze(domain, results, website_content)
            results["llm_summary_results"] = llm_result

            # Cache the LLM result
            cache_manager.set_cached_result(domain, "llm_summary", llm_result)

            console.print("✅ LLM Summary completed")
        except Exception as e:
            console.print(f"❌ Error running LLM summary: {str(e)}")
            results["llm_summary_results"] = {"errors": [str(e)]}

    # Generate report if requested
    if report:
        try:
            report_generator = ReportGenerator()
            report_path = report_generator.generate_report(domain, results, pdf=pdf)
            console.print(f"📄 Report generated: {report_path}")
        except Exception as e:
            console.print(f"❌ Error generating report: {str(e)}")

    # Show cache statistics
    stats = cache_manager.get_cache_stats()
    console.print(
        f"📊 Cache Stats: {stats['total_keys']} keys, {stats['hit_rate']:.1%} hit rate, {stats['memory_used']} memory used"
    )


@app.command()
def cache(
    action: str = typer.Argument(..., help="Cache action (stats, clear, invalidate)"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Domain to invalidate (for invalidate action)"),
):
    """Manage cache operations."""

    cache_manager = CacheManager()

    if action == "stats":
        stats = cache_manager.get_cache_stats()
        console.print("📊 Cache Statistics:")
        console.print(f"  Total Keys: {stats['total_keys']}")
        console.print(f"  Memory Used: {stats['memory_used']}")
        console.print(f"  Hit Rate: {stats['hit_rate']:.1%}")
        console.print(f"  Peak Memory: {stats['peak_memory']}")
        console.print(f"  Evictions: {stats['evictions']}")

    elif action == "clear":
        cache_manager.clear_cache()
        console.print("🗑️ Cache cleared successfully")

    elif action == "invalidate":
        if not domain:
            console.print("❌ Domain must be specified for invalidate action")
            sys.exit(1)
        cache_manager.invalidate_domain(domain)
        console.print(f"🗑️ Cache invalidated for domain: {domain}")

    else:
        console.print("❌ Invalid cache action. Use: stats, clear, or invalidate")


@app.command()
def init():
    """Initialize AlexScan environment (Docker containers)."""
    console.print("🚀 Initializing AlexScan environment...")

    # This would typically start Docker containers for Redis and Ollama
    # For now, just provide instructions
    console.print("📋 Please ensure the following are available:")
    console.print("  - Redis server (for caching)")
    console.print("  - Ollama (for LLM analysis)")
    console.print("  - Docker (for containerized services)")


if __name__ == "__main__":
    app()
