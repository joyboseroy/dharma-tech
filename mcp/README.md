# Dharma MCP Server + Client

A self-contained MCP server and command-line client built from scratch.

**No LLM SDKs like Gemini or Claude. No cloud. Runs entirely in your WSL terminal.**

Uses only:
- **Ollama** — local LLM (qwen2.5:7b or any model you have)
- **Standard Python** — json, sys, subprocess, pathlib

## How it works

```
WSL terminal
     |
     | python mcp/client.py
     v
client.py            ← JSON-RPC client (runs in WSL)
     |
     | stdin/stdout JSON-RPC (subprocess)
     v
dharma_mcp_server.py ← MCP server (runs in WSL)
     |
     | calls locally
     v
Ollama (qwen2.5:7b)  ← local LLM, no internet
data/ JSONL files    ← local graph data
```

`client.py` starts the server as a subprocess and talks to it via JSON-RPC stdio.
Everything runs inside WSL. Nothing leaves your machine.

## Setup

```bash
# 1. Install Ollama for Linux/WSL: https://ollama.com/download/linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
ollama serve          # keep running in a separate WSL terminal

# 2. Install Python dependencies
pip install ollama requests

# 3. Run
cd ~/dharma-tech
python mcp/client.py  # interactive mode
```

## Usage

```bash
# Interactive — type tool names and parameters
python mcp/client.py

# Single commands
python mcp/client.py query_concept sunyata
python mcp/client.py find_path anatta sunyata
python mcp/client.py get_tensions
python mcp/client.py tradition_compare consciousness
python mcp/client.py retrieve_passages sunyata 5
python mcp/client.py verify_quote "The mind is everything"
python mcp/client.py identify_hindrance "my mind keeps jumping to plans"
python mcp/client.py find_free_text "Heart Sutra"
python mcp/client.py daily_reflection
```

## Environment variables

```bash
export DHARMA_MODEL="llama3.2:3b"        # use a different Ollama model
export OLLAMA_URL="http://localhost:11434" # default
```

## Tools (9)

| Tool | Needs Ollama | Description |
|------|:---:|-------------|
| `query_concept` | No | Get a concept with all philosophical edges |
| `find_path` | No | Shortest path between two concepts |
| `get_tensions` | No | All live doctrinal tensions |
| `retrieve_passages` | No | Text passages for a concept |
| `tradition_compare` | No | Cross-tradition comparison |
| `identify_hindrance` | Yes | Map meditation experience to five hindrances |
| `verify_quote` | Yes | Check if a quote is actually canonical |
| `find_free_text` | Optional | Find free sources for any Buddhist text |
| `daily_reflection` | No | Today's passage and lojong slogan |

The 5 graph tools work from local JSONL files — no Ollama needed at all.

## How MCP works (for the curious)

MCP is JSON-RPC over stdin/stdout. Three message types:

```
initialize    → server returns its capabilities
tools/list    → server returns list of available tools
tools/call    → server runs a tool and returns the result
```

`client.py` implements the client side in ~150 lines of standard Python.
`dharma_mcp_server.py` implements the server side. No SDK, no framework.

→ [Back to main repo](../README.md)
