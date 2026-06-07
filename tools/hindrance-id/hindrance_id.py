"""
tools/hindrance-id/hindrance_id.py

Maps a meditation experience description to one of the five hindrances.
Uses Ollama for identification + graph-constrained passage retrieval
for relevant sutta references.

Usage:
    python hindrance_id.py "My mind keeps wandering to what I need to do later"
    python hindrance_id.py --interactive
"""

import sys
import argparse

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent))
from core.llm import DharmaLLM
from core.rag import GraphRAG

HINDRANCE_TO_CONCEPT = {
    "sensual_desire":       "five_aggregates",
    "ill_will":             "pratityasamutpada",
    "sloth_torpor":         "five_aggregates",
    "restlessness_worry":   "twelve_nidanas",
    "doubt":                "two_truths",
    "mixed":                "five_aggregates",
    "none":                 None,
}

HINDRANCE_LABELS = {
    "sensual_desire":     "Sensual Desire (kāmacchanda)",
    "ill_will":           "Ill Will (byāpāda)",
    "sloth_torpor":       "Sloth and Torpor (thīnamiddha)",
    "restlessness_worry": "Restlessness and Worry (uddhaccakukkucca)",
    "doubt":              "Doubt (vicikicchā)",
    "mixed":              "Mixed hindrances",
    "none":               "No hindrance identified",
}

ANTIDOTES = {
    "sensual_desire":     "Contemplation of the unattractive (asubha). Reflection on impermanence of pleasant objects.",
    "ill_will":           "Cultivation of metta (loving-kindness). Reflection on karma.",
    "sloth_torpor":       "Increasing effort. Contemplating the perception of light. Standing meditation.",
    "restlessness_worry": "Calming. Focusing on the breath as an anchor. Recollecting virtue.",
    "doubt":              "Study of the Dhamma. Asking questions of a teacher. Reviewing the path.",
}


def identify_hindrance(experience, model="qwen2.5:7b"):
    llm = DharmaLLM(model=model)
    rag = GraphRAG()

    print(f"\nAnalyzing: '{experience[:80]}...'" if len(experience) > 80
          else f"\nAnalyzing: '{experience}'")
    print()

    result = llm.identify_hindrance(experience)

    hindrance   = result.get("hindrance", "none")
    confidence  = result.get("confidence", 0.0)
    explanation = result.get("explanation", "")
    antidote    = result.get("antidote", "")
    sutta_ref   = result.get("sutta_reference", "")

    label = HINDRANCE_LABELS.get(hindrance, hindrance)
    print(f"  Hindrance: {label}")
    print(f"  Confidence: {int(confidence * 100)}%")
    print()
    print(f"  {explanation}")
    print()

    if antidote:
        print(f"  Traditional antidote:")
        print(f"  {antidote}")
        print()

    if sutta_ref:
        print(f"  Sutta reference: {sutta_ref}")
        print()

    # retrieve related passages from the graph
    concept_id = HINDRANCE_TO_CONCEPT.get(hindrance)
    if concept_id:
        passages = rag.retrieve_constrained(concept_id, hops=1, top_n=2)
        if passages:
            print("  Relevant passages from corpus:")
            for p in passages:
                print(f"  [{p['text_id']}]")
                print(f"  {p['text'][:200]}...")
                print()

    # daily reflection
    reflection = llm.generate_reflection(
        f"The hindrance of {label}: {explanation}",
        tradition="theravada"
    )
    print(f"  Contemplation for today:")
    print(f"  {reflection}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Identify meditation hindrances from experience description"
    )
    parser.add_argument("experience", nargs="?",
                        help="Description of your meditation experience")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--interactive", "-i", action="store_true")
    args = parser.parse_args()

    if args.interactive:
        print("\nHindrance Identifier — describe your meditation experience")
        print("Type 'quit' to exit\n")
        while True:
            exp = input("Experience: ").strip()
            if exp.lower() in ("quit", "exit", "q"):
                break
            if exp:
                identify_hindrance(exp, args.model)
    elif args.experience:
        identify_hindrance(args.experience, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
