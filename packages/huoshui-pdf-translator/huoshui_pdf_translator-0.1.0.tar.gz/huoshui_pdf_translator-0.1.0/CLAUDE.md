# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Server
```bash
# Development mode
uv run python main.py

# Install dependencies
uv sync

# Install with development dependencies
uv sync --group dev
```

### Code Quality
```bash
# Format code
black main.py

# Lint code
ruff check main.py

# Run tests (if available)
pytest

# Check external tool dependency
pmt --version
```

### Dependencies
- Requires Python 3.12+
- External dependency: `pmt` command (PDFMathTranslate-next)
- Install with: `pip install pdf-math-translate-next`

## Architecture Overview

This is a FastMCP-based PDF translation server that acts as an MCP (Model Context Protocol) server providing PDF translation capabilities through the PDFMathTranslate-next engine.

### Core Components

**FastMCP Server (`main.py`)**: Single-file MCP server implementation with:
- **Tools**: `translate_pdf`, `pdf_get`, `check_translation_tool`
- **Resources**: `translation_capability_list`
- **Prompts**: 5 specialized prompts for different user scenarios
- **Data Models**: `PDFResource`, `TranslationCapability`

### Key Design Patterns

**Path Handling**: Flexible path resolution supporting both absolute and relative paths. Relative paths are resolved against the user's home directory. Security restrictions prevent access to system directories.

**Error Handling**: Comprehensive error handling with specific error codes and user-friendly messages. Tool errors are wrapped in `ToolError` with appropriate HTTP-like status codes.

**Progress Reporting**: Async progress reporting during translation operations using FastMCP's context system.

**External Tool Integration**: Subprocess-based integration with the `pmt` command-line tool, including proper timeout handling and error capture.

### File Structure
- `main.py`: Complete MCP server implementation
- `pyproject.toml`: Python project configuration with UV package management
- `manifest.json`: MCP manifest describing server capabilities
- `uv.lock`: Dependency lock file

### Translation Workflow
1. Path validation and security checking
2. PDF file validation and info extraction
3. External tool (`pmt`) execution with progress reporting
4. Output file verification
5. Result reporting with timing information

### Security Features
- Path sanitization to prevent access to system directories
- File size limits (200MB max)
- Timeout protection for external tool execution (15 minutes)
- Input validation for all user-provided paths

### Performance and Timeout Handling
- **First Run**: May take 2-5 minutes due to font/model downloads
- **Subsequent Runs**: Much faster as assets are cached
- **Warmup Tool**: Use `warm_up_translator` before first translation
- **Progress Reporting**: Real-time updates every 5 seconds during translation
- **Timeout Limits**: 15 minutes for translation, 5 minutes for warmup

### Troubleshooting MCP Client Timeouts
1. **Run warmup first**: Call `warm_up_translator` tool before translation
2. **Check network**: Fonts download from internet on first use
3. **Be patient**: First translation downloads ~50MB of fonts and models
4. **Cache location**: Assets cached in `~/.cache/babeldoc/`

## Development Experiences

### Recent Reflections
- Successfully integrated FastMCP with PDF translation tool, demonstrating robust external tool integration
- Implemented comprehensive error handling and security features for file-based operations
- Developed async progress reporting mechanism to enhance user experience during long-running translations