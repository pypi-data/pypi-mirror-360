# Semantic Scholar MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

Access millions of academic papers from Semantic Scholar using the Model Context Protocol (MCP). Works with Claude Code, Claude Desktop, Cursor, VS Code, and other MCP-compatible editors.

## Features

- **Smart Search**: Search papers with filters for year, fields of study, and sorting
- **Full Paper Details**: Get abstracts, authors, citations, and references
- **Author Profiles**: Explore researcher profiles and their publications
- **Citation Network**: Analyze citation relationships and impact
- **AI-Powered**: Get paper recommendations and research insights
- **Fast & Reliable**: Built-in caching, rate limiting, and error recovery

## Installation

### One-Command Setup

**Claude Code** (recommended):
```bash
claude mcp add semantic-scholar -- uvx semantic-scholar-mcp
```

**Or run directly**:
```bash
uvx semantic-scholar-mcp
```

### Alternative Installation Methods

```bash
# Install globally with uv
uv tool install semantic-scholar-mcp

# Or with pip  
pip install semantic-scholar-mcp
```

### Manual Configuration (if needed)

Basic setup:
```json
{
  "mcpServers": {
    "semantic-scholar": {
      "command": "uvx",
      "args": ["semantic-scholar-mcp"]
    }
  }
}
```

With API key for higher limits:
```json
{
  "mcpServers": {
    "semantic-scholar": {
      "command": "uvx",
      "args": ["semantic-scholar-mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Get your free API key at: https://www.semanticscholar.org/product/api

## Usage

Ask in natural language:
- *"Find recent papers on transformer architectures in NLP"*
- *"Show me the paper 'Attention is All You Need'"*
- *"Find papers by Yoshua Bengio"*  
- *"Help me create a literature review on quantum computing"*
- *"Analyze the impact of BERT paper through its citations"*

## Available Tools

| Tool                   | Description                          |
| ---------------------- | ------------------------------------ |
| `search_papers`        | Search papers with advanced filters  |
| `get_paper`            | Get detailed paper information       |
| `get_paper_citations`  | Retrieve papers citing a given paper |
| `get_paper_references` | Get references from a paper          |
| `search_authors`       | Search for researchers               |
| `get_author`           | Get author profile details           |
| `get_author_papers`    | List papers by an author             |
| `get_recommendations`  | Get AI-powered paper recommendations |
| `batch_get_papers`     | Fetch multiple papers efficiently    |

## Advanced Features

### Resources
- `papers/{paper_id}` - Direct access to paper data
- `authors/{author_id}` - Direct access to author profiles

### AI Prompts
- `literature_review` - Generate comprehensive literature reviews
- `citation_analysis` - Analyze citation networks and impact
- `research_trend_analysis` - Identify emerging research trends

## Development

### Setup

```bash
git clone https://github.com/hy20191108/semantic-scholar-mcp.git
cd semantic-scholar-mcp
uv sync
```

### Testing

```bash
# Run tests
uv run pytest

# Test MCP server
uv run python test_simple_search.py

# Use MCP Inspector
uv run mcp dev server_standalone.py
```

### Build

```bash
uv build
```

## Architecture

Built with enterprise-grade patterns:
- **Resilience**: Circuit breaker pattern for fault tolerance
- **Performance**: In-memory LRU caching with TTL
- **Reliability**: Exponential backoff with jitter for retries
- **Observability**: Structured logging with correlation IDs
- **Type Safety**: Full type hints with Pydantic models

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Semantic Scholar](https://www.semanticscholar.org/) for the academic graph API
- [Anthropic](https://www.anthropic.com/) for the MCP specification
- The academic community for making research accessible

---

Built for researchers worldwide