"""
tools/sutta-verifier/sutta_verifier.py

Checks whether a Buddhist quote is actually in the Pali Canon.
Common problem: quotes attributed to the Buddha that are not in any text.

Usage:
    python sutta_verifier.py "You yourself must strive"
    python sutta_verifier.py "The mind is everything. What you think you become."
    python sutta_verifier.py --interactive
"""

import sys
import argparse
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent))

from core.llm import DharmaLLM
from core.rag import GraphRAG

VERIFY_PROMPT = """You are a Pali Canon scholar with deep knowledge of the Tipitaka
and its translations. A user wants to know if a quote is genuinely from the Buddhist
canon or misattributed.

Common misattributed quotes include:
- "The mind is everything. What you think you become." — NOT in Pali Canon
- "Three things cannot be long hidden: the sun, the moon, and the truth." — NOT authentic
- "Peace comes from within. Do not seek it without." — NOT authentic
- "You yourself must strive" — IS authentic (Dhp 276)
- "Hatred is never appeased by hatred" — IS authentic (Dhp 5)

Return ONLY valid JSON:
{{
  "quote": "{quote}",
  "verdict": "authentic/misattributed/uncertain/partial",
  "confidence": 0.0-1.0,
  "explanation": "2-3 sentences",
  "actual_source": "sutta name and reference if authentic, else null",
  "actual_translation": "more accurate translation if the quote is distorted, else null",
  "similar_authentic": "closest authentic quote if misattributed",
  "suttacentral_url": "URL if known, else null"
}}

Quote to verify: {quote}"""

SUSPICIOUS_QUOTES = [
    "The mind is everything",
    "Peace comes from within",
    "Three things cannot be long hidden",
    "Thousands of candles can be lit",
    "Every morning we are born again",
    "If you truly loved yourself",
    "Do not dwell in the past",
    "You only lose what you cling to",
]


def verify_quote(quote, model="qwen2.5:7b"):
    llm = DharmaLLM(model=model)
    rag = GraphRAG()

    print(f'\nVerifying: "{quote[:80]}{"..." if len(quote) > 80 else ""}"')

    from core.llm import DharmaLLM as _LLM
    import ollama, json

    prompt = VERIFY_PROMPT.format(quote=quote)
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1}
        )
        text = response["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
    except Exception as e:
        print(f"  Error: {e}")
        return None

    verdict    = result.get("verdict", "uncertain")
    confidence = result.get("confidence", 0.0)
    explanation = result.get("explanation", "")

    icons = {"authentic": "✓", "misattributed": "✗",
             "uncertain": "?", "partial": "~"}
    icon = icons.get(verdict, "?")

    print(f"\n  {icon} {verdict.upper()} (confidence: {int(confidence*100)}%)")
    print(f"\n  {explanation}")

    if result.get("actual_source"):
        print(f"\n  Source: {result['actual_source']}")
    if result.get("suttacentral_url"):
        print(f"  URL: {result['suttacentral_url']}")
    if result.get("actual_translation"):
        print(f"\n  More accurate translation:")
        print(f"  \"{result['actual_translation']}\"")
    if result.get("similar_authentic"):
        print(f"\n  Closest authentic quote:")
        print(f"  \"{result['similar_authentic']}\"")

    # try to find in passage corpus
    if verdict == "authentic":
        passages = rag.retrieve_keyword(quote[:50], top_n=2)
        if passages:
            print(f"\n  Found in corpus:")
            for p in passages:
                print(f"  [{p['text_id']}] {p['text'][:200]}...")

    print()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Verify whether a quote is actually in the Buddhist canon"
    )
    parser.add_argument("quote", nargs="?")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--check-suspicious", action="store_true",
                        help="Check a list of commonly misattributed quotes")
    args = parser.parse_args()

    if args.check_suspicious:
        print("Checking commonly misattributed Buddhist quotes...\n")
        for q in SUSPICIOUS_QUOTES:
            verify_quote(q, args.model)
    elif args.interactive:
        print('\nSutta Verifier — type a quote to check, or "quit" to exit\n')
        while True:
            quote = input("Quote: ").strip().strip('"').strip("'")
            if quote.lower() in ("quit", "exit", "q"):
                break
            if quote:
                verify_quote(quote, args.model)
    elif args.quote:
        verify_quote(args.quote, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
