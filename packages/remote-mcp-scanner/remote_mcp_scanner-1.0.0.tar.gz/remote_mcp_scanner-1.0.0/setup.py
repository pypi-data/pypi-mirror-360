from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="remote-mcp-scanner",
    version="1.0.0",
    author="Nova Security",
    author_email="info@novasecurity.co.nz",
    description="A security scanner for remote MCP (Model Context Protocol) servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/novasecuritynz/remote-mcp-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology", 
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcp-scanner=remote_mcp_scanner.cli:cli",
            "remote-mcp-scanner=remote_mcp_scanner.cli:cli",
        ],
    },
    keywords="security, oauth, mcp, scanner, vulnerability, xss, penetration-testing",
    project_urls={
        "Bug Reports": "https://github.com/novasecuritynz/remote-mcp-scanner/issues",
        "Source": "https://github.com/novasecuritynz/remote-mcp-scanner",
        "Documentation": "https://github.com/novasecuritynz/remote-mcp-scanner#readme",
    },
)