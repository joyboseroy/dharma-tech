#!/usr/bin/env python3
"""
mcp/client.py

Command-line MCP client for dharma-tech.
Runs entirely in WSL/Linux terminal. No Claude. No cloud. No browser.

Starts the MCP server as a subprocess and communicates via JSON-RPC stdio.
This is the correct way to use the MCP server from the command line.

Usage:
    python mcp/client.py                        # interactive mode
    python mcp/client.py query_concept sunyata  # single command
    python mcp/client.py get_tensions
    python mcp/client.py tradition_compare anatta
    python mcp/client.py find_free_text "Bodhicharyavatara"
    python mcp/client.py verify_quote "The mind is everything"
    python mcp/client.py identify_hindrance "My mind keeps jumping to plans"
    python mcp/client.py daily_reflection

Requirements:
    pip install ollama requests   (same as the server)
    ollama pull qwen2.5:7b
    ollama serve                  (in another terminal)
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path

SERVER = Path(__file__).parent / "dharma_mcp_server.py"


class MCPClient:
    """
    Thin JSON-RPC client that talks to dharma_mcp_server.py over stdio.
    The server runs as a subprocess — stdin/stdout are the transport.
    """

    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self._id = 0
        self._initialize()

    def _next_id(self):
        self._id += 1
        return self._id

    def _send(self, method, params=None):
        msg = {
            "jsonrpc": "2.0",
            "id":      self._next_id(),
            "method":  method,
            "params":  params or {}
        }
        line = json.dumps(msg) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()

    def _recv(self):
        line = self.proc.stdout.readline()
        if not line:
            return None
        return json.loads(line.strip())

    def _call(self, method, params=None):
        self._send(method, params)
        return self._recv()

    def _initialize(self):
        resp = self._call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "dharma-cli", "version": "1.0"}
        })
        if not resp or "error" in resp:
            print(f"Server init failed: {resp}", file=sys.stderr)
            sys.exit(1)
        # send initialized notification (no response expected)
        self._send("notifications/initialized")

    def list_tools(self):
        resp = self._call("tools/list")
        if resp and "result" in resp:
            return resp["result"].get("tools", [])
        return []

    def call_tool(self, name, arguments=None):
        resp = self._call("tools/call", {
            "name":      name,
            "arguments": arguments or {}
        })
        if resp and "result" in resp:
            content = resp["result"].get("content", [])
            return "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
        if resp and "error" in resp:
            return f"Error: {resp['error'].get('message', 'unknown error')}"
        return "No response"

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


# ── argument parsing for each tool ────────────────────────────────────────

TOOL_ARGS = {
    "query_concept":     [("concept_id", "Concept ID e.g. sunyata anatta pratityasamutpada")],
    "find_path":         [("source", "Source concept ID"), ("target", "Target concept ID")],
    "get_tensions":      [],
    "retrieve_passages": [("concept_id", "Concept ID"), ("n", "Number of passages (default 5)")],
    "tradition_compare": [("concept", "Concept name or ID")],
    "identify_hindrance":[("description", "Describe your meditation experience")],
    "verify_quote":      [("quote", "The quote to verify")],
    "find_free_text":    [("title", "Book title or sutta name")],
    "daily_reflection":  [],
}


def interactive(client):
    tools = client.list_tools()
    names = [t["name"] for t in tools]

    print("\nDharma-tech MCP client")
    print(f"Server: {SERVER}")
    print(f"Tools:  {', '.join(names)}")
    print("Type 'help' to list tools, 'quit' to exit\n")

    while True:
        try:
            line = input("dharma> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            break
        if line == "help":
            print("\nAvailable tools:")
            for t in tools:
                print(f"  {t['name']:<25} {t['description'][:60]}")
            print()
            continue

        parts = line.split(None, 1)
        name  = parts[0]

        if name not in names:
            print(f"Unknown tool: {name}. Type 'help' to list tools.")
            continue

        # gather arguments
        expected = TOOL_ARGS.get(name, [])
        args = {}

        if len(parts) > 1 and expected:
            # first arg provided on the same line
            args[expected[0][0]] = parts[1]
            # ask for remaining required args
            for param, hint in expected[1:]:
                val = input(f"  {param} ({hint}): ").strip()
                if val:
                    args[param] = int(val) if param == "n" else val
        else:
            for param, hint in expected:
                val = input(f"  {param} ({hint}): ").strip()
                if val:
                    args[param] = int(val) if param == "n" else val

        print()
        result = client.call_tool(name, args)
        print(result)
        print()


def single_command(client, tool_name, tool_args):
    """Run one tool and print result — for scripting."""
    if tool_name not in TOOL_ARGS:
        print(f"Unknown tool: {tool_name}")
        print(f"Available: {', '.join(TOOL_ARGS.keys())}")
        sys.exit(1)

    expected = TOOL_ARGS[tool_name]
    args = {}

    for i, (param, _) in enumerate(expected):
        if i < len(tool_args):
            val = tool_args[i]
            args[param] = int(val) if param == "n" and val.isdigit() else val

    print(client.call_tool(tool_name, args))


def main():
    parser = argparse.ArgumentParser(
        description="Command-line MCP client for dharma-tech (WSL/Linux terminal)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp/client.py                              # interactive
  python mcp/client.py query_concept sunyata
  python mcp/client.py find_path anatta sunyata
  python mcp/client.py get_tensions
  python mcp/client.py tradition_compare consciousness
  python mcp/client.py retrieve_passages sunyata 3
  python mcp/client.py verify_quote "Peace comes from within"
  python mcp/client.py identify_hindrance "mind keeps wandering"
  python mcp/client.py find_free_text "Heart Sutra"
  python mcp/client.py daily_reflection
        """
    )
    parser.add_argument("tool",   nargs="?", help="Tool name")
    parser.add_argument("params", nargs="*", help="Tool parameters")
    args = parser.parse_args()

    client = MCPClient()
    try:
        if args.tool:
            single_command(client, args.tool, args.params)
        else:
            interactive(client)
    finally:
        client.close()


if __name__ == "__main__":
    main()
