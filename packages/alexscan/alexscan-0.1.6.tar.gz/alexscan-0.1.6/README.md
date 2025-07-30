# AlexScan - Domain Security Analyzer

[![CI/CD Pipeline](https://github.com/alexevan13/domain-analyzer/workflows/Pytest%20Test%20Suite/badge.svg)](https://github.com/alexevan13/domain-analyzer/actions)
[![Version](https://img.shields.io/badge/version-LATEST-blue.svg)](https://github.com/alexevan13/domain-analyzer/releases)
[![PyPI version](https://badge.fury.io/py/alexscan.svg)](https://badge.fury.io/py/alexscan)
[![PyPI downloads](https://img.shields.io/pypi/dm/alexscan.svg)](https://pypi.org/project/alexscan/)
[![Python versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: flake8](https://img.shields.io/badge/linting-flake8-yellowgreen)](https://flake8.pycqa.org/)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/alexevan13/domain-analyzer/graphs/commit-activity)
[![GitHub stars](https://img.shields.io/github/stars/alexevan13/domain-analyzer.svg?style=social&label=Star)](https://github.com/alexevan13/domain-analyzer)
[![GitHub forks](https://img.shields.io/github/forks/alexevan13/domain-analyzer.svg?style=social&label=Fork)](https://github.com/alexevan13/domain-analyzer)

A comprehensive domain security analysis tool that combines multiple analyzers to assess domain safety and provide detailed security insights.

## Features

- **DNS Analysis**: Comprehensive DNS record analysis and security assessment
- **WHOIS Analysis**: Domain registration information and age analysis
- **SSL/TLS Analysis**: Certificate validation and security assessment
- **Blocklist Analysis**: Check domain against multiple security blocklists
- **Whitelist Analysis**: Verify domain against trusted whitelists
- **DGA Detection**: Domain Generation Algorithm detection for malicious domains
- **HTTP Security Headers**: Analyze web server security headers
- **Web Crawler**: Extract and analyze website content
- **Port Scanning**: Scan open ports and detect vulnerabilities
- **Screenshot Generation**: Visual verification of domains
- **AI-Powered Summary**: LLM-based analysis and recommendations
- **🔍 Domain Categorization**: LLM-powered content categorization with detailed taxonomy
- **🔒 Domain Safety Rating**: Comprehensive safety scoring algorithm

## Domain Safety Rating System

AlexScan includes a sophisticated safety rating algorithm that provides a comprehensive assessment of domain security:

### Safety Score Calculation
- Each analyzer computes a **score between 0-10** based on its analysis
- Overall safety rating: **(Sum of all analyzer scores) ÷ (Number of analyzers run)**
- Results in a percentage score from 0-100%

### Classification Thresholds
- **70–100% (7.0-10.0)**: ✅ Safe
- **50–70% (5.0-7.0)**: ⚠️ Likely Unsafe
- **30–50% (3.0-5.0)**: ❌ Likely Malicious
- **0–30% (0.0-3.0)**: ❌ Unsafe (high risk)

### Component Scoring
Each analyzer contributes to the overall safety rating:

- **DNS Analyzer**: Based on DNSSEC presence, essential records, security records (SPF, DMARC)
- **WHOIS Analyzer**: Domain age, registrar reputation, organization information
- **SSL Analyzer**: Certificate validity, expiration, issuer reputation, cipher strength
- **Blocklist Analyzer**: Percentage of security lists that flag the domain
- **Whitelist Analyzer**: Percentage of trusted lists that whitelist the domain
- **DGA Analyzer**: Domain generation algorithm detection probability
- **Headers Analyzer**: Security header implementation score
- **Crawler Analyzer**: Content analysis and suspicious patterns
- **Port Scanner**: Open ports assessment and vulnerability detection

## Installation

### Prerequisites
- Python 3.9, 3.10, or 3.11
- Redis server (for caching)
- Ollama (for LLM analysis)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd domain-analyzer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install .

# Initialize environment
alexscan init
```

## Usage

### Basic Analysis
```bash
# Run all analyzers and compute safety rating
alexscan analyze example.com --all

# Run specific analyzers
alexscan analyze example.com --dns --whois --ssl

# Run domain categorization only
alexscan analyze example.com --categorize

# Run port scanning only
alexscan analyze example.com --ports

# Generate markdown report
alexscan analyze example.com --all --report
```

### Safety Rating Output
The CLI displays a comprehensive safety assessment:
```
================================================================================
┌─ Domain Safety Assessment ──────────────────────────────────────────────────┐
│ 🔒 Overall Domain Safety Rating                                             │
│ Safety Score: 7.8/10 (78.0%)                                               │
│ Classification: ✅ Safe                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ Component Safety Scores ───────────────────────────────────────────────────┐
│ Analyzer        │ Score │
│─────────────────│───────│
│ Dns             │ 8.5   │
│ Whois           │ 7.2   │
│ Ssl             │ 9.1   │
│ Blocklist       │ 10.0  │
│ Whitelist       │ 6.5   │
│ Dga             │ 8.0   │
│ Headers         │ 7.5   │
│ Ports           │ 6.8   │
└─────────────────│───────┘
================================================================================
```

### Cache Management
```bash
# Show cache statistics
alexscan cache stats

# Clear all cached results
alexscan cache clear

# Invalidate cache for specific domain
alexscan cache invalidate --domain example.com
```

## Analyzers

### DNS Analyzer
Analyzes DNS records for security indicators:
- A, AAAA, MX, NS, TXT records
- SPF and DMARC presence
- DNSSEC implementation
- IPv6 support

### WHOIS Analyzer
Examines domain registration information:
- Domain age and creation date
- Registrar reputation
- Organization information
- Privacy protection status

### SSL/TLS Analyzer
Validates SSL certificate security:
- Certificate validity and expiration
- Issuer reputation
- Cipher strength
- Wildcard certificate detection

### Blocklist Analyzer
Checks domain against security blocklists:
- Multiple blocklist sources
- Listing percentage calculation
- Detailed status reporting

### Whitelist Analyzer
Verifies domain against trusted lists:
- Trusted domain verification
- Whitelist percentage calculation
- Reputation assessment

### DGA Analyzer
Detects Domain Generation Algorithms:
- Machine learning-based detection
- Probability scoring
- Risk level assessment

### HTTP Headers Analyzer
Analyzes web server security headers:
- Security header implementation
- Missing critical headers
- Configuration assessment

### Port Scanner
Scans for open ports and vulnerabilities:
- Common port scanning
- Service version detection
- Vulnerability assessment
- Web-based vulnerability lookups

### Web Crawler
Extracts and analyzes website content:
- Content analysis
- Form detection
- External link analysis
- Suspicious pattern detection

### Screenshot Analyzer
Generates visual verification:
- Website screenshots
- Visual domain verification

### LLM Summary Analyzer
AI-powered analysis and recommendations:
- Comprehensive domain assessment
- Risk-based recommendations
- Security insights

### Domain Categorization Analyzer
LLM-powered content categorization with detailed taxonomy:
- **11 Primary Categories**: News/Media, Social Media, E-commerce, Technology, etc.
- **60+ Subcategories**: Detailed classification within each primary category
- **Confidence Scoring**: 0-100% confidence in classification
- **Evidence-Based**: Clear rationale for classification decisions
- **Configurable Taxonomy**: Easily extensible and updatable
- **HTML Content Analysis**: Analyzes title, meta tags, visible text, and platform markers
- **Uncategorized Handling**: Labels domains with <50% confidence as "Uncategorized"

**Classification Categories:**
1. **News/Media** - General News, Politics, Technology News, Sports, etc.
2. **Social Media & Communities** - Social Networks, Forums, Gaming Communities, etc.
3. **E-commerce & Shopping** - Retail, Electronics, Fashion, Marketplaces, etc.
4. **Adult Content** - Adult entertainment and related content
5. **Gambling** - Online casinos, sports betting, lottery sites
6. **Technology** - Developer Tools, IT Services, SaaS Platforms, etc.
7. **Blogs & Personal Websites** - Lifestyle, Travel, Technical blogs, etc.
8. **Education & Reference** - Universities, Online Learning, Libraries, etc.
9. **Government & Law** - Government portals, Legal sites, Military, etc.
10. **Finance & Business** - Banking, Investment, Cryptocurrency, etc.
11. **Other/Miscellaneous** - Parked domains, CDNs, Search engines, etc.

## Configuration

### Environment Variables
```bash
# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Ollama configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Cache configuration
CACHE_TTL=3600  # 1 hour
MAX_CACHE_SIZE=1000
```

## Report Generation

AlexScan generates comprehensive Markdown reports including:

- **Overall Domain Safety Rating** with component scores
- **Executive Summary** with AI-powered insights
- **Detailed Analysis** from each analyzer
- **Security Recommendations** based on findings
- **Visual Evidence** (screenshots, when enabled)

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_safety_rating.py

# Run with coverage
python -m pytest --cov=alexscan
```

### Adding New Analyzers
1. Create analyzer class inheriting from `BaseAnalyzer`
2. Implement `analyze()` method
3. Add safety scoring logic to `SafetyRatingCalculator`
4. Update CLI and report generator
5. Add comprehensive tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

- AlexScan is designed for security analysis and should be used responsibly
- Always respect rate limits and terms of service for external APIs
- Use in accordance with applicable laws and regulations
- Report security vulnerabilities to the maintainers

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation
- Review existing discussions

## Release Notes

### [LATEST]
- Enhanced domain analysis capabilities
- Improved classification and categorization
- Better DGA detection with LLM reasoning
- Updated CI/CD pipeline with auto-versioning
- Enhanced test coverage
- Better error handling and reporting
- Fixed various edge cases in domain analysis
- Improved reliability of screenshot generation

### [v0.1.1] - 2024-01-XX
- Initial release with comprehensive domain analysis
- DNS, WHOIS, SSL/TLS analysis
- Blocklist and whitelist checking
- DGA detection with entropy analysis
- HTTP security headers analysis
- Port scanning capabilities
- Web crawling and content analysis
- Screenshot generation
- LLM-powered summary and recommendations
- Domain categorization with hierarchical taxonomy
- Safety rating algorithm
- Markdown report generation
- PDF report export functionality
- Cache management system
