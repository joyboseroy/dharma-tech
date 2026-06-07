"""
mcp/dharma_mcp_server.py

A self-contained MCP server for dharma-tech.
Built from scratch using raw JSON-RPC over stdio.
No Anthropic SDK. No Claude API. No cloud dependencies.

Uses only:
  - ollama (local LLM)
  - falkordb (local graph DB, optional)
  - standard Python libraries

Works with any MCP-compatible client:
  - Claude Desktop
  - Cursor
  - Any MCP client that speaks JSON-RPC over stdio

HOW MCP WORKS (stdio transport):
  1. Client starts this script as a subprocess
  2. Client sends JSON-RPC requests on stdin
  3. This server reads stdin, processes, writes JSON-RPC responses to stdout
  4. stderr is for logging only — never write tool output to stderr

SETUP:
  pip install ollama requests
  ollama pull qwen2.5:7b
  ollama serve   (in a separate terminal)

Add to your MCP client config:
  {
    "mcpServers": {
      "dharma-tech": {
        "command": "python",
        "args": ["/absolute/path/to/dharma-tech/mcp/dharma_mcp_server.py"]
      }
    }
  }

Test without a client:
  python dharma_mcp_server.py --cli
"""

import sys
import json
import os
import logging
from pathlib import Path

# ── logging to stderr only (stdout is the MCP channel) ────────────────────
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [dharma-mcp] %(message)s"
)
log = logging.getLogger("dharma-mcp")

# ── path setup ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
DATA_DIR = ROOT / "data"

# ── optional imports ───────────────────────────────────────────────────────
try:
    import ollama as _ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    log.warning("ollama not installed: pip install ollama")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

OLLAMA_MODEL = os.environ.get("DHARMA_MODEL", "qwen2.5:7b")
OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434")


# ── data helpers ───────────────────────────────────────────────────────────

def load_jsonl(path):
    records = []
    p = Path(path)
    if not p.exists():
        return records
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records

def _concepts():
    return {c["id"]: c for c in load_jsonl(DATA_DIR / "concepts.jsonl")}

def _edges():
    return load_jsonl(DATA_DIR / "edges.jsonl")

def _texts():
    return {t["id"]: t for t in load_jsonl(DATA_DIR / "corpus_manifest.jsonl")}

def _passages():
    return load_jsonl(DATA_DIR / "passages.jsonl")

def _pedges():
    return load_jsonl(DATA_DIR / "passage_edges.jsonl")


# ── local LLM call (Ollama only, no cloud) ─────────────────────────────────

def llm(prompt, temperature=0.2):
    """Call local Ollama — no cloud, no API key."""
    if not HAS_OLLAMA:
        return "[Ollama not installed. Run: pip install ollama]"
    try:
        r = _ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        return r["message"]["content"].strip()
    except Exception as e:
        log.error(f"Ollama error: {e}")
        return f"[Ollama error: {e}. Is Ollama running? Try: ollama serve]"

def llm_json(prompt, temperature=0.1):
    """Call Ollama, expect JSON back."""
    text = llm(prompt, temperature)
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "LLM did not return valid JSON", "raw": text[:200]}


# ── tool implementations ───────────────────────────────────────────────────

def tool_query_concept(concept_id: str) -> str:
    concepts = _concepts()
    edges    = _edges()
    texts    = _texts()

    # fuzzy match if exact not found
    if concept_id not in concepts:
        for cid, c in concepts.items():
            if concept_id.lower() in c.get("label", "").lower():
                concept_id = cid
                break
        else:
            return (f"Concept '{concept_id}' not found.\n"
                    f"Available: {', '.join(list(concepts.keys())[:15])}")

    c = concepts[concept_id]
    out = [
        f"## {c['label']}",
        f"Sanskrit: {c.get('sanskrit','')}  |  "
        f"Pali: {c.get('pali','')}  |  "
        f"Tibetan: {c.get('tibetan','')}",
        f"Tradition: {c.get('tradition',[])}",
        f"Category: {c.get('category','')}",
        "",
        f"{c.get('definition','')}",
        "",
        "### Philosophical edges:"
    ]
    for e in edges:
        if concept_id not in (e["source"], e["target"]):
            continue
        other_id = e["target"] if e["source"] == concept_id else e["source"]
        other    = (concepts.get(other_id, texts.get(other_id, {}))
                    .get("label", other_id))
        direction = "→" if e["source"] == concept_id else "←"
        out.append(
            f"  {direction} [{e['relation']}] {other} "
            f"[{e.get('tradition','')}] weight={e.get('weight',0.5)}"
        )
        if e.get("notes"):
            out.append(f"    {e['notes'][:150]}")
    return "\n".join(out)


def tool_find_path(source: str, target: str) -> str:
    edges    = _edges()
    concepts = _concepts()
    texts    = _texts()

    def label(nid):
        return (concepts.get(nid, texts.get(nid, {}))
                .get("label", nid))

    # build adjacency
    graph = {}
    for e in edges:
        graph.setdefault(e["source"], []).append((e["target"], e["relation"]))

    # BFS
    from collections import deque
    queue   = deque([(source, [(source, "")])])
    visited = {source}
    while queue:
        node, path = queue.popleft()
        if node == target:
            lines = ["### Path found:"]
            for i, (n, rel) in enumerate(path):
                if i < len(path) - 1:
                    next_rel = path[i+1][1]
                    lines.append(f"  {label(n)} --[{next_rel}]-->")
                else:
                    lines.append(f"  {label(n)}")
            return "\n".join(lines)
        for nbr, rel in graph.get(node, []):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, path + [(nbr, rel)]))
    return f"No path found between '{source}' and '{target}'."


def tool_get_tensions() -> str:
    edges    = _edges()
    concepts = _concepts()
    texts    = _texts()

    def label(nid):
        return (concepts.get(nid, texts.get(nid, {}))
                .get("label", nid))

    tensions = [e for e in edges if e["relation"] == "tensions_with"]
    if not tensions:
        return "No doctrinal tensions found in current graph."

    lines = ["## Live doctrinal tensions\n"]
    for e in tensions:
        a = label(e["source"])
        b = label(e["target"])
        lines.append(f"**{a}  ↔  {b}**")
        lines.append(f"Tradition: {e.get('tradition','mixed')}")
        if e.get("notes"):
            lines.append(e["notes"][:300])
        lines.append("")
    return "\n".join(lines)


def tool_retrieve_passages(concept_id: str, n: int = 5) -> str:
    passages = _passages()
    pedges   = _pedges()

    pids = {pe["source"] for pe in pedges if pe["target"] == concept_id}

    # also try neighbours (1 hop)
    edges = _edges()
    neighbours = set()
    for e in edges:
        if e["source"] == concept_id:
            neighbours.add(e["target"])
        if e["target"] == concept_id:
            neighbours.add(e["source"])
    for pe in pedges:
        if pe["target"] in neighbours:
            pids.add(pe["source"])

    pid_index = {p["id"]: p for p in passages}
    results   = [pid_index[pid] for pid in pids if pid in pid_index]

    # rank by how many concepts mentioned
    results.sort(key=lambda p: len(p.get("concepts_mentioned", [])), reverse=True)
    results = results[:n]

    if not results:
        return f"No passages found for '{concept_id}'."

    lines = [f"## Passages for '{concept_id}' ({len(results)} found)\n"]
    for p in results:
        lines.append(f"**[{p['text_id']}]**")
        lines.append(p["text"][:500])
        if p.get("concepts_mentioned"):
            lines.append(f"_Concepts: {', '.join(p['concepts_mentioned'])}_")
        lines.append("")
    return "\n".join(lines)


def tool_tradition_compare(concept: str) -> str:
    concepts = _concepts()
    edges    = _edges()
    texts    = _texts()

    # find concept
    concept_id = concept
    if concept_id not in concepts:
        for cid, c in concepts.items():
            if concept.lower() in c.get("label","").lower():
                concept_id = cid
                break
        else:
            return f"Concept '{concept}' not found."

    label = concepts[concept_id]["label"]
    defn  = concepts[concept_id].get("definition", "")

    by_trad = {}
    for e in edges:
        if concept_id not in (e["source"], e["target"]):
            continue
        trad = e.get("tradition", "mixed") or "mixed"
        by_trad.setdefault(trad, [])
        other_id  = e["target"] if e["source"] == concept_id else e["source"]
        other_lbl = (concepts.get(other_id, texts.get(other_id, {}))
                     .get("label", other_id))
        direction = "→" if e["source"] == concept_id else "←"
        by_trad[trad].append(
            f"  {direction} [{e['relation']}] {other_lbl}\n"
            f"    {e.get('notes','')[:120]}"
        )

    lines = [f"## {label} — cross-tradition comparison\n", defn, ""]
    order = ["theravada", "madhyamaka", "prasangika",
             "yogacara", "prajnaparamita", "mahayana", "mixed"]
    for trad in order:
        if trad in by_trad:
            lines.append(f"### {trad.title()}")
            lines.extend(by_trad[trad])
            lines.append("")
    for trad, items in by_trad.items():
        if trad not in order:
            lines.append(f"### {trad.title()}")
            lines.extend(items)
            lines.append("")
    return "\n".join(lines)


def tool_identify_hindrance(description: str) -> str:
    prompt = f"""You are a Theravada meditation teacher.
The student describes their experience. Identify which of the five hindrances is present.

Five hindrances: sensual_desire, ill_will, sloth_torpor, restlessness_worry, doubt

Return ONLY valid JSON:
{{
  "hindrance": "name",
  "confidence": 0.0-1.0,
  "explanation": "2-3 sentences",
  "antidote": "traditional antidote from Pali texts",
  "sutta_reference": "sutta if known or null"
}}

Experience: {description}"""

    result = llm_json(prompt)
    if "error" in result:
        return f"LLM error: {result.get('raw','')}"

    hindrance  = result.get("hindrance", "unknown")
    confidence = int(result.get("confidence", 0) * 100)
    icons = {"sensual_desire": "🔥", "ill_will": "😠",
             "sloth_torpor": "😴", "restlessness_worry": "😰",
             "doubt": "🤔", "none": "✓"}
    icon = icons.get(hindrance, "•")

    lines = [
        f"{icon} **{hindrance.replace('_',' ').title()}** ({confidence}% confidence)",
        "",
        result.get("explanation", ""),
    ]
    if result.get("antidote"):
        lines += ["", f"**Antidote:** {result['antidote']}"]
    if result.get("sutta_reference"):
        lines += ["", f"**Reference:** {result['sutta_reference']}"]
    return "\n".join(lines)


def tool_verify_quote(quote: str) -> str:
    prompt = f"""You are a Pali Canon scholar.
Is this quote actually in the Buddhist canonical texts?

Common misattributed quotes: "The mind is everything what you think you become",
"Peace comes from within", "Three things cannot be long hidden",
"If you truly loved yourself you could never hurt another".

Return ONLY valid JSON:
{{
  "verdict": "authentic/misattributed/uncertain",
  "confidence": 0.0-1.0,
  "explanation": "2-3 sentences",
  "actual_source": "sutta ref and translator if authentic, null if not",
  "similar_authentic": "closest real canonical quote if misattributed, null otherwise"
}}

Quote: {quote}"""

    result = llm_json(prompt)
    if "error" in result:
        return f"LLM error: {result.get('raw','')}"

    verdict = result.get("verdict", "uncertain")
    icons   = {"authentic": "✓", "misattributed": "✗", "uncertain": "?"}
    icon    = icons.get(verdict, "?")
    conf    = int(result.get("confidence", 0) * 100)

    lines = [
        f"{icon} **{verdict.upper()}** ({conf}% confidence)",
        "",
        result.get("explanation", ""),
    ]
    if result.get("actual_source"):
        lines += ["", f"**Source:** {result['actual_source']}"]
    if result.get("similar_authentic"):
        lines += ["", f"**Closest canonical quote:** {result['similar_authentic']}"]
    return "\n".join(lines)


def tool_find_free_text(title: str) -> str:
    """
    Find free sources for a Buddhist text.
    Uses the sources registry then falls back to Ollama knowledge.
    """
    # try sources registry first
    sources_path = ROOT / "tools" / "dharma-finder" / "sources.py"
    if sources_path.exists():
        sys.path.insert(0, str(sources_path.parent))
        try:
            from sources import KNOWN_TEXTS, SOURCES
            from dharma_finder import lookup_known_texts, detect_tradition, build_search_urls

            known    = lookup_known_texts(title)
            tradition = detect_tradition(title)
            search   = build_search_urls(title, tradition)

            lines = [f"## Free sources for: {title}\n"]
            if known:
                _, entry = known
                free = entry.get("free_sources", [])
                if free:
                    lines.append(f"**Direct links ({len(free)}):**")
                    for s in free:
                        src  = SOURCES.get(s.get("source",""), {})
                        name = src.get("name", s.get("source",""))
                        lines.append(f"  • [{name}]({s.get('url','')})")
                        lines.append(
                            f"    {s.get('translator','')} | "
                            f"{s.get('type','')} | {s.get('license','')}"
                        )
                    lines.append("")
                note = entry.get("commercial_note","")
                if note:
                    lines.append(f"**Note:** {note}\n")

            if not (known and known[1].get("free_sources")):
                lines.append("**Search these sources:**")
                seen = set()
                for s in search[:6]:
                    if s["source"] not in seen:
                        seen.add(s["source"])
                        lines.append(f"  • [{s['name']}]({s['url']})")

            return "\n".join(lines)
        except Exception as e:
            log.warning(f"sources registry error: {e}")

    # fallback: ask Ollama
    prompt = f"""You are a Buddhist librarian. What free legal online sources exist
for this text? List specific URLs if you know them. Be honest if you are unsure.
Text: {title}"""
    return llm(prompt, temperature=0.2)


def tool_daily_reflection() -> str:
    import hashlib
    from datetime import date

    passages = _passages()
    if not passages:
        return "No passages loaded. Check data/passages.jsonl."

    seed    = int(hashlib.md5(str(date.today()).encode()).hexdigest(), 16)
    passage = passages[seed % len(passages)]
    today   = date.today().strftime("%A, %B %-d")

    # lojong slogan
    slogan_text = ""
    lojong_path = ROOT / "practice" / "lojong-bot" / "lojong_bot.py"
    if lojong_path.exists():
        sys.path.insert(0, str(lojong_path.parent))
        try:
            from lojong_bot import get_slogan
            num, slogan, commentary = get_slogan()
            slogan_text = f"\n## Lojong slogan {num}\n\"{slogan}\"\n\n{commentary}"
        except Exception:
            pass

    lines = [
        f"## Daily reflection — {today}",
        "",
        f"**From the texts [{passage['text_id']}]:**",
        passage["text"][:500],
        slogan_text
    ]
    return "\n".join(lines)


# ── MCP tool registry ──────────────────────────────────────────────────────

TOOLS = {
    "query_concept": {
        "description": (
            "Get a Buddhist philosophical concept with all its typed edges. "
            "Try: sunyata, anatta, pratityasamutpada, svabhava, bodhichitta"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "concept_id": {
                    "type": "string",
                    "description": "Concept ID e.g. sunyata, anatta, two_truths"
                }
            },
            "required": ["concept_id"]
        },
        "fn": lambda a: tool_query_concept(a["concept_id"])
    },
    "find_path": {
        "description": "Find the shortest philosophical path between two Buddhist concepts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source concept ID"},
                "target": {"type": "string", "description": "Target concept ID"}
            },
            "required": ["source", "target"]
        },
        "fn": lambda a: tool_find_path(a["source"], a["target"])
    },
    "get_tensions": {
        "description": "Get all live doctrinal tensions between Buddhist traditions encoded in the graph.",
        "inputSchema": {"type": "object", "properties": {}},
        "fn": lambda a: tool_get_tensions()
    },
    "retrieve_passages": {
        "description": "Get text passages from the Buddhist corpus for a concept.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "concept_id": {"type": "string"},
                "n": {"type": "integer", "default": 5, "description": "Number of passages"}
            },
            "required": ["concept_id"]
        },
        "fn": lambda a: tool_retrieve_passages(a["concept_id"], a.get("n", 5))
    },
    "tradition_compare": {
        "description": (
            "Compare how Buddhist traditions (Theravada, Madhyamaka, Yogacara, Mahayana) "
            "relate to a concept. Uses the knowledge graph — not LLM generation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Concept name or ID e.g. sunyata, consciousness, anatta"
                }
            },
            "required": ["concept"]
        },
        "fn": lambda a: tool_tradition_compare(a["concept"])
    },
    "identify_hindrance": {
        "description": (
            "Describe your meditation experience. "
            "Identifies which of the five hindrances is present with the traditional antidote. "
            "Uses local Ollama LLM."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Plain description of your meditation experience"
                }
            },
            "required": ["description"]
        },
        "fn": lambda a: tool_identify_hindrance(a["description"])
    },
    "verify_quote": {
        "description": (
            "Check whether a quote attributed to the Buddha or Buddhist teachers "
            "is actually in the canonical texts. Many popular quotes are misattributed. "
            "Uses local Ollama LLM."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "quote": {"type": "string", "description": "The quote to verify"}
            },
            "required": ["quote"]
        },
        "fn": lambda a: tool_verify_quote(a["quote"])
    },
    "find_free_text": {
        "description": (
            "Find free legal online sources for any Buddhist book, sutta, or sutra. "
            "Searches SuttaCentral, 84000, Lotsawa House, BuddhaNet, Access to Insight, "
            "Internet Archive and more."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Book title, sutta name, or description"
                }
            },
            "required": ["title"]
        },
        "fn": lambda a: tool_find_free_text(a["title"])
    },
    "daily_reflection": {
        "description": "Get today's Buddhist reflection — a passage from the corpus and a lojong slogan.",
        "inputSchema": {"type": "object", "properties": {}},
        "fn": lambda a: tool_daily_reflection()
    },
}


# ── Raw JSON-RPC stdio MCP server ──────────────────────────────────────────
# Implements the MCP protocol directly — no SDK, no Anthropic dependency.
# Spec: https://spec.modelcontextprotocol.io/

def send(obj):
    """Write a JSON-RPC message to stdout."""
    line = json.dumps(obj, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    send({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message}
    })

def handle(msg):
    method = msg.get("method", "")
    req_id = msg.get("id")
    params = msg.get("params", {})

    # ── initialize handshake ───────────────────────────────────────────────
    if method == "initialize":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name":    "dharma-tech",
                    "version": "1.0.0"
                }
            }
        })

    elif method == "notifications/initialized":
        pass  # client acknowledgement, no response needed

    # ── list tools ────────────────────────────────────────────────────────
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name":        name,
                        "description": info["description"],
                        "inputSchema": info["inputSchema"]
                    }
                    for name, info in TOOLS.items()
                ]
            }
        })

    # ── call tool ─────────────────────────────────────────────────────────
    elif method == "tools/call":
        name      = params.get("name", "")
        arguments = params.get("arguments", {})

        if name not in TOOLS:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return

        log.info(f"Calling tool: {name} args={list(arguments.keys())}")
        try:
            result = TOOLS[name]["fn"](arguments)
        except Exception as e:
            log.error(f"Tool error {name}: {e}", exc_info=True)
            result = f"Error running {name}: {e}"

        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": str(result)}]
            }
        })

    # ── ping ──────────────────────────────────────────────────────────────
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": req_id, "result": {}})

    # ── unknown method ────────────────────────────────────────────────────
    elif req_id is not None:
        send_error(req_id, -32601, f"Method not found: {method}")


def run_stdio():
    """Main loop — read JSON-RPC from stdin, write responses to stdout."""
    log.info(f"dharma-tech MCP server started (model={OLLAMA_MODEL})")
    log.info(f"Data directory: {DATA_DIR}")
    log.info(f"Ollama available: {HAS_OLLAMA}")

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            msg = json.loads(raw_line)
            handle(msg)
        except json.JSONDecodeError as e:
            log.error(f"Bad JSON: {e}")
        except Exception as e:
            log.error(f"Unhandled error: {e}", exc_info=True)


# ── CLI test mode ─────────────────────────────────────────────────────────

def run_cli():
    """
    Interactive CLI for testing tools without a MCP client.
    Useful for verifying everything works before connecting Claude Desktop.
    """
    print("\nDharma-tech MCP server — CLI test mode")
    print(f"Model: {OLLAMA_MODEL}  |  Ollama: {HAS_OLLAMA}")
    print(f"Data: {DATA_DIR}")
    print(f"\nAvailable tools: {', '.join(TOOLS.keys())}")
    print("Type 'quit' to exit\n")

    while True:
        try:
            name = input("Tool name: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if name in ("quit", "q", "exit"):
            break
        if name not in TOOLS:
            print(f"Unknown tool. Options: {', '.join(TOOLS.keys())}")
            continue

        schema   = TOOLS[name]["inputSchema"]
        required = schema.get("required", [])
        props    = schema.get("properties", {})
        args     = {}

        for param, info in props.items():
            if param in required:
                val = input(f"  {param}: ").strip()
                if info.get("type") == "integer":
                    val = int(val) if val else info.get("default", 5)
                args[param] = val

        print()
        try:
            result = TOOLS[name]["fn"](args)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        print()


# ── entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_cli()
    else:
        run_stdio()
