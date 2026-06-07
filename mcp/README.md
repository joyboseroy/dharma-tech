# Dharma MCP Server

A self-contained MCP server built from scratch using raw JSON-RPC over stdio.

**No Anthropic SDK. No Claude API. No cloud. Your data stays on your machine.**

Uses only:
- **Ollama** — local LLM (qwen2.5:7b or any model you have)
- **FalkorDB** — local graph database (optional)
- **Standard Python** — json, sys, pathlib

Works with any MCP-compatible client: Claude Desktop, Cursor, or any client that speaks JSON-RPC over stdio.

## How it works

```
Your MCP client (e.g. Claude Desktop)
        |
        | JSON-RPC over stdio
        v
dharma_mcp_server.py    ← runs on your machine
        |
        | calls locally
        v
Ollama (qwen2.5:7b)     ← your local LLM
data/ JSONL files       ← your local graph data
```

The client (Claude Desktop etc) connects to your server. Your server uses Ollama internally. Nothing goes to the cloud.

## Setup

```bash
# 1. Install Ollama: https://ollama.com
ollama pull qwen2.5:7b
ollama serve   # keep running in a terminal

# 2. Install Python dependency (only one)
pip install ollama requests

# 3. Test it works
python dharma_mcp_server.py --cli
```

## Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "dharma-tech": {
      "command": "python",
      "args": ["/absolute/path/to/dharma-tech/mcp/dharma_mcp_server.py"]
    }
  }
}
```

Windows: `%APPDATA%\Claude\claude_desktop_config.json`
Linux: `~/.config/claude/claude_desktop_config.json`

Restart Claude Desktop. The tools appear automatically.

## Environment variables

```bash
export DHARMA_MODEL="llama3.2:3b"    # use a different Ollama model
export OLLAMA_URL="http://localhost:11434"  # default
```

## Tools exposed (9)

| Tool | Description | Needs Ollama |
|------|-------------|:---:|
| `query_concept` | Get a concept with all philosophical edges | No |
| `find_path` | Shortest path between two concepts | No |
| `get_tensions` | All live doctrinal tensions | No |
| `retrieve_passages` | Text passages for a concept | No |
| `tradition_compare` | Cross-tradition comparison | No |
| `identify_hindrance` | Map experience to five hindrances | Yes |
| `verify_quote` | Check if quote is canonical | Yes |
| `find_free_text` | Find free sources for any Buddhist text | Optional |
| `daily_reflection` | Today's passage and lojong slogan | No |

The graph-based tools (query, path, tensions, passages, compare) work entirely from local JSONL files — no Ollama needed.

## Test without a client

```bash
python dharma_mcp_server.py --cli
```

→ [Back to main repo](../README.md)
