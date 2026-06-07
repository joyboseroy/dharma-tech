"""
tools/tradition-compare/tradition_compare.py

Compare how different Buddhist traditions handle the same concept or question.
Uses the emptiness-graph's tradition-scoped edges — not LLM generation from
training data. Every comparison is grounded in actual typed edges and passages.

This is the tool that most directly shows what the graph adds over plain RAG:
the same concept appears differently in Theravada, Madhyamaka, Yogacara, and
Mahayana, and the graph encodes exactly how and why.

Usage:
    python tradition_compare.py sunyata
    python tradition_compare.py "dependent origination"
    python tradition_compare.py consciousness --traditions theravada madhyamaka yogacara
    python tradition_compare.py --question "Is there a self?"
    python tradition_compare.py --interactive
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.rag import GraphRAG

DATA_DIR = Path(__file__).parent.parent.parent / "data"

TRADITIONS = ["theravada", "madhyamaka", "yogacara", "mahayana",
              "prajnaparamita", "prasangika", "mixed"]

TRADITION_DESCRIPTIONS = {
    "theravada":     "Theravada / Pali Abhidharma",
    "madhyamaka":    "Madhyamaka (Nagarjuna, Chandrakirti)",
    "yogacara":      "Yogacara (Asanga, Vasubandhu)",
    "mahayana":      "Mahayana (general)",
    "prajnaparamita":"Prajnaparamita sutras",
    "prasangika":    "Prasangika Madhyamaka (Chandrakirti)",
    "mixed":         "Cross-traditional / debated",
}

QUESTION_TO_CONCEPTS = {
    "is there a self":          ["anatta", "anatta_of_persons", "anatta_of_dharmas"],
    "what is consciousness":    ["alayavijnana", "cittamatra", "five_aggregates"],
    "what is emptiness":        ["sunyata", "svabhava", "emptiness_of_emptiness"],
    "how does karma work":      ["twelve_nidanas", "pratityasamutpada"],
    "what is dependent origination": ["pratityasamutpada", "sunyata"],
    "what is buddha nature":    ["tathagatagarbha", "nonduality", "dharmadhatu"],
    "what are the two truths":  ["two_truths", "two_truths_theravada"],
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


def find_concept(query: str, concepts: dict) -> str:
    """Find best matching concept_id from a query string."""
    query_lower = query.lower().replace(" ", "_").replace("-", "_")

    # exact match
    if query_lower in concepts:
        return query_lower

    # label match
    for cid, c in concepts.items():
        if query.lower() in c.get("label", "").lower():
            return cid
        for alt in c.get("label_alt", []):
            if query.lower() in alt.lower():
                return cid

    # partial id match
    for cid in concepts:
        if query_lower in cid:
            return cid

    return None


def compare_concept(query: str,
                    target_traditions: list = None,
                    verbose: bool = False):
    """
    Main comparison function.
    Traverses the graph by tradition tag and shows how each tradition
    relates to the concept differently.
    """
    concepts_list = load_jsonl(DATA_DIR / "concepts.jsonl")
    concepts = {c["id"]: c for c in concepts_list}
    edges = load_jsonl(DATA_DIR / "edges.jsonl")
    texts = {t["id"]: t for t in load_jsonl(DATA_DIR / "corpus_manifest.jsonl")}
    rag = GraphRAG()

    concept_id = find_concept(query, concepts)
    if not concept_id:
        print(f"\n  Concept '{query}' not found.")
        print(f"  Available: {', '.join(list(concepts.keys())[:15])}...")
        return

    c = concepts[concept_id]
    label = c["label"]
    definition = c.get("definition", "")

    print(f"\n{'='*65}")
    print(f"  {label}")
    if c.get("sanskrit"):
        print(f"  Sanskrit: {c['sanskrit']}", end="")
        if c.get("pali"):
            print(f"  |  Pali: {c['pali']}", end="")
        if c.get("tibetan"):
            print(f"  |  Tibetan: {c['tibetan']}", end="")
        print()
    print(f"{'='*65}")
    print(f"\n  {definition}\n")

    # gather edges by tradition
    by_tradition = {}
    for e in edges:
        if concept_id not in (e["source"], e["target"]):
            continue
        trad = e.get("tradition", "mixed") or "mixed"
        if target_traditions and trad not in target_traditions:
            continue
        if trad not in by_tradition:
            by_tradition[trad] = []

        other_id = e["target"] if e["source"] == concept_id else e["source"]
        other_label = (concepts.get(other_id, {}).get("label")
                       or texts.get(other_id, {}).get("title")
                       or other_id)
        direction = "→" if e["source"] == concept_id else "←"

        by_tradition[trad].append({
            "relation": e["relation"],
            "direction": direction,
            "other": other_label,
            "other_id": other_id,
            "weight": e.get("weight", 0.5),
            "notes": e.get("notes", ""),
        })

    if not by_tradition:
        print("  No tradition-specific edges found for this concept.")
        return

    # print by tradition in a meaningful order
    order = ["theravada", "prajnaparamita", "madhyamaka",
             "prasangika", "yogacara", "mahayana", "mixed"]

    for trad in order:
        if trad not in by_tradition:
            continue
        trad_name = TRADITION_DESCRIPTIONS.get(trad, trad.title())
        print(f"  ── {trad_name} ──")

        items = sorted(by_tradition[trad], key=lambda x: -x["weight"])
        for item in items:
            rel = item["relation"].replace("_", " ")
            print(f"  {item['direction']} [{rel}] {item['other']}")
            if item["notes"] and verbose:
                print(f"    {item['notes'][:200]}")
                print()
            elif item["notes"]:
                # always show first sentence
                first_sentence = item["notes"].split(".")[0] + "."
                print(f"    {first_sentence[:150]}")

        # retrieve one key passage per tradition
        trad_passages = rag._passage_in_tradition  # use internal method
        if not verbose:
            print()
            continue

        trad_text_ids = {
            "theravada":  ["anattalakkhana_sutta", "milindapanha_chariot"],
            "madhyamaka": ["mmk_nagarjuna", "sunyatasaptati_nagarjuna",
                           "bodhicharyavatara_ch9"],
            "prajnaparamita": ["heart_sutra", "diamond_sutra",
                               "ashtasahasrika_prajnaparamita"],
            "yogacara":   ["samdhinirmocana_sutra"],
            "mahayana":   ["vimalakirti_sutra"],
        }.get(trad, [])

        for text_id in trad_text_ids:
            ps = rag.passages_for_text(text_id, concept_id, top_n=1)
            if ps:
                print(f"\n  From {text_id.replace('_',' ').title()}:")
                print(f"  \"{ps[0]['text'][:250]}...\"")
                break
        print()

    # identify the key tension if any
    tensions = [e for e in edges
                if concept_id in (e["source"], e["target"])
                and e["relation"] == "tensions_with"]
    if tensions:
        print(f"  ── Live doctrinal tension ──")
        for t in tensions:
            other_id = t["target"] if t["source"] == concept_id else t["source"]
            other_label = (concepts.get(other_id, {}).get("label") or other_id)
            print(f"  {label} ↔ {other_label}")
            print(f"  {t.get('notes','')[:250]}")
        print()


def compare_question(question: str, verbose: bool = False):
    """
    Handle natural language questions by mapping to concept IDs.
    """
    q_lower = question.lower().strip("?")

    # check known mappings
    for pattern, concept_ids in QUESTION_TO_CONCEPTS.items():
        if any(w in q_lower for w in pattern.split()):
            print(f"\n  Question maps to: {concept_ids}")
            for cid in concept_ids:
                compare_concept(cid, verbose=verbose)
            return

    # fall back to treating as concept query
    compare_concept(question, verbose=verbose)


def synthesis_summary(concept_id: str):
    """
    LLM synthesis of cross-tradition differences — only called if Ollama available.
    """
    try:
        import ollama
    except ImportError:
        return

    concepts = {c["id"]: c for c in load_jsonl(DATA_DIR / "concepts.jsonl")}
    edges = load_jsonl(DATA_DIR / "edges.jsonl")

    if concept_id not in concepts:
        return

    label = concepts[concept_id]["label"]
    relevant_edges = [e for e in edges
                      if concept_id in (e["source"], e["target"])]
    edge_summary = json.dumps([
        {"relation": e["relation"], "tradition": e.get("tradition",""),
         "notes": e.get("notes","")[:150]}
        for e in relevant_edges
    ], indent=2)

    prompt = f"""You are a Buddhist scholar comparing traditions.
Based on these graph edges showing how traditions relate to {label},
write a 4-5 sentence synthesis of the key differences and agreements.
Be specific. Name the traditions and their positions.
Do not be vague.

Graph data:
{edge_summary}

Synthesis:"""

    try:
        r = ollama.chat(
            model="qwen2.5:7b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3}
        )
        print(f"  ── LLM synthesis ──")
        print(f"  {r['message']['content'].strip()}")
        print()
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Compare Buddhist traditions on any concept"
    )
    parser.add_argument("concept", nargs="?",
                        help="Concept name or ID")
    parser.add_argument("--question", "-q",
                        help="Natural language question")
    parser.add_argument("--traditions", nargs="+",
                        choices=TRADITIONS,
                        help="Filter to specific traditions")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show full notes and passages")
    parser.add_argument("--synthesize", "-s", action="store_true",
                        help="Add LLM synthesis summary (needs Ollama)")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--list", action="store_true",
                        help="List all available concepts")
    args = parser.parse_args()

    if args.list:
        concepts = load_jsonl(DATA_DIR / "concepts.jsonl")
        print("\nAvailable concepts:")
        for c in concepts:
            print(f"  {c['id']:<35} {c['label']}")
        return

    if args.interactive:
        print("\nTradition Comparator — type a concept or question, 'quit' to exit")
        print("Examples: sunyata | consciousness | 'is there a self?' | anatta\n")
        while True:
            query = input("Concept or question: ").strip()
            if query.lower() in ("quit","exit","q"):
                break
            if query.startswith("?") or "?" in query:
                compare_question(query, verbose=args.verbose)
            else:
                compare_concept(query,
                                target_traditions=args.traditions,
                                verbose=args.verbose)
            if args.synthesize:
                concepts = {c["id"]: c for c in load_jsonl(DATA_DIR / "concepts.jsonl")}
                cid = find_concept(query, concepts)
                if cid:
                    synthesis_summary(cid)
    elif args.question:
        compare_question(args.question, verbose=args.verbose)
    elif args.concept:
        compare_concept(args.concept,
                        target_traditions=args.traditions,
                        verbose=args.verbose)
        if args.synthesize:
            concepts = {c["id"]: c for c in load_jsonl(DATA_DIR / "concepts.jsonl")}
            cid = find_concept(args.concept, concepts)
            if cid:
                synthesis_summary(cid)
    else:
        # demo
        compare_concept("sunyata", verbose=False)


if __name__ == "__main__":
    main()
