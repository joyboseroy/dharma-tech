<div align="center">

# 🪷 dharma-tech

**Buddhist AI — open source tools for dharma study, practice, and philosophy**

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE.md)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE.md)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![Ollama](https://img.shields.io/badge/Runs%20on-Ollama-orange.svg)](https://ollama.com)
[![HuggingFace](https://img.shields.io/badge/🤗-Dataset-yellow)](https://huggingface.co/datasets/joyboseroy/emptiness-graph)

*Local-first. No API keys. No subscriptions. Runs on your laptop.*

[**Quick Start**](#quick-start) · [**Tools**](#tools) · [**Philosophy**](#the-idea) · [**Contribute**](#contributing)

</div>

---

## What is this?

A collection of AI tools for Buddhist practitioners, students, scholars, and teachers — built with local LLMs, knowledge graphs, and agents.

**For practitioners:** Track your ngondro, log meditation sessions, get today's lojong slogan, plan a retreat.

**For students:** Find free translations of any Buddhist text, verify whether a quote is actually canonical, generate Anki flashcards from Buddhist concepts, compare how traditions differ.

**For scholars and teachers:** Cross-tradition philosophical comparison grounded in a typed knowledge graph, a Computational Madhyamaka reasoning engine, a passage index of 1,126 text segments across 10 canonical sources.

**For developers:** MCP server + command-line client running entirely in WSL/Linux terminal. Shared graph/LLM/RAG infrastructure. Typed philosophical knowledge graph ready to load into FalkorDB or NetworkX.

Everything runs locally. No data leaves your machine. No API keys required.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/joyboseroy/dharma-tech
cd dharma-tech

# 2. Install
pip install -r requirements.txt

# 3. Start local LLM (optional — tools work without it for core functions)
ollama pull qwen2.5:7b

# 4. Try something immediately
python tools/tradition-compare/tradition_compare.py sunyata
python practice/lojong-bot/lojong_bot.py
python tools/sutta-verifier/sutta_verifier.py "The mind is everything. What you think you become."
python tools/dharma-finder/dharma_finder.py "Bodhicharyavatara"
```

No database setup required for most tools. The knowledge graph data is in `data/` as plain JSONL files.

---

## Tools

### 🔍 Find & Verify

| Tool | What it does | Needs Ollama |
|------|-------------|:---:|
| [dharma-finder](tools/dharma-finder/) | Find free legal sources for any Buddhist book, sutta, or sutra. Searches SuttaCentral, 84000, Lotsawa House, BuddhaNet, Access to Insight, Internet Archive and 15 more sources. Verifies links are actually live. | Yes |
| [sutta-verifier](tools/sutta-verifier/) | Check whether a quote attributed to the Buddha is actually in the canonical texts. Catches the most common misattributions. | Yes |

```bash
python tools/dharma-finder/dharma_finder.py "Samaññaphala Sutta"
python tools/dharma-finder/dharma_finder.py --interactive

python tools/sutta-verifier/sutta_verifier.py "Peace comes from within. Do not seek it without."
python tools/sutta-verifier/sutta_verifier.py --check-suspicious  # batch check common misquotes
```

---

### 🧭 Philosophy & Study

| Tool | What it does | Needs Ollama |
|------|-------------|:---:|
| [tradition-compare](tools/tradition-compare/) | Compare how Theravada, Madhyamaka, Yogacara, and Mahayana relate to any concept. Graph-grounded — not LLM generation. | Optional |
| [prasanga-engine](agents/prasanga-engine/) | Apply the Madhyamaka prasanga (consequence) method to any claim. A LangGraph agent implementing formal Buddhist philosophical inference. | Yes |
| [flashcard-gen](study/flashcard-gen/) | Generate Anki flashcard decks from the Buddhist concept graph. Prerequisite-ordered. | No |

```bash
python tools/tradition-compare/tradition_compare.py sunyata
python tools/tradition-compare/tradition_compare.py consciousness --verbose
python tools/tradition-compare/tradition_compare.py --question "is there a self?"

python agents/prasanga-engine/prasanga_engine.py "consciousness has inherent existence"
python agents/prasanga-engine/prasanga_engine.py "my job defines who I am"
python agents/prasanga-engine/prasanga_engine.py --interactive

python study/flashcard-gen/flashcard_gen.py --tradition madhyamaka --output madhyamaka.apkg
python study/flashcard-gen/flashcard_gen.py --with-passages  # include text evidence
```

---

### 🪷 Daily Practice

| Tool | What it does | Needs Ollama |
|------|-------------|:---:|
| [lojong-bot](practice/lojong-bot/) | All 59 Atisha lojong slogans with commentary. One per day, rotationally. | Optional |
| [daily-sutta](practice/daily-sutta/) | Daily passage from the corpus with reflection. Can email via SMTP or run on a schedule. | Optional |
| [session-logger](practice/session-logger/) | Log meditation sessions with technique, hindrances, quality. Pattern analysis over time. | Optional |
| [ngondro-tracker](practice/ngondro-tracker/) | Track accumulations for all four foundations across traditions. Supports Nyingma, Kagyu, Gelug target counts. | No |
| [hindrance-id](tools/hindrance-id/) | Describe your meditation experience, identify which of the five hindrances is present, get the traditional antidote. | Yes |
| [precept-checker](tools/precept-checker/) | Ethical analysis of any daily life situation against the five precepts. Theravada and Mahayana perspectives. | Yes |

```bash
python practice/lojong-bot/lojong_bot.py
python practice/lojong-bot/lojong_bot.py --number 7
python practice/lojong-bot/lojong_bot.py --all

python practice/daily-sutta/daily_sutta.py --tradition theravada
python practice/daily-sutta/daily_sutta.py --email you@email.com --schedule

python practice/session-logger/session_logger.py log 45 --technique vipassana --hindrances restlessness
python practice/session-logger/session_logger.py status
python practice/session-logger/session_logger.py patterns  # LLM analysis of your trends

python practice/ngondro-tracker/ngondro_tracker.py log prostrations 108
python practice/ngondro-tracker/ngondro_tracker.py status
python practice/ngondro-tracker/ngondro_tracker.py --tradition karma_kagyu status

python tools/hindrance-id/hindrance_id.py "My mind keeps jumping to plans for later"
python tools/hindrance-id/hindrance_id.py --interactive

python tools/precept-checker/precept_checker.py "I told a small lie to spare someone's feelings"
```

---

### 🔌 MCP Server + CLI Client

Run all tools from your WSL/Linux terminal using the included client:

```bash
# interactive mode
python mcp/client.py

# single commands
python mcp/client.py query_concept sunyata
python mcp/client.py find_path anatta sunyata
python mcp/client.py get_tensions
python mcp/client.py tradition_compare consciousness
python mcp/client.py verify_quote "The mind is everything"
python mcp/client.py identify_hindrance "mind keeps wandering to plans"
python mcp/client.py find_free_text "Heart Sutra"
python mcp/client.py daily_reflection
```

The client starts the MCP server as a subprocess and communicates via JSON-RPC stdio.
Everything runs locally on your machine. No external services.

---

## The Knowledge Graph

At the core of this repo is a hand-authored typed philosophical knowledge graph:

- **25 concept nodes** — sunyata, anatta, pratityasamutpada, svabhava, prasanga, alayavijnana, tathagatagarbha, bodhichitta, and more — with Sanskrit, Pali, and Tibetan terms
- **38 philosophical edges** — typed with 17 relation types: `negates`, `refutes`, `is_identical_to`, `tensions_with`, `reframes_as`, `presupposes`, `enables`, and more
- **1,126 text passages** from 10 canonical sources — Heart Sutra, Diamond Sutra, MMK (Nagarjuna), Bodhicharyavatara Ch.9 (Shantideva), Samaññaphala Sutta, and more
- **Every edge has a `notes` field** — a paragraph of philosophical reasoning explaining why the edge exists

The graph is available as a HuggingFace dataset: [joyboseroy/emptiness-graph](https://huggingface.co/datasets/joyboseroy/emptiness-graph)

```python
# Load and query in Python
import json, networkx as nx

def load_jsonl(path):
    return [json.loads(l) for l in open(path) if l.strip() and not l.startswith('#')]

G = nx.MultiDiGraph()
for c in load_jsonl("data/concepts.jsonl"):
    G.add_node(c["id"], **c)
for e in load_jsonl("data/edges.jsonl"):
    G.add_edge(e["source"], e["target"], **e)

# What does the Heart Sutra refute?
for u, v, data in G.edges(data=True):
    if u == "heart_sutra" and data["relation"] in ("refutes", "deconstructs"):
        print(f"{G.nodes[v]['label']} [{data['relation']}]")

# How do traditions differ on sunyata?
for u, v, data in G.edges(data=True):
    if "sunyata" in (u, v):
        print(f"[{data['tradition']}] {u} --{data['relation']}--> {v}")
```

Or load into FalkorDB for Cypher queries:

```bash
docker run -p 6379:6379 falkordb/falkordb:latest
python -c "from core.db import DharmaDB; DharmaDB().load_emptiness_graph()"
```

```cypher
-- All paths from anatta to sunyata
MATCH path = (:Concept {id:'anatta'})-[*1..3]->(:Concept {id:'sunyata'})
RETURN path

-- How traditions differ on a concept
MATCH (a)-[r]->(b:Concept {id:'sunyata'})
RETURN r.tradition, a.label, type(r), r.weight
ORDER BY r.weight DESC

-- All live doctrinal tensions
MATCH (a)-[r:TENSIONS_WITH]->(b)
RETURN a.label, b.label, r.notes
```

---

## The Idea

Most "Buddhist AI" projects are chatbots with a system prompt saying "answer like a monk." This repo is different.

Buddhist philosophy has a specific claim about the nature of reality: nothing exists independently. Everything arises in dependence on causes, conditions, and designations. This is *pratityasamutpada* — dependent origination.

From a computer science perspective, dependent origination is a graph. Everything is a node. All existence is edges. There are no standalone nodes — only the network.

**The graph is not representing Buddhist philosophy. It is demonstrating it.**

This means:
- The prasanga engine applies Nagarjuna's inference procedure formally, not as a chatbot persona
- The tradition comparator uses typed graph edges, not LLM generation from training data
- The hindrance identifier and precept checker are grounded in the passage corpus, not just prompted LLM knowledge
- The MCP server exposes graph-constrained reasoning, not open-ended generation

The LLM is used for what LLMs are good at: understanding natural language queries and generating natural language responses. The graph is used for what graphs are good at: encoding philosophical structure and constraining inference.

---

## Text Sources

All texts are openly available. No paywalled content.

| Source | Coverage | License |
|--------|----------|---------|
| SuttaCentral | Pali Canon, CC0 | CC0 |
| Access to Insight | Theravada | Free distribution |
| Dhammatalks.org | Thanissaro translations | Free distribution |
| BuddhaNet | All traditions | Free |
| 84000.co | Tibetan Kangyur/Tengyur | CC BY-NC-ND |
| Lotsawa House | 6000+ Tibetan texts | CC BY-NC |
| Internet Archive | Pre-1928 translations | Public domain |
| GRETIL | Sanskrit originals | Public domain |

The dharma-finder tool knows about all of these and routes queries to the right source automatically.

---

## Project Structure

```
dharma-tech/
├── core/                    # Shared infrastructure (import from here)
│   ├── db.py               # FalkorDB helpers
│   ├── llm.py              # Ollama wrapper + Buddhist prompt templates
│   └── rag.py              # Graph-constrained RAG
│
├── data/                    # Knowledge graph data (JSONL, ready to use)
│   ├── concepts.jsonl      # 25 philosophical concept nodes
│   ├── edges.jsonl         # 38 typed philosophical edges
│   ├── corpus_manifest.jsonl # 16 source texts with metadata
│   ├── passages.jsonl      # 1,126 text passages
│   └── passage_edges.jsonl # Passage-concept links
│
├── mcp/
│   ├── dharma_mcp_server.py # MCP server (JSON-RPC stdio)
│   └── client.py            # command-line MCP client for WSL
│
├── agents/
│   └── prasanga-engine/    # Computational Madhyamaka (LangGraph)
│
├── tools/                   # Single-purpose tools
│   ├── dharma-finder/      # Free text locator
│   ├── sutta-verifier/     # Quote verification
│   ├── tradition-compare/  # Cross-tradition comparison
│   ├── hindrance-id/       # Meditation hindrance identifier
│   └── precept-checker/    # Five precepts analysis
│
├── practice/                # Daily practice tools
│   ├── lojong-bot/         # 59 slogans with commentary
│   ├── daily-sutta/        # Daily passage + reflection
│   ├── session-logger/     # Meditation log
│   └── ngondro-tracker/    # Accumulation counter
│
└── study/
    └── flashcard-gen/      # Anki deck generator
```

---

## Contributing

The most valuable contributions, in order:

**1. New edges in `data/edges.jsonl`**
Add a typed philosophical relation with a `notes` field explaining the reasoning. Do not add edges without notes — that field is the scholarly contribution. See existing edges for format.

**2. New source texts as passages**
Place a `.txt` file in `data/texts/`, add an entry to `corpus_manifest.jsonl`, run `python scripts/build_passage_index.py`. Translations must be public domain or openly licensed.

**3. Extend the known texts registry**
Add entries to `tools/dharma-finder/sources.py` for texts you know the free-source status of. The `KNOWN_TEXTS` dict is where pre-verified source information lives.

**4. New tools**
Each tool should import from `core/` rather than reimplementing LLM calls or graph queries. A new tool is essentially: one function calling `core/llm.py`, one calling `core/rag.py`, formatted output. The hindrance identifier is the template.

**Please do not add:**
- LLM personas without graph grounding ("you are a Zen master")
- Tools that make philosophical claims without citing graph edges
- Content scraped from paywalled or copyrighted sources

---

## Related projects

- [emptiness-graph](https://github.com/joyboseroy/emptiness-graph) — the knowledge graph used here, also available standalone
- [indic-concept-graph](https://github.com/joyboseroy/indic-concept-graph) — prerequisite concept graph, 22 Indic languages
- [DharmaBench](https://aclanthology.org/2025.ijcnlp-long.114.pdf) — linguistic benchmark for Sanskrit/Tibetan NLP
- [SuttaCentral](https://suttacentral.net) — the canonical Buddhist text platform
- [84000](https://84000.co) — Tibetan canonical translation project

---

## Citation

```bibtex
@software{bose2026dharmatech,
  title   = {dharma-tech: Buddhist AI — Open Source Tools for Dharma Study and Practice},
  author  = {Bose, Joy},
  year    = {2026},
  version = {1.0},
  url     = {https://github.com/joyboseroy/dharma-tech},
  note    = {Local-first Buddhist AI tools using FalkorDB, Ollama, and
             graph-constrained reasoning. MIT license.}
}
```

---

## License

Code: **MIT**
Graph data (`concepts.jsonl`, `edges.jsonl`, `corpus_manifest.jsonl`): **CC BY 4.0**
Passage data (`passages.jsonl`): **CC BY-NC 4.0** (includes 84000 material)

---

<div align="center">
<sub>Built with respect for the tradition. Not a replacement for teachers, practice, or community.</sub>
</div>
