# Remote MCP Scanner

A comprehensive security scanner for remote MCP (Model Context Protocol) servers that tests for OAuth dynamic client registration vulnerabilities.

## Features

- **OAuth Well-Known Endpoint Discovery** - Automatically discovers OAuth authorization server configurations
- **Dynamic Client Registration Testing** - Tests OAuth client registration endpoints for security issues
- **Comprehensive XSS Testing** - Tests both `redirect_uri` and `website_uri` fields with 60+ XSS payloads
- **Manual Testing URLs** - Generates ready-to-use URLs for manual vulnerability verification
- **Colorized Output** - Easy-to-read colored console output with clear vulnerability reporting
- **Multiple Attack Vectors** - JavaScript, Data URIs, HTML injection, encoding bypasses, and more

## Installation

### From PyPI (Recommended)

```bash
pip install remote-mcp-scanner
```

### From Source

```bash
git clone https://github.com/novasecuritynz/remote-mcp-scanner
cd remote-mcp-scanner
pip install -e .
```

## Usage

### Command Line

```bash
# Basic scan
mcp-scanner https://mcp-server.example.com

# Verbose output
mcp-scanner https://mcp-server.example.com --verbose

# Alternative command name
remote-mcp-scanner https://mcp-server.example.com
```

### Python API

```python
from remote_mcp_scanner import run_scan

# Run a scan programmatically
oauth_configs = run_scan("https://mcp-server.example.com", verbose=True)
print(f"Found OAuth configs: {oauth_configs}")
```

## What It Tests

### 1. OAuth Well-Known Endpoints
- `/.well-known/oauth-protected-resource`
- `/.well-known/oauth-authorization-server`
- Tests both full MCP path and base domain

### 2. Dynamic Client Registration
- Tests client registration with standard OAuth payload
- Verifies registration endpoint accessibility
- Captures client credentials for further testing

### 3. Redirect URI Validation
Tests 40+ attack vectors including:
- **JavaScript Execution**: `javascript:alert('XSS')`
- **Data URIs**: `data:text/html,<script>alert('XSS')</script>`
- **Protocol Bypasses**: VBScript, File, FTP protocols
- **Domain Confusion**: Authority bypasses, subdomain tricks
- **Encoding Bypasses**: URL encoding, HTML entities, null bytes

### 4. Website URI XSS Testing
Tests 60+ attack vectors including:
- **Advanced JavaScript**: Function constructors, bracket notation
- **HTML Injection**: Event handlers, form actions, meta redirects
- **Template Injection**: Multiple template engine syntaxes
- **Polyglot Payloads**: Multi-context XSS vectors
- **CSS Injection**: Expression-based attacks

## Output Example

```
🔗 REDIRECT_URI XSS MANUAL TESTING:
📋 INSTRUCTIONS: Complete the full OAuth flow to test XSS:
1. Click the URL below in your browser
2. Complete any login/authorization steps
3. Watch for JavaScript execution during redirect
4. Check browser console and network tabs for XSS

🚨 REDIRECT_URI XSS Test (JavaScript schema XSS):
   Client ID: abc123
   Payload: javascript://domain.com/%0aalert(1);//
   Test URL: https://oauth.example.com/authorize?response_type=code&client_id=abc123&redirect_uri=javascript%3A//domain.com/%250aalert%281%29%3B//&state=xss_test_redirect

=== REDIRECT URI VALIDATION SUMMARY ===
🚨 XSS RISKS FOUND:
  • javascript://domain.com/%0aalert(1);// - JavaScript schema XSS
  → These redirect URIs can lead to XSS attacks!

📊 Total bypasses found: 5/40
```

## Security Features

- **Defensive Purpose Only** - Designed for legitimate security testing
- **Comprehensive Reporting** - Detailed vulnerability categorization
- **Manual Verification** - Provides URLs for manual testing confirmation
- **Professional Output** - Clear, actionable security findings

## Requirements

- Python 3.8+
- httpx
- click
- beautifulsoup4

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Disclaimer

This tool is intended for authorized security testing only. Users are responsible for ensuring they have proper permission before testing any systems.

## Support

- **Issues**: [GitHub Issues](https://github.com/novasecuritynz/remote-mcp-scanner/issues)
- **Email**: info@novasecurity.co.nz
- **Website**: [Nova Security](https://www.novasecurity.co.nz)