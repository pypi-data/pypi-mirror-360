# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based security scanner for remote MCP (Model Context Protocol) servers. The tool performs defensive security testing to identify common vulnerabilities in MCP server implementations.

## Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Scanner
```bash
python cli.py TARGET_URL [--verbose]
```

## Architecture

The codebase follows a simple modular structure:

- `cli.py` - Command-line interface using Click framework
- `scanner.py` - Core scanning logic with individual test functions
- `utils/http.py` - HTTP utility functions for making requests

### Key Components

**Scanner Module** (`scanner.py`):
- `run_scan()` - Main orchestration function that executes all tests
- Individual test functions for specific vulnerability classes:
  - `test_dynamic_registration()` - Tests OAuth client registration
  - `test_redirect_uri_validation()` - Tests redirect URI bypass techniques
  - `test_csrf_flow()` - Placeholder for CSRF testing
  - `test_xss_in_website_uri()` - Tests for stored XSS vulnerabilities

**HTTP Utilities** (`utils/http.py`):
- `post_json()` - POST requests with JSON payloads using httpx
- `get_text()` - GET requests returning text content using httpx
- `get_json()` - GET requests using requests library (mixed usage)

### Dependencies

- `httpx` - Modern HTTP client for async/sync requests
- `click` - Command-line interface framework
- `beautifulsoup4` - HTML parsing (imported but not actively used)
- `requests` - HTTP library (used alongside httpx)

## Security Focus

This tool is designed for defensive security testing only. It identifies common OAuth and web application vulnerabilities in MCP server implementations through controlled testing scenarios.