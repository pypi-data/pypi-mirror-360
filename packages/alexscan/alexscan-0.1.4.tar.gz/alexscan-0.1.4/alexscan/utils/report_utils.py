"""Utility functions for report generation and formatting."""

from datetime import datetime
from typing import Any, Dict, Optional, Union


def get_risk_indicator(status: str, format_type: str = "emoji") -> str:
    """Get risk indicator based on status and format type.

    Args:
        status: Status string (safe, warning, critical, unknown, etc.)
        format_type: Type of indicator (emoji, html, markdown, text)

    Returns:
        Formatted risk indicator
    """
    status_lower = status.lower()

    if format_type == "emoji":
        if any(word in status_lower for word in ["safe", "clean", "legitimate", "low"]):
            return "✅"
        elif any(word in status_lower for word in ["warning", "suspicious", "medium"]):
            return "⚠️"
        elif any(word in status_lower for word in ["critical", "malicious", "high", "listed"]):
            return "❌"
        else:
            return "❓"

    elif format_type == "html":
        if any(word in status_lower for word in ["safe", "clean", "legitimate", "low"]):
            return '<span class="status-safe">✅ Safe</span>'
        elif any(word in status_lower for word in ["warning", "suspicious", "medium"]):
            return '<span class="status-warning">⚠️ Warning</span>'
        elif any(word in status_lower for word in ["critical", "malicious", "high", "listed"]):
            return '<span class="status-critical">❌ Critical</span>'
        else:
            return '<span class="status-unknown">❓ Unknown</span>'

    elif format_type == "markdown":
        if any(word in status_lower for word in ["safe", "clean", "legitimate", "low"]):
            return "✅ **Safe**"
        elif any(word in status_lower for word in ["warning", "suspicious", "medium"]):
            return "⚠️ **Warning**"
        elif any(word in status_lower for word in ["critical", "malicious", "high", "listed"]):
            return "❌ **Critical**"
        else:
            return "❓ **Unknown**"

    else:  # text
        if any(word in status_lower for word in ["safe", "clean", "legitimate", "low"]):
            return "SAFE"
        elif any(word in status_lower for word in ["warning", "suspicious", "medium"]):
            return "WARNING"
        elif any(word in status_lower for word in ["critical", "malicious", "high", "listed"]):
            return "CRITICAL"
        else:
            return "UNKNOWN"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format timestamp for reports."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."  # noqa


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def get_section_icon(section_name: str) -> str:
    """Get emoji icon for different analysis sections."""
    icons = {
        "dns": "🌐",
        "whois": "📋",
        "ssl": "🔒",
        "blocklist": "🛡️",
        "dga": "🤖",
        "crawler": "🕷️",
        "llm_summary": "🧠",
        "summary": "📊",
        "executive": "📈",
    }
    return icons.get(section_name.lower(), "📄")


def calculate_overall_risk_score(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall risk score based on all analysis results."""
    risk_factors = []

    # DNS Risk Factors
    if "dns" in results and "records" in results["dns"]:
        dns_records = results["dns"]["records"]
        if not dns_records.get("A", {}).get("values", []):
            risk_factors.append(("No A records found", 30))
        if not dns_records.get("MX", {}).get("values", []):
            risk_factors.append(("No MX records found", 10))

    # SSL Risk Factors
    if "ssl" in results and "ssl_data" in results["ssl"]:
        ssl_data = results["ssl"]["ssl_data"]
        if ssl_data.get("is_expired"):
            risk_factors.append(("SSL certificate expired", 50))
        days_until_expiry = ssl_data.get("days_until_expiry", 365)
        if isinstance(days_until_expiry, int) and days_until_expiry < 30:
            risk_factors.append(("SSL certificate expires soon", 25))

    # Blocklist Risk Factors
    if "blocklist" in results and "summary" in results["blocklist"]:
        blocklist_summary = results["blocklist"]["summary"]
        listed_count = blocklist_summary.get("listed_count", 0)
        if listed_count > 0:
            risk_factors.append((f"Listed on {listed_count} blocklists", listed_count * 20))

    # DGA Risk Factors
    if "dga" in results and "dga_analysis" in results["dga"]:
        dga_analysis = results["dga"]["dga_analysis"]
        dga_prob = dga_analysis.get("dga_probability", 0)
        if dga_prob > 0.7:
            risk_factors.append(("High DGA probability", 40))
        elif dga_prob > 0.5:
            risk_factors.append(("Medium DGA probability", 25))

    # Calculate total risk score
    total_risk = min(sum(factor[1] for factor in risk_factors), 100)

    # Determine risk level
    if total_risk >= 70:
        risk_level = "High"
        risk_color = "critical"
    elif total_risk >= 40:
        risk_level = "Medium"
        risk_color = "warning"
    else:
        risk_level = "Low"
        risk_color = "safe"

    return {
        "score": total_risk,
        "level": risk_level,
        "color": risk_color,
        "factors": risk_factors,
        "indicator": get_risk_indicator(risk_level, "emoji"),
    }


def generate_executive_summary(results: Dict[str, Any]) -> str:
    """Generate executive summary from analysis results."""
    domain = results.get("domain", "unknown")
    risk_assessment = calculate_overall_risk_score(results)

    summary_parts = [
        f"Domain {domain} has been analyzed with an overall risk score of {risk_assessment['score']}/100 ({risk_assessment['level']} risk)."
    ]

    # Add key findings
    findings = []

    if "dns" in results:
        dns_records = results["dns"].get("records", {})
        record_count = sum(len(records.get("values", [])) for records in dns_records.values())
        findings.append(f"{record_count} DNS records found")

    if "ssl" in results and results["ssl"].get("ssl_data"):
        ssl_data = results["ssl"]["ssl_data"]
        if ssl_data.get("is_expired"):
            findings.append("SSL certificate is expired")
        else:
            findings.append("Valid SSL certificate present")

    if "blocklist" in results:
        blocklist_summary = results["blocklist"].get("summary", {})
        listed_count = blocklist_summary.get("listed_count", 0)
        total_lists = blocklist_summary.get("total_lists_checked", 0)
        if listed_count > 0:
            findings.append(f"Listed on {listed_count}/{total_lists} blocklists")
        else:
            findings.append(f"Clean on all {total_lists} blocklists checked")

    if "crawler" in results:
        crawl_data = results["crawler"].get("crawl_data", {})
        pages_crawled = crawl_data.get("pages_crawled", 0)
        if pages_crawled > 0:
            findings.append(f"{pages_crawled} pages crawled successfully")

    if findings:
        summary_parts.append(" Key findings include: " + ", ".join(findings) + ".")

    # Add recommendations
    if risk_assessment["score"] >= 70:
        summary_parts.append(" Immediate attention recommended due to high-risk indicators.")
    elif risk_assessment["score"] >= 40:
        summary_parts.append(" Further investigation suggested due to moderate risk factors.")
    else:
        summary_parts.append(" Domain appears to be operating normally with minimal risk indicators.")

    return "".join(summary_parts)


def create_stats_summary(results: Dict[str, Any]) -> Dict[str, Union[int, str]]:
    """Create statistics summary for dashboard-style display."""
    stats = {}

    # Count analyzers run
    analyzer_count = 0
    for key in ["dns", "whois", "ssl", "blocklist", "dga", "crawler", "llm_summary"]:
        if key in results and results[key]:
            analyzer_count += 1
    stats["Analyzers Run"] = analyzer_count

    # DNS stats
    if "dns" in results and "records" in results["dns"]:
        dns_records = results["dns"]["records"]
        record_count = sum(len(records.get("values", [])) for records in dns_records.values())
        stats["DNS Records"] = record_count

    # SSL stats
    if "ssl" in results and "ssl_data" in results["ssl"]:
        ssl_data = results["ssl"]["ssl_data"]
        if ssl_data:
            stats["SSL Certificates"] = 1
            if ssl_data.get("days_until_expiry"):
                stats["SSL Expiry (days)"] = ssl_data["days_until_expiry"]

    # Blocklist stats
    if "blocklist" in results and "summary" in results["blocklist"]:
        blocklist_summary = results["blocklist"]["summary"]
        stats["Blocklists Checked"] = blocklist_summary.get("total_lists_checked", 0)
        stats["Blocklist Hits"] = blocklist_summary.get("listed_count", 0)

    # Crawler stats
    if "crawler" in results and "crawl_data" in results["crawler"]:
        crawl_data = results["crawler"]["crawl_data"]
        stats["Pages Crawled"] = crawl_data.get("pages_crawled", 0)
        stats["Links Found"] = crawl_data.get("total_links", 0)
        stats["Emails Found"] = len(crawl_data.get("emails", []))

    # DGA stats
    if "dga" in results and "dga_analysis" in results["dga"]:
        dga_analysis = results["dga"]["dga_analysis"]
        dga_prob = dga_analysis.get("dga_probability", 0)
        stats["DGA Probability"] = f"{dga_prob:.1%}"

    return stats
