"""Command-line interface for alexscan."""

import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from alexscan import __version__
from alexscan.analyzers.blocklist import BlocklistAnalyzer
from alexscan.analyzers.dga import DGAAnalyzer
from alexscan.analyzers.dns import DNSAnalyzer
from alexscan.analyzers.llm_summary import LLMSummaryAnalyzer
from alexscan.analyzers.ssl import SSLAnalyzer
from alexscan.analyzers.whois import WHOISAnalyzer
from alexscan.utils.validators import is_valid_domain

app = typer.Typer(help="Domain analysis tool")


@app.command()
def init(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Initialize Docker and Ollama for LLM-based analysis."""
    console = Console()

    console.print(Panel("Initializing alexscan environment", style="bright_blue"))

    # Create LLM analyzer to access initialization methods
    llm_analyzer = LLMSummaryAnalyzer()

    # Check if already initialized
    if llm_analyzer.is_available():
        console.print("[green]✓ Ollama is already running and ready[/green]")

        # Show model information
        model_info = llm_analyzer.get_model_info()
        if model_info:
            console.print(f"[green]✓ Model '{model_info.get('name', 'Unknown')}' is available[/green]")

        console.print(Panel("Environment is already initialized and ready!", style="green"))
        return

    # Initialize with progress tracking
    success = _initialize_llm_environment(console, llm_analyzer, verbose)

    if success:
        console.print(Panel("✅ Initialization completed successfully!", style="green"))
        console.print("[green]You can now use the --summary flag with domain analysis.[/green]")
    else:
        console.print(Panel("❌ Initialization failed", style="red"))
        console.print("[red]Please check the error messages above and try again.[/red]")
        console.print("[yellow]You can still use other analysis features without the LLM summary.[/yellow]")
        raise typer.Exit(1)


def _initialize_llm_environment(console: Console, llm_analyzer: LLMSummaryAnalyzer, verbose: bool = False) -> bool:
    """Initialize LLM environment with progress feedback."""

    # Step 1: Check Docker availability
    with console.status("[bold blue]Checking Docker availability...", spinner="dots"):
        if not llm_analyzer._is_docker_available():
            console.print("[red]✗ Docker is not available[/red]")
            console.print("[yellow]Please install Docker and ensure it's running.[/yellow]")
            return False

        console.print("[green]✓ Docker is available[/green]")

    # Step 2: Check if Ollama container is running
    with console.status("[bold blue]Checking Ollama container status...", spinner="dots"):
        if llm_analyzer._is_ollama_container_running():
            console.print("[green]✓ Ollama container is already running[/green]")
            container_started = True
        else:
            console.print("[yellow]• Ollama container is not running[/yellow]")
            container_started = False

    # Step 3: Start Ollama container if needed
    if not container_started:
        with console.status("[bold blue]Starting Ollama container...", spinner="dots"):
            if llm_analyzer._start_ollama_container():
                console.print("[green]✓ Ollama container started successfully[/green]")
            else:
                console.print("[red]✗ Failed to start Ollama container[/red]")
                return False

    # Step 4: Wait for Ollama to be ready
    with console.status("[bold blue]Waiting for Ollama to be ready...", spinner="dots"):
        max_wait = 30
        start_time = time.time()

        while time.time() - start_time < max_wait:
            if llm_analyzer._is_ollama_available():
                console.print("[green]✓ Ollama is ready and responding[/green]")
                break
            time.sleep(2)
        else:
            console.print("[red]✗ Ollama did not become ready within 30 seconds[/red]")
            return False

    # Step 5: Check and pull model if needed
    console.print(f"[blue]Checking model availability: {llm_analyzer.model}[/blue]")

    with console.status(f"[bold blue]Checking if model '{llm_analyzer.model}' is available...", spinner="dots"):
        if llm_analyzer._ensure_model_available():
            console.print(f"[green]✓ Model '{llm_analyzer.model}' is available[/green]")
        else:
            console.print(f"[red]✗ Failed to ensure model '{llm_analyzer.model}' is available[/red]")
            console.print("[yellow]This might be due to network issues or the model name being invalid.[/yellow]")
            return False

    # Step 6: Final verification
    with console.status("[bold blue]Performing final verification...", spinner="dots"):
        if llm_analyzer.is_available():
            console.print("[green]✓ LLM environment is fully initialized[/green]")

            # Show model information
            model_info = llm_analyzer.get_model_info()
            if model_info and verbose:
                info_table = Table(title="Model Information", show_header=True, header_style="bold magenta")
                info_table.add_column("Field", style="dim", width=15)
                info_table.add_column("Value", style="dim", width=50)

                info_table.add_row("Name", model_info.get("name", "Unknown"))
                if model_info.get("size"):
                    size_gb = model_info["size"] / (1024 * 1024 * 1024)
                    info_table.add_row("Size", f"{size_gb:.1f} GB")
                info_table.add_row("Digest", model_info.get("digest", "Unknown")[:16] + "...")

                console.print(info_table)

            return True
        else:
            console.print("[red]✗ LLM environment verification failed[/red]")
            return False


@app.command()
def analyze(
    domain: str = typer.Argument(..., help="Domain to analyze"),
    dns: bool = typer.Option(False, "--dns", help="Run DNS analysis only"),
    whois: bool = typer.Option(False, "--whois", help="Run WHOIS analysis only"),
    ssl: bool = typer.Option(False, "--ssl", help="Run SSL analysis only"),
    blocklist: bool = typer.Option(False, "--blocklist", help="Run Blocklist analysis only"),
    dga: bool = typer.Option(False, "--dga", help="Run DGA analysis only"),
    summary: bool = typer.Option(False, "--summary", help="Run LLM summary analysis only"),
    all_analyzers: bool = typer.Option(False, "--all", help="Run all available analyzers"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Analyze a domain using various analyzers."""
    console = Console()

    # Validate domain
    if not is_valid_domain(domain):
        console.print(f"[red]Error: '{domain}' is not a valid domain name[/red]")
        raise typer.Exit(1)

    if verbose:
        console.print(f"[blue]Analyzing domain: {domain}[/blue]")

    # Determine which analyzers to run
    run_dns = False
    run_whois = False
    run_ssl = False
    run_blocklist = False
    run_dga = False
    run_summary = False

    if dns:
        run_dns = True
    elif whois:
        run_whois = True
    elif ssl:
        run_ssl = True
    elif blocklist:
        run_blocklist = True
    elif dga:
        run_dga = True
    elif summary:
        run_summary = True
        # For summary, we need to run other analyzers first but won't display them
        run_dns = True
        run_whois = True
        run_ssl = True
        run_blocklist = True
        run_dga = True
    elif all_analyzers:
        run_dns = True
        run_whois = True
        run_ssl = True
        run_blocklist = True
        run_dga = True
        run_summary = True
    else:
        # Default behavior: run all available analyzers except summary
        run_dns = True
        run_whois = True
        run_ssl = True
        run_blocklist = True
        run_dga = True

    # Run DNS analyzer if requested
    if run_dns:
        dns_analyzer = DNSAnalyzer()

        if not dns_analyzer.is_available():
            console.print("[red]Error: DNS analyzer is not available (dnspython not installed)[/red]")
            raise typer.Exit(1)

        try:
            dns_results = dns_analyzer.analyze(domain)
            # Only display results if not running summary-only mode
            if not summary or all_analyzers:
                _display_dns_results(console, dns_results, verbose)
        except Exception as e:
            console.print(f"[red]Error during DNS analysis: {str(e)}[/red]")
            raise typer.Exit(1)

    # Run WHOIS analyzer if requested
    if run_whois:
        whois_analyzer = WHOISAnalyzer()

        if not whois_analyzer.is_available():
            console.print("[red]Error: WHOIS analyzer is not available (python-whois not installed)[/red]")
            raise typer.Exit(1)

        try:
            whois_results = whois_analyzer.analyze(domain)
            # Only display results if not running summary-only mode
            if not summary or all_analyzers:
                _display_whois_results(console, whois_results, verbose)
        except Exception as e:
            console.print(f"[red]Error during WHOIS analysis: {str(e)}[/red]")
            raise typer.Exit(1)

    # Run SSL analyzer if requested
    if run_ssl:
        ssl_analyzer = SSLAnalyzer()

        if not ssl_analyzer.is_available():
            console.print("[red]Error: SSL analyzer is not available[/red]")
            raise typer.Exit(1)

        try:
            ssl_results = ssl_analyzer.analyze(domain)
            # Only display results if not running summary-only mode
            if not summary or all_analyzers:
                _display_ssl_results(console, ssl_results, verbose)
        except Exception as e:
            console.print(f"[red]Error during SSL analysis: {str(e)}[/red]")
            raise typer.Exit(1)

    # Run Blocklist analyzer if requested
    if run_blocklist:
        blocklist_analyzer = BlocklistAnalyzer()

        if not blocklist_analyzer.is_available():
            console.print("[red]Error: Blocklist analyzer is not available (requests not installed)[/red]")
            raise typer.Exit(1)

        try:
            blocklist_results = blocklist_analyzer.analyze(domain)
            # Only display results if not running summary-only mode
            if not summary or all_analyzers:
                _display_blocklist_results(console, blocklist_results, verbose)
        except Exception as e:
            console.print(f"[red]Error during Blocklist analysis: {str(e)}[/red]")
            raise typer.Exit(1)

    # Run DGA analyzer if requested
    if run_dga:
        dga_analyzer = DGAAnalyzer()

        if not dga_analyzer.is_available():
            console.print("[red]Error: DGA analyzer is not available[/red]")
            raise typer.Exit(1)

        try:
            dga_results = dga_analyzer.analyze(domain)
            # Only display results if not running summary-only mode
            if not summary or all_analyzers:
                _display_dga_results(console, dga_results, verbose)
        except Exception as e:
            console.print(f"[red]Error during DGA analysis: {str(e)}[/red]")
            raise typer.Exit(1)

    # Collect results for summary if needed
    all_results = {}
    if run_summary:
        # Collect results from analyzers that ran successfully
        if run_dns and "dns_results" not in locals():
            dns_results = {"records": {}, "errors": ["DNS analyzer was not run"]}
        if run_whois and "whois_results" not in locals():
            whois_results = {"whois_data": {}, "errors": ["WHOIS analyzer was not run"]}
        if run_ssl and "ssl_results" not in locals():
            ssl_results = {"ssl_data": {}, "errors": ["SSL analyzer was not run"]}
        if run_blocklist and "blocklist_results" not in locals():
            blocklist_results = {"blocklist_status": {}, "summary": {}, "errors": ["Blocklist analyzer was not run"]}
        if run_dga and "dga_results" not in locals():
            dga_results = {"dga_analysis": {}, "errors": ["DGA analyzer was not run"]}

        # Store results for summarization
        if "dns_results" in locals():
            all_results["dns_results"] = dns_results
        if "whois_results" in locals():
            all_results["whois_results"] = whois_results
        if "ssl_results" in locals():
            all_results["ssl_results"] = ssl_results
        if "blocklist_results" in locals():
            all_results["blocklist_results"] = blocklist_results
        if "dga_results" in locals():
            all_results["dga_results"] = dga_results

    # Run LLM summary analyzer if requested
    if run_summary:
        llm_analyzer = LLMSummaryAnalyzer()

        if not llm_analyzer.is_available():
            console.print("[yellow]LLM summary analyzer is not ready.[/yellow]")
            console.print("[blue]Tip: Run 'alexscan init' to set up the LLM environment.[/blue]")

            if verbose:
                console.print("[yellow]Attempting to start Ollama automatically...[/yellow]")
                # The analyzer will attempt to start Ollama automatically
                try:
                    llm_results = llm_analyzer.analyze(domain, all_results)
                    if llm_results.get("errors"):
                        console.print(f"[red]Error: {llm_results['errors'][0]}[/red]")
                        if not summary:  # Don't exit if running other analyzers too
                            console.print("[yellow]Continuing with other analysis results...[/yellow]")
                        else:
                            console.print("[blue]Try running 'alexscan init' first, then retry your command.[/blue]")
                            raise typer.Exit(1)
                    else:
                        _display_llm_summary_results(console, llm_results, verbose)
                except Exception as e:
                    console.print(f"[red]Error during LLM summary analysis: {str(e)}[/red]")
                    if summary:  # Only exit if summary was the only requested analyzer
                        console.print("[blue]Try running 'alexscan init' first, then retry your command.[/blue]")
                        raise typer.Exit(1)
            else:
                if summary:  # Only exit if summary was the only requested analyzer
                    console.print("[blue]Try running 'alexscan init' first, then retry your command.[/blue]")
                    raise typer.Exit(1)
        else:
            try:
                llm_results = llm_analyzer.analyze(domain, all_results)
                _display_llm_summary_results(console, llm_results, verbose)
            except Exception as e:
                console.print(f"[red]Error during LLM summary analysis: {str(e)}[/red]")
                if summary:  # Only exit if summary was the only requested analyzer
                    raise typer.Exit(1)

    if not run_dns and not run_whois and not run_ssl and not run_blocklist and not run_dga and not run_summary:
        console.print("[yellow]No analyzers selected to run[/yellow]")

    if verbose:
        console.print(f"[green]Analysis completed for {domain}[/green]")


def _display_dns_results(console: Console, results: dict, verbose: bool = False):
    """Display DNS analysis results."""
    domain = results.get("domain", "")
    records = results.get("records", {})
    errors = results.get("errors", [])

    # Create panel for DNS results
    console.print(Panel(f"DNS Analysis for {domain}", style="blue"))

    if records:
        # Create table for DNS records
        table = Table(title="DNS Records", show_header=True, header_style="bold magenta")
        table.add_column("Record Type", style="dim", width=12)
        table.add_column("Description", style="dim", width=20)
        table.add_column("Values", style="dim", width=30)

        for record_type, record_data in records.items():
            description = record_data.get("description", "")
            values = record_data.get("values", [])

            if values:
                # Add first value
                table.add_row(record_type, description, values[0])

                # Add remaining values with empty record type and description
                for value in values[1:]:
                    table.add_row("", "", value)

        console.print(table)

    if errors:
        console.print(Panel("Errors encountered during DNS analysis:", style="red"))
        for error in errors:
            console.print(f"  [red]• {error}[/red]")


def _display_whois_results(console: Console, results: dict, verbose: bool = False):
    """Display WHOIS analysis results."""
    domain = results.get("domain", "")
    whois_data = results.get("whois_data", {})
    errors = results.get("errors", [])

    # Create panel for WHOIS results
    console.print(Panel(f"WHOIS Analysis for {domain}", style="green"))

    if whois_data:
        # Create table for WHOIS data
        table = Table(title="WHOIS Information", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="dim", width=15)
        table.add_column("Value", style="dim", width=50)

        # Field mapping for better display
        field_mapping = {
            "registrar": "Registrar",
            "creation_date": "Created",
            "expiry_date": "Expires",
            "updated_date": "Updated",
            "status": "Status",
            "organization": "Organization",
            "country": "Country",
        }

        for field, value in whois_data.items():
            if field == "name_servers":
                # Handle name servers separately
                if value:
                    table.add_row("Name Servers", value[0])
                    for ns in value[1:]:
                        table.add_row("", ns)
            else:
                display_name = field_mapping.get(field, field.replace("_", " ").title())
                table.add_row(display_name, str(value))

        console.print(table)

    if errors:
        console.print(Panel("Errors encountered during WHOIS analysis:", style="red"))
        for error in errors:
            console.print(f"  [red]• {error}[/red]")


def _display_ssl_results(console: Console, results: dict, verbose: bool = False):
    """Display SSL analysis results."""
    domain = results.get("domain", "")
    ssl_data = results.get("ssl_data", {})
    errors = results.get("errors", [])

    # Create panel for SSL results
    console.print(Panel(f"SSL Analysis for {domain}", style="yellow"))

    if ssl_data:
        # Create table for SSL data
        table = Table(title="SSL Certificate Information", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", style="dim", width=60)

        # Field mapping for better display
        field_mapping = {
            "subject": "Subject",
            "issuer": "Issuer",
            "serial_number": "Serial Number",
            "version": "Version",
            "valid_from": "Valid From",
            "valid_to": "Valid To",
            "is_expired": "Is Expired",
            "days_until_expiry": "Days Until Expiry",
            "signature_algorithm": "Signature Algorithm",
            "protocol_version": "Protocol Version",
            "cipher_suite": "Cipher Suite",
            "cipher_version": "Cipher Version",
            "cipher_bits": "Cipher Bits",
        }

        for field, value in ssl_data.items():
            if field == "subject_alt_names":
                # Handle subject alternative names separately
                if value:
                    table.add_row("Subject Alt Names", value[0])
                    for san in value[1:]:
                        table.add_row("", san)
            else:
                display_name = field_mapping.get(field, field.replace("_", " ").title())

                # Special formatting for certain fields
                if field == "is_expired":
                    value_str = "Yes" if value else "No"
                    style = "red" if value else "green"
                    table.add_row(display_name, f"[{style}]{value_str}[/{style}]")
                elif field == "days_until_expiry":
                    if value <= 30:
                        style = "red" if value <= 7 else "yellow"
                        table.add_row(display_name, f"[{style}]{value} days[/{style}]")
                    else:
                        table.add_row(display_name, f"{value} days")
                else:
                    table.add_row(display_name, str(value))

        console.print(table)

    if errors:
        console.print(Panel("Errors encountered during SSL analysis:", style="red"))
        for error in errors:
            console.print(f"  [red]• {error}[/red]")


def _display_blocklist_results(console: Console, results: dict, verbose: bool = False):
    """Display Blocklist analysis results."""
    domain = results.get("domain", "")
    blocklist_status = results.get("blocklist_status", {})
    summary = results.get("summary", {})
    errors = results.get("errors", [])

    # Create panel for Blocklist results
    console.print(Panel(f"Blocklist Analysis for {domain}", style="magenta"))

    # Display summary first
    if summary:
        summary_table = Table(title="Blocklist Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="dim", width=20)
        summary_table.add_column("Count", style="dim", width=10)

        summary_table.add_row("Total Lists Checked", str(summary.get("total_lists_checked", 0)))

        listed_count = summary.get("listed_count", 0)
        if listed_count > 0:
            summary_table.add_row("Listed", f"[red]{listed_count}[/red]")
        else:
            summary_table.add_row("Listed", f"[green]{listed_count}[/green]")

        summary_table.add_row("Clean", f"[green]{summary.get('clean_count', 0)}[/green]")

        error_count = summary.get("error_count", 0)
        if error_count > 0:
            summary_table.add_row("Errors", f"[yellow]{error_count}[/yellow]")
        else:
            summary_table.add_row("Errors", str(error_count))

        console.print(summary_table)

    # Display detailed blocklist results
    if blocklist_status:
        detail_table = Table(title="Detailed Blocklist Results", show_header=True, header_style="bold magenta")
        detail_table.add_column("Blocklist", style="dim", width=20)
        detail_table.add_column("Status", style="dim", width=15)
        detail_table.add_column("Description", style="dim", width=40)

        for blocklist_id, status_info in blocklist_status.items():
            name = status_info.get("name", blocklist_id)
            status = status_info.get("status", "Unknown")
            description = status_info.get("description", "")

            # Color code the status
            if status == "Listed":
                status_display = f"[red]{status}[/red]"
            elif status == "Clean":
                status_display = f"[green]{status}[/green]"
            elif status == "Error":
                status_display = f"[yellow]{status}[/yellow]"
            else:
                status_display = status

            detail_table.add_row(name, status_display, description)

        console.print(detail_table)

    if errors:
        console.print(Panel("Errors encountered during Blocklist analysis:", style="red"))
        for error in errors:
            console.print(f"  [red]• {error}[/red]")


def _display_dga_results(console: Console, results: dict, verbose: bool = False):
    """Display DGA analysis results."""
    domain = results.get("domain", "")
    dga_analysis = results.get("dga_analysis", {})
    errors = results.get("errors", [])

    # Create panel for DGA results
    console.print(Panel(f"DGA Analysis for {domain}", style="cyan"))

    if dga_analysis:
        # Create table for DGA analysis
        table = Table(title="DGA Detection Results", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim", width=25)
        table.add_column("Value", style="dim", width=50)

        # Display main classification results
        classification = dga_analysis.get("classification", "Unknown")
        dga_probability = dga_analysis.get("dga_probability", 0.0)
        confidence = dga_analysis.get("confidence", "Unknown")
        risk_level = dga_analysis.get("risk_level", "Unknown")

        # Color code classification based on risk
        if classification == "Likely DGA":
            classification_display = f"[red]{classification}[/red]"
        elif classification == "Suspicious":
            classification_display = f"[yellow]{classification}[/yellow]"
        elif classification == "Possibly Legitimate":
            classification_display = f"[blue]{classification}[/blue]"
        else:
            classification_display = f"[green]{classification}[/green]"

        table.add_row("Classification", classification_display)
        table.add_row("DGA Probability", f"{dga_probability:.3f}")
        table.add_row("Confidence", confidence)

        # Color code risk level
        if risk_level == "High":
            risk_display = f"[red]{risk_level}[/red]"
        elif risk_level == "Medium":
            risk_display = f"[yellow]{risk_level}[/yellow]"
        else:
            risk_display = f"[green]{risk_level}[/green]"

        table.add_row("Risk Level", risk_display)

        console.print(table)

        # Display detailed features if verbose
        if verbose:
            features = dga_analysis.get("features", {})
            if features:
                feature_table = Table(title="Detailed Feature Analysis", show_header=True, header_style="bold magenta")
                feature_table.add_column("Feature", style="dim", width=25)
                feature_table.add_column("Value", style="dim", width=20)

                # Group features for better display
                length_features = ["domain_length", "total_length"]
                entropy_features = ["entropy", "char_frequency_variance"]
                composition_features = ["vowel_ratio", "consonant_ratio", "digit_ratio"]
                pattern_features = ["consecutive_consonants", "consecutive_digits"]
                dictionary_features = ["contains_dictionary_words", "dictionary_word_ratio"]
                structural_features = ["legitimate_tld", "hyphen_count", "underscore_count", "has_special_chars"]

                feature_groups = [
                    ("Length Features", length_features),
                    ("Entropy Features", entropy_features),
                    ("Composition Features", composition_features),
                    ("Pattern Features", pattern_features),
                    ("Dictionary Features", dictionary_features),
                    ("Structural Features", structural_features),
                ]

                for group_name, feature_list in feature_groups:
                    # Add group header
                    feature_table.add_row(f"[bold]{group_name}[/bold]", "")

                    for feature in feature_list:
                        if feature in features:
                            value = features[feature]
                            if isinstance(value, float):
                                value_str = f"{value:.3f}"
                            else:
                                value_str = str(value)
                            feature_table.add_row(f"  {feature.replace('_', ' ').title()}", value_str)

                console.print(feature_table)

    if errors:
        console.print(Panel("Errors encountered during DGA analysis:", style="red"))
        for error in errors:
            console.print(f"  [red]• {error}[/red]")


def _display_llm_summary_results(console: Console, results: dict, verbose: bool = False):
    """Display LLM summary analysis results."""
    domain = results.get("domain", "")
    llm_summary = results.get("llm_summary", {})
    errors = results.get("errors", [])

    # Create panel for LLM summary results
    console.print(Panel(f"LLM Summary for {domain}", style="bright_green"))

    if llm_summary:
        summary_text = llm_summary.get("summary", "")
        model_used = llm_summary.get("model_used", "Unknown")
        analyzers_summarized = llm_summary.get("analyzers_summarized", [])

        # Create main summary display
        if summary_text:
            # Display the summary in a panel
            console.print(Panel(summary_text, title="AI-Generated Summary", style="green"))

        # Display metadata if verbose
        if verbose:
            metadata_table = Table(title="Summary Metadata", show_header=True, header_style="bold magenta")
            metadata_table.add_column("Field", style="dim", width=20)
            metadata_table.add_column("Value", style="dim", width=50)

            metadata_table.add_row("Model Used", model_used)
            metadata_table.add_row("Analyzers Included", ", ".join(analyzers_summarized))

            console.print(metadata_table)

    if errors:
        console.print(Panel("Errors encountered during LLM summary analysis:", style="red"))
        for error in errors:
            console.print(f"  [red]• {error}[/red]")


@app.command()
def version():
    """Show version information."""
    console = Console()
    console.print(f"alexscan version {__version__}")


if __name__ == "__main__":
    app()
