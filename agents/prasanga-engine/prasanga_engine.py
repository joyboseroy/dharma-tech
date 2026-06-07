"""
agents/prasanga-engine/prasanga_engine.py

Computational Madhyamaka — a LangGraph agent that applies the prasanga
(consequence) method to any claim.

The prasanga method (Nagarjuna, Vigrahavyavartani):
  1. Take the opponent's position
  2. Find its hidden svabhava assumption
  3. Derive an unwanted consequence from that assumption
  4. Show the consequence contradicts the opponent's own premises
  5. Conclude the position is untenable
  6. Show what remains conventionally valid

This is NOT a chatbot. It is a formal inference procedure.
The LLM fills natural language. The graph provides the dependency structure.
The inference rules are deterministic.

Usage:
    python prasanga_engine.py "consciousness has inherent existence"
    python prasanga_engine.py "my job defines who I am"
    python prasanga_engine.py "this nation has always existed"
    python prasanga_engine.py --interactive

Requires: pip install langgraph ollama
"""

import sys
import json
import argparse
from typing import TypedDict, Optional, List
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.rag import GraphRAG

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    print("Install: pip install langgraph", file=sys.stderr)

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

DATA_DIR = Path(__file__).parent.parent.parent / "data"
MODEL = "qwen2.5:7b"

# ── Inference rules ───────────────────────────────────────────────────────
# These are the formal Madhyamaka rules applied deterministically.
# The LLM is NOT used for these — they are the graph layer.

INFERENCE_RULES = {
    "dependence_rule": {
        "name": "Dependence implies no svabhava",
        "pattern": "If X depends on Y, X lacks svabhava",
        "mmk_ref": "MMK Ch.1 — nothing arises from itself, another, both, or neither",
        "apply": lambda deps: len(deps) > 0
    },
    "impermanence_rule": {
        "name": "Impermanence implies no self",
        "pattern": "If X is impermanent and identified as self, self lacks svabhava",
        "mmk_ref": "MMK Ch.18 — if aggregates were self, self would arise and cease",
        "apply": lambda deps: any(
            d in ["twelve_nidanas", "five_aggregates", "pratityasamutpada"]
            for d in deps
        )
    },
    "self_application_rule": {
        "name": "Emptiness of emptiness",
        "pattern": "Apply the analysis to the analysis itself",
        "mmk_ref": "Vigrahavyavartani — the words refuting svabhava also lack svabhava",
        "apply": lambda deps: True  # always apply as final check
    },
    "two_truths_rule": {
        "name": "Conventional validity preserved",
        "pattern": "Lacking svabhava does not mean nonexistent conventionally",
        "mmk_ref": "MMK Ch.24 — emptiness enables conventional functioning",
        "apply": lambda deps: True  # always apply to prevent nihilism
    }
}

def load_jsonl(path):
    records = []
    if not Path(path).exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                records.append(json.loads(line))
    return records


# ── State ──────────────────────────────────────────────────────────────────

class PrasangaState(TypedDict):
    claim: str
    hidden_assumption: Optional[str]
    graph_concepts: Optional[List[str]]
    graph_dependencies: Optional[List[str]]
    applicable_rules: Optional[List[str]]
    consequence: Optional[str]
    contradiction: Optional[str]
    nihilism_check: Optional[str]
    conventional_note: Optional[str]
    mmk_references: Optional[List[str]]
    passage_evidence: Optional[List[str]]
    final_argument: Optional[str]
    complete: bool


# ── Node functions ─────────────────────────────────────────────────────────

def llm_call(prompt: str, temperature: float = 0.1) -> str:
    if not HAS_OLLAMA:
        return "{}"
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature}
    )
    return response["message"]["content"].strip()


def node_extract_assumption(state: PrasangaState) -> PrasangaState:
    """
    Node 1: Extract the hidden svabhava assumption.
    What independent, inherent existence does this claim presuppose?
    """
    prompt = f"""You are a Madhyamaka philosopher. Find the hidden svabhava assumption.

Every claim that something "truly exists", "defines", "is essentially", or "really is"
contains a hidden assumption that the thing has inherent, independent existence (svabhava).

Claim: "{state['claim']}"

Return ONLY valid JSON:
{{
  "hidden_assumption": "The claim assumes that X possesses svabhava because...",
  "concepts_involved": ["list", "of", "relevant", "buddhist", "concepts"],
  "tradition_relevance": "madhyamaka"
}}"""

    text = llm_call(prompt)
    text = text.replace("```json","").replace("```","").strip()
    try:
        result = json.loads(text)
        return {
            **state,
            "hidden_assumption": result.get("hidden_assumption",""),
            "graph_concepts": result.get("concepts_involved", []),
        }
    except Exception:
        return {**state,
                "hidden_assumption": f"The claim assumes '{state['claim']}' has svabhava",
                "graph_concepts": ["svabhava", "pratityasamutpada"]}


def node_graph_traversal(state: PrasangaState) -> PrasangaState:
    """
    Node 2: DETERMINISTIC graph traversal — no LLM.
    Find what the claimed entity depends on using the emptiness-graph.
    This is where the graph does real philosophical work.
    """
    concepts = {c["id"]: c for c in load_jsonl(DATA_DIR / "concepts.jsonl")}
    edges = load_jsonl(DATA_DIR / "edges.jsonl")
    rag = GraphRAG()

    # map claim concepts to graph nodes
    graph_concepts = state.get("graph_concepts", [])
    matched_nodes = []
    for gc in graph_concepts:
        gc_lower = gc.lower().replace(" ", "_").replace("-", "_")
        if gc_lower in concepts:
            matched_nodes.append(gc_lower)
        else:
            for cid in concepts:
                if gc_lower in cid or cid in gc_lower:
                    matched_nodes.append(cid)
                    break

    # find dependencies: what do these concepts depend_on or presuppose?
    dependencies = set()
    mmk_refs = []

    for node in matched_nodes:
        for e in edges:
            if e["source"] == node and e["relation"] in (
                "presupposes", "depends_on", "is_precursor_of"
            ):
                dependencies.add(e["target"])
                if "mmk" in e.get("notes","").lower():
                    mmk_refs.append(f"MMK: {e['notes'][:80]}")

            # what negates this concept?
            if e["target"] == node and e["relation"] == "negates":
                dependencies.add(e["source"])

    # always add the core dependency chain
    core_deps = ["pratityasamutpada", "svabhava"]
    dependencies.update(core_deps)

    # retrieve relevant passages
    passages = []
    for node in (matched_nodes or ["sunyata"]):
        ps = rag.retrieve_constrained(node, hops=1, top_n=2)
        passages.extend(p["text"][:200] for p in ps)

    # determine which inference rules apply
    applicable = []
    for rule_id, rule in INFERENCE_RULES.items():
        if rule["apply"](list(dependencies)):
            applicable.append(rule_id)
            mmk_refs.append(rule["mmk_ref"])

    return {
        **state,
        "graph_dependencies": list(dependencies),
        "applicable_rules": applicable,
        "mmk_references": list(set(mmk_refs))[:5],
        "passage_evidence": passages[:3],
    }


def node_derive_consequence(state: PrasangaState) -> PrasangaState:
    """
    Node 3: Derive the unwanted consequence.
    If the claim's hidden assumption were true, what absurd result follows?
    """
    deps = state.get("graph_dependencies", [])
    rules = state.get("applicable_rules", [])

    rule_texts = [
        f"Rule: {INFERENCE_RULES[r]['pattern']} (ref: {INFERENCE_RULES[r]['mmk_ref']})"
        for r in rules if r in INFERENCE_RULES
    ]

    prompt = f"""You are a Madhyamaka philosopher applying the prasanga method.

Claim: "{state['claim']}"
Hidden assumption: {state.get('hidden_assumption','')}
Graph dependencies found: {deps}
Applicable inference rules:
{chr(10).join(rule_texts)}

Derive ONE unwanted consequence that follows from the hidden svabhava assumption.
The consequence must be something the opponent would not want to accept.
Be precise — not vague. Point to a specific contradiction.

Return ONLY valid JSON:
{{
  "consequence": "If X truly had svabhava then...",
  "why_unwanted": "The opponent cannot accept this because...",
  "contradiction_with": "This contradicts their own acceptance of..."
}}"""

    text = llm_call(prompt)
    text = text.replace("```json","").replace("```","").strip()
    try:
        result = json.loads(text)
        contradiction = (f"{result.get('consequence','')} — "
                        f"{result.get('why_unwanted','')} — "
                        f"Contradicts: {result.get('contradiction_with','')}")
        return {
            **state,
            "consequence": result.get("consequence",""),
            "contradiction": contradiction,
        }
    except Exception:
        return {
            **state,
            "consequence": "If this had svabhava it could not arise dependently",
            "contradiction": "Contradicts dependent origination which the opponent accepts"
        }


def node_check_nihilism(state: PrasangaState) -> PrasangaState:
    """
    Node 4: DETERMINISTIC check — does the argument slide into nihilism?
    This is the two-truths guard. Nagarjuna's most important move.
    Always apply.
    """
    two_truths_note = (
        "The argument shows lack of svabhava (ultimate truth), not nonexistence. "
        "Conventionally, " + state["claim"].split(" ")[0] +
        " still functions, causes effects, and matters. "
        "Emptiness enables conventional functioning — it does not abolish it. "
        "(MMK Ch.24: 'For one to whom emptiness makes sense, everything makes sense.')"
    )
    return {**state, "nihilism_check": two_truths_note}


def node_apply_self(state: PrasangaState) -> PrasangaState:
    """
    Node 5: Apply the analysis to itself — emptiness of emptiness.
    The argument itself lacks svabhava. This prevents the argument
    from becoming a new absolute. Nagarjuna: 'I have no thesis.'
    """
    self_note = (
        "The prasanga argument itself lacks svabhava — it is a conventional tool, "
        "not an ultimate truth. Emptiness is not a doctrine to be grasped. "
        "(Vigrahavyavartani: the words refuting svabhava also lack svabhava, "
        "and that is precisely why they can function.)"
    )
    return {**state, "conventional_note": self_note}


def node_synthesize(state: PrasangaState) -> PrasangaState:
    """
    Node 6: Synthesize the complete prasanga argument in natural language.
    """
    passages = state.get("passage_evidence", [])
    passage_text = "\n".join(f'"{p}"' for p in passages[:2]) if passages else ""

    prompt = f"""You are Nagarjuna's student. Synthesize this prasanga argument clearly.

Original claim: "{state['claim']}"
Hidden assumption: {state.get('hidden_assumption','')}
Unwanted consequence: {state.get('consequence','')}
Contradiction: {state.get('contradiction','')}
Two truths guard: {state.get('nihilism_check','')}
Self-application: {state.get('conventional_note','')}
MMK references: {state.get('mmk_references',[])}
Supporting passages:
{passage_text}

Write the complete prasanga argument in 6 clearly labeled steps.
Be rigorous but readable. Do not be preachy.
Step 6 must show what remains conventionally valid after the analysis."""

    text = llm_call(prompt, temperature=0.3)
    return {**state, "final_argument": text, "complete": True}


def should_continue(state: PrasangaState) -> str:
    if state.get("complete"):
        return END
    return "synthesize"


# ── Build and run the graph ────────────────────────────────────────────────

def build_graph():
    if not HAS_LANGGRAPH:
        return None

    g = StateGraph(PrasangaState)

    g.add_node("extract_assumption", node_extract_assumption)
    g.add_node("graph_traversal",    node_graph_traversal)
    g.add_node("derive_consequence",  node_derive_consequence)
    g.add_node("check_nihilism",      node_check_nihilism)
    g.add_node("apply_self",          node_apply_self)
    g.add_node("synthesize",          node_synthesize)

    g.set_entry_point("extract_assumption")
    g.add_edge("extract_assumption", "graph_traversal")
    g.add_edge("graph_traversal",    "derive_consequence")
    g.add_edge("derive_consequence",  "check_nihilism")
    g.add_edge("check_nihilism",      "apply_self")
    g.add_edge("apply_self",          "synthesize")
    g.add_edge("synthesize",          END)

    return g.compile()


def run_prasanga(claim: str, verbose: bool = False):
    print(f'\nApplying prasanga to: "{claim}"')
    print()

    if not HAS_LANGGRAPH:
        print("Install: pip install langgraph")
        return
    if not HAS_OLLAMA:
        print("Install: pip install ollama  then: ollama pull qwen2.5:7b")
        return

    graph = build_graph()
    initial_state = PrasangaState(
        claim=claim,
        hidden_assumption=None,
        graph_concepts=None,
        graph_dependencies=None,
        applicable_rules=None,
        consequence=None,
        contradiction=None,
        nihilism_check=None,
        conventional_note=None,
        mmk_references=None,
        passage_evidence=None,
        final_argument=None,
        complete=False
    )

    if verbose:
        steps = ["extract_assumption", "graph_traversal",
                 "derive_consequence", "check_nihilism",
                 "apply_self", "synthesize"]
        state = initial_state
        for step in steps:
            node_fn = {
                "extract_assumption": node_extract_assumption,
                "graph_traversal":    node_graph_traversal,
                "derive_consequence":  node_derive_consequence,
                "check_nihilism":      node_check_nihilism,
                "apply_self":          node_apply_self,
                "synthesize":          node_synthesize,
            }[step]
            print(f"  [{step}]...")
            state = node_fn(state)
        result = state
    else:
        result = graph.invoke(initial_state)

    print("=" * 60)
    print("PRASANGA ARGUMENT")
    print("=" * 60)
    print()
    if result.get("final_argument"):
        print(result["final_argument"])
    print()
    if result.get("mmk_references"):
        print("MMK References:")
        for ref in result["mmk_references"][:3]:
            print(f"  • {ref}")
    print()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Computational Madhyamaka — apply prasanga to any claim"
    )
    parser.add_argument("claim", nargs="?",
                        help="The claim to analyze")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show each reasoning step")
    args = parser.parse_args()

    if args.interactive:
        print("\nPrasanga Engine — Computational Madhyamaka")
        print("Enter any claim to analyze. Type 'quit' to exit.\n")
        while True:
            claim = input("Claim: ").strip()
            if claim.lower() in ("quit", "exit", "q"):
                break
            if claim:
                run_prasanga(claim, verbose=args.verbose)
    elif args.claim:
        run_prasanga(args.claim, verbose=args.verbose)
    else:
        # demo
        run_prasanga("consciousness has inherent existence", verbose=True)


if __name__ == "__main__":
    main()
