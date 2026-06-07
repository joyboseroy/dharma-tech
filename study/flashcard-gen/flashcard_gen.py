"""
study/flashcard-gen/flashcard_gen.py

Generates Anki-compatible flashcard decks from the Buddhist concept graph.
Cards are ordered by prerequisite — you see anatta before sunyata,
five aggregates before Heart Sutra, two truths before prasanga.

Requires: pip install genanki

Usage:
    python flashcard_gen.py                          # all concepts
    python flashcard_gen.py --tradition madhyamaka   # one tradition
    python flashcard_gen.py --concept sunyata        # one concept + neighbours
    python flashcard_gen.py --with-passages          # include text passages
    python flashcard_gen.py --output my_deck.apkg
"""

import sys
import json
import random
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.rag import GraphRAG

try:
    import genanki
    HAS_GENANKI = True
except ImportError:
    HAS_GENANKI = False

DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Prerequisite ordering — cards in this order
CONCEPT_ORDER = [
    # Theravada foundation
    "five_aggregates",
    "twelve_nidanas",
    "anatta",
    "anatta_of_persons",
    "pratityasamutpada",
    "two_truths_theravada",
    # Mahayana extension
    "anatta_of_dharmas",
    "abhidharma_realism",
    "skillful_means",
    "bodhichitta",
    "three_kayas",
    # Madhyamaka
    "svabhava",
    "sunyata",
    "two_truths",
    "prasanga",
    "dependent_designation",
    "emptiness_of_emptiness",
    "nihilism_extreme",
    "eternalism_extreme",
    "dharmadhatu",
    "nonduality",
    # Yogacara
    "alayavijnana",
    "three_natures",
    "cittamatra",
    "tathagatagarbha",
]

TRADITION_FILTER = {
    "theravada": ["five_aggregates", "twelve_nidanas", "anatta",
                  "anatta_of_persons", "pratityasamutpada",
                  "two_truths_theravada", "abhidharma_realism"],
    "madhyamaka": ["svabhava", "sunyata", "two_truths", "prasanga",
                   "dependent_designation", "emptiness_of_emptiness",
                   "nihilism_extreme", "eternalism_extreme",
                   "dharmadhatu", "nonduality"],
    "yogacara": ["alayavijnana", "three_natures", "cittamatra",
                 "tathagatagarbha"],
    "mahayana": ["anatta_of_dharmas", "skillful_means", "bodhichitta",
                 "three_kayas", "nonduality", "tathagatagarbha"],
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


def make_front(concept):
    """Card front — question side."""
    parts = []
    label = concept["label"]
    alts  = concept.get("label_alt", [])

    parts.append(f"<h2>{label}</h2>")

    terms = []
    if concept.get("sanskrit"):
        terms.append(f"<em>Sanskrit:</em> {concept['sanskrit']}")
    if concept.get("pali"):
        terms.append(f"<em>Pāli:</em> {concept['pali']}")
    if concept.get("tibetan"):
        terms.append(f"<em>Tibetan:</em> {concept['tibetan']}")
    if terms:
        parts.append("<p style='color:#666;font-size:0.9em'>" +
                     " &nbsp;|&nbsp; ".join(terms) + "</p>")

    if alts:
        parts.append(f"<p style='color:#888;font-size:0.85em'>"
                     f"Also known as: {', '.join(alts[:3])}</p>")

    tradition = concept.get("tradition", [])
    if isinstance(tradition, list):
        tradition_str = " · ".join(tradition)
    else:
        tradition_str = tradition
    if tradition_str:
        parts.append(f"<p style='color:#888;font-size:0.85em'>"
                     f"Tradition: {tradition_str}</p>")

    return "\n".join(parts)


def make_back(concept, passages=None):
    """Card back — answer side."""
    parts = []

    definition = concept.get("definition", "")
    if definition:
        parts.append(f"<p>{definition}</p>")

    category = concept.get("category", "")
    if category:
        parts.append(f"<p style='color:#666;font-size:0.85em'>"
                     f"Category: {category.replace('_', ' ')}</p>")

    key_texts = concept.get("key_texts", [])
    if key_texts:
        texts_str = ", ".join(t.replace("_", " ").title()
                              for t in key_texts[:3])
        parts.append(f"<p style='color:#666;font-size:0.85em'>"
                     f"Key texts: {texts_str}</p>")

    if passages:
        parts.append("<hr>")
        parts.append("<p style='font-size:0.85em;color:#444'>"
                     "<em>From the texts:</em></p>")
        for p in passages[:1]:
            text = p["text"][:300].replace("<", "&lt;").replace(">", "&gt;")
            src  = p["text_id"].replace("_", " ").title()
            parts.append(f"<p style='font-size:0.85em;color:#555'>"
                         f"[{src}] {text}...</p>")

    return "\n".join(parts)


def generate_deck(tradition=None, concept_id=None,
                  with_passages=False, output="dharma_concepts.apkg"):
    if not HAS_GENANKI:
        print("Install genanki: pip install genanki")
        print("Printing cards to terminal instead.\n")

    concepts_list = load_jsonl(DATA_DIR / "concepts.jsonl")
    concepts = {c["id"]: c for c in concepts_list}

    rag = GraphRAG() if with_passages else None

    # determine which concepts to include
    if concept_id and concept_id in concepts:
        # this concept + immediate neighbours
        edges = load_jsonl(DATA_DIR / "edges.jsonl")
        related = {concept_id}
        for e in edges:
            if e["source"] == concept_id:
                related.add(e["target"])
            if e["target"] == concept_id:
                related.add(e["source"])
        order = [c for c in CONCEPT_ORDER if c in related]
    elif tradition and tradition in TRADITION_FILTER:
        order = TRADITION_FILTER[tradition]
    else:
        order = CONCEPT_ORDER

    order = [c for c in order if c in concepts]

    if not HAS_GENANKI:
        # terminal output
        print(f"Generating {len(order)} flashcards\n")
        print("=" * 60)
        for i, cid in enumerate(order, 1):
            c = concepts[cid]
            passages = rag.retrieve(cid, top_n=1) if rag else []
            print(f"\nCard {i}: {c['label']}")
            print("-" * 40)
            print("FRONT:")
            print(f"  {c['label']} | {c.get('sanskrit','')}")
            print("BACK:")
            print(f"  {c.get('definition','')[:200]}")
            if passages:
                print(f"  [{passages[0]['text_id']}] "
                      f"{passages[0]['text'][:150]}...")
        print(f"\n{len(order)} cards generated")
        return

    # build Anki deck
    deck_id = random.randrange(1 << 30, 1 << 31)
    model_id = random.randrange(1 << 30, 1 << 31)

    css = """
    .card { font-family: serif; font-size: 16px; max-width: 600px; margin: auto; }
    h2 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 8px; }
    p { line-height: 1.6; color: #333; }
    hr { border: none; border-top: 1px solid #eee; margin: 12px 0; }
    """

    model = genanki.Model(
        model_id,
        "Dharma Concept",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
        ],
        templates=[{
            "name": "Concept Card",
            "qfmt": "{{Front}}",
            "afmt": "{{FrontSide}}<hr>{{Back}}",
        }],
        css=css
    )

    deck_name = f"Dharma Concepts"
    if tradition:
        deck_name += f" — {tradition.title()}"
    if concept_id:
        deck_name += f" — {concepts[concept_id]['label']} cluster"

    deck = genanki.Deck(deck_id, deck_name)

    for cid in order:
        c = concepts[cid]
        passages = rag.retrieve(cid, top_n=1) if rag else []
        note = genanki.Note(
            model=model,
            fields=[make_front(c), make_back(c, passages)]
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output)
    print(f"Generated {len(order)}-card Anki deck: {output}")
    print(f"Import into Anki: File → Import → select {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Anki flashcard deck from Buddhist concept graph"
    )
    parser.add_argument("--tradition",
                        choices=["theravada", "madhyamaka", "mahayana", "yogacara"])
    parser.add_argument("--concept",
                        help="Generate cards for one concept and its neighbours")
    parser.add_argument("--with-passages", action="store_true",
                        help="Include text passages on card backs")
    parser.add_argument("--output", default="dharma_concepts.apkg")
    args = parser.parse_args()

    generate_deck(
        tradition=args.tradition,
        concept_id=args.concept,
        with_passages=args.with_passages,
        output=args.output
    )


if __name__ == "__main__":
    main()
