"""
tools/precept-checker/precept_checker.py

Analyzes a daily life situation against the five precepts.
Gives nuanced Buddhist ethical analysis, not a binary pass/fail.
Shows differences between Theravada and Mahayana approaches.

Usage:
    python precept_checker.py "I told a small lie to spare my friend's feelings"
    python precept_checker.py "I killed a mosquito that was biting me"
    python precept_checker.py --interactive
"""

import sys
import argparse
import json
import ollama
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent))
from core.rag import GraphRAG

PRECEPTS = {
    1: "Refrain from taking life (pāṇātipātā veramaṇī)",
    2: "Refrain from taking what is not given (adinnādānā veramaṇī)",
    3: "Refrain from sexual misconduct (kāmesumicchācārā veramaṇī)",
    4: "Refrain from false speech (musāvādā veramaṇī)",
    5: "Refrain from intoxicants (surāmeraya... veramaṇī)",
}

ANALYZE_PROMPT = """You are a Buddhist ethics teacher with deep knowledge of both
Theravada Vinaya and Mahayana bodhisattva ethics.

Analyze this situation against the five precepts. Be nuanced — most situations
are not simple violations or non-violations. Consider:
- Intention (cetana) — Buddhism emphasizes intention over action
- Context and degree
- The difference between the spirit and letter of each precept
- How Theravada and Mahayana might assess this differently

Return ONLY valid JSON:
{{
  "situation": "{situation}",
  "precepts_involved": [1, 4],
  "overall_assessment": "clear/borderline/violation/context_dependent/not_applicable",
  "intention_analysis": "2 sentences on the role of intention here",
  "precept_details": [
    {{
      "precept_number": 4,
      "precept_name": "False speech",
      "relevance": "high/medium/low/none",
      "theravada_view": "2 sentences",
      "mahayana_view": "2 sentences — skillful means considerations",
      "verdict": "violation/borderline/not_violation/context_dependent"
    }}
  ],
  "skillful_alternative": "what might be more skillful if relevant",
  "relevant_teaching": "a relevant canonical teaching or principle",
  "reflection_question": "one open question to sit with"
}}

Situation: {situation}"""


def check_situation(situation, model="qwen2.5:7b"):
    rag = GraphRAG()

    print(f'\nSituation: "{situation[:100]}{"..." if len(situation) > 100 else ""}"')

    try:
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": ANALYZE_PROMPT.format(situation=situation)
            }],
            options={"temperature": 0.2}
        )
        text = response["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
    except Exception as e:
        print(f"  Error: {e}")
        return None

    assessment = result.get("overall_assessment", "unclear")
    icons = {
        "clear": "✓ Clear",
        "not_applicable": "— Not applicable",
        "borderline": "~ Borderline",
        "violation": "✗ Violation",
        "context_dependent": "? Context dependent"
    }
    print(f"\n  Assessment: {icons.get(assessment, assessment)}")

    intention = result.get("intention_analysis", "")
    if intention:
        print(f"\n  Intention: {intention}")

    for detail in result.get("precept_details", []):
        num = detail.get("precept_number")
        name = detail.get("precept_name", "")
        if num:
            print(f"\n  Precept {num} — {name}")
            print(f"  Theravada: {detail.get('theravada_view','')}")
            print(f"  Mahayana:  {detail.get('mahayana_view','')}")

    alt = result.get("skillful_alternative")
    if alt:
        print(f"\n  More skillful alternative: {alt}")

    teaching = result.get("relevant_teaching")
    if teaching:
        print(f"\n  Relevant teaching: {teaching}")

    reflection = result.get("reflection_question")
    if reflection:
        print(f"\n  Reflection: {reflection}")

    # retrieve related passages
    passages = rag.retrieve_constrained("anatta", hops=1, top_n=2)
    if passages:
        print(f"\n  Related passages:")
        for p in passages[:1]:
            print(f"  [{p['text_id']}] {p['text'][:200]}...")

    print()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a situation against the five Buddhist precepts"
    )
    parser.add_argument("situation", nargs="?",
                        help="Describe the situation to analyze")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--interactive", "-i", action="store_true")
    args = parser.parse_args()

    if args.interactive:
        print("\nPrecept Checker — describe a situation for ethical analysis")
        print("Type 'quit' to exit\n")
        while True:
            sit = input("Situation: ").strip()
            if sit.lower() in ("quit", "exit", "q"):
                break
            if sit:
                check_situation(sit, args.model)
    elif args.situation:
        check_situation(args.situation, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
