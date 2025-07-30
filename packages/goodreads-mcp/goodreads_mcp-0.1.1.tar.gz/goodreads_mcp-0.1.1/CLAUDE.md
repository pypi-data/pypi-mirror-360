# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI tool for Goodreads MCP (Model Context Protocol) integration, currently in early development (v0.1.0, Alpha status).

## Development Commands

### Setup Development Environment
```bash
# Clone and install in development mode
git clone https://github.com/gather-engineering/goodreads-mcp.git
cd goodreads-mcp
pip install -e .
```

### Build and Package
```bash
# Build distribution packages
python -m build
```

### Install Locally
```bash
# Using pip
pip install .

# Using pipx (recommended for CLI tools)
pipx install .
```

### Run the CLI
```bash
goodreads-mcp
```

## Project Architecture

This is a Python package with minimal structure:
- **goodreads_mcp/**: Main package directory
  - `cli.py`: Entry point for the CLI tool (main function)
  - `__init__.py`: Package initialization
- **pyproject.toml**: Modern Python project configuration using hatchling build system
- Requires Python 3.13 or higher

## Current Implementation Status

The project is in initial stages with:
- Basic CLI structure that prints "Hello from goodreads-mcp!"
- Proper packaging setup for pip/pipx installation
- No dependencies currently installed

## Planned Features (from TODO.md)

1. ✅ Installable via pipx (completed)
2. ⬜ Goodreads CLI functionality (using production server & local)
3. ⬜ Goodreads MCP integration (using production server & local)

## Important Notes

- The project uses modern Python packaging standards (PEP 517/518)
- No testing framework is currently set up
- The main functionality for Goodreads integration is yet to be implemented