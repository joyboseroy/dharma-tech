"""
core/llm.py — Ollama wrapper with Buddhist-specific prompt templates
All dharma-tech agents import from here.
"""

import json

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


DEFAULT_MODEL = "qwen2.5:7b"

# ── PROMPT TEMPLATES ───────────────────────────────────────────────────────

IDENTIFY_TEXT = """You are a Buddhist scholar. Identify the text from the query.
Return ONLY valid JSON:
{{
  "name": "canonical English name",
  "alternate_names": ["list"],
  "author": "or null",
  "tradition": "theravada/mahayana/vajrayana/zen/madhyamaka/general",
  "canonical_ref": "DN 2 / Toh 107 / T 475 / null",
  "suttacentral_ref": "dn2 / mn36 / null",
  "toh_number": "Toh107 / null",
  "language_original": "pali/sanskrit/tibetan/chinese",
  "brief_description": "one sentence",
  "likely_free": true/false,
  "free_note": "brief honest note on availability"
}}
Query: {query}"""

IDENTIFY_CONCEPT = """You are a Buddhist scholar. Given a user's description,
identify the most relevant Buddhist philosophical concept.
Return ONLY valid JSON:
{{
  "concept_id": "snake_case_id matching standard Buddhist terms",
  "label": "English label",
  "tradition": "which tradition primarily uses this",
  "confidence": 0.0-1.0,
  "alternate_concepts": ["other possible matches"]
}}
Description: {description}"""

HINDRANCE_IDENTIFIER = """You are a Theravada meditation teacher.
The user describes a meditation experience. Identify which of the five
hindrances is present, if any. Be specific and compassionate.
Return ONLY valid JSON:
{{
  "hindrance": "sensual_desire/ill_will/sloth_torpor/restlessness_worry/doubt/none/mixed",
  "confidence": 0.0-1.0,
  "explanation": "2-3 sentences explaining the identification",
  "antidote": "traditional antidote from the Pali texts",
  "sutta_reference": "relevant sutta if known, else null"
}}
Experience: {experience}"""

PRASANGA_GENERATOR = """You are a Madhyamaka philosopher trained in the prasanga method.
Generate a formal prasanga (consequence) argument against the given position.
Structure:
1. State the opponent's position
2. Derive the unwanted consequence
3. Show this contradicts their own accepted premise
4. Conclude the position is untenable
5. Note what is still conventionally valid

Return ONLY valid JSON:
{{
  "position": "the position being examined",
  "hidden_assumption": "the svabhava assumption it rests on",
  "consequence": "the absurd result that follows",
  "contradiction": "what this contradicts",
  "conclusion": "therefore...",
  "conventional_note": "what remains true conventionally",
  "mmk_reference": "closest MMK chapter if applicable"
}}
Position: {position}"""

TWO_TRUTHS_CLASSIFIER = """You are a Madhyamaka philosopher.
Classify whether this statement operates at the conventional or ultimate level of truth,
or whether it conflates the two.
Return ONLY valid JSON:
{{
  "level": "conventional/ultimate/conflated/both",
  "explanation": "2-3 sentences",
  "tradition_note": "does this differ across Madhyamaka schools?"
}}
Statement: {statement}"""

PRECEPT_CHECKER = """You are a Buddhist ethics teacher familiar with both
Theravada and Mahayana ethical frameworks.
Analyze this situation against the five precepts.
Return ONLY valid JSON:
{{
  "precepts_relevant": ["list of relevant precepts"],
  "assessment": "clear/borderline/violation/context_dependent",
  "explanation": "3-4 sentences of reasoning",
  "tradition_differences": "how Theravada vs Mahayana might differ",
  "skillful_alternative": "what might be more skillful"
}}
Situation: {situation}"""

TRADITION_AWARE_ANSWER = """You are a Buddhist scholar. Answer this question
from the perspective of the {tradition} tradition only.
Ground your answer in the provided graph context and passages.
Do not assert claims not supported by the context.
If the question touches a live doctrinal tension, present both sides.

Graph context:
{graph_context}

Relevant passages:
{passages}

Question: {question}

Answer (3-5 sentences, tradition-scoped, source-grounded):"""

SUMMARIZE_SUTTA = """You are a Buddhist scholar. Summarize this text at three levels:
1. Literal: what is literally being said
2. Philosophical: the deeper doctrinal point
3. Practical: how this applies to daily practice or meditation

Return ONLY valid JSON:
{{
  "title": "text title",
  "tradition": "tradition",
  "literal": "2-3 sentences",
  "philosophical": "2-3 sentences",
  "practical": "2-3 sentences",
  "key_terms": ["Pali/Sanskrit terms with brief definitions"],
  "related_texts": ["other texts that discuss this theme"]
}}
Text: {text}"""

REFLECTION_GENERATOR = """You are a dharma teacher generating a contemplation prompt.
Based on this Buddhist concept or passage, generate a single open inquiry question
that a practitioner can hold during their day.
The question should:
- Open rather than close inquiry
- Be applicable to ordinary daily experience
- Not require Buddhist knowledge to engage with
- Avoid jargon

Concept/passage: {input}
Tradition: {tradition}

Return just the question, nothing else."""


# ── LLM CLASS ─────────────────────────────────────────────────────────────

class DharmaLLM:

    def __init__(self, model=DEFAULT_MODEL):
        self.model = model
        if not HAS_OLLAMA:
            print(f"[warn] ollama not installed. Install: pip install ollama")
            print(f"[warn] Then pull model: ollama pull {model}")

    def _call(self, prompt, temperature=0.1, expect_json=True):
        if not HAS_OLLAMA:
            raise RuntimeError("ollama not available")
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        text = response["message"]["content"].strip()
        if expect_json:
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        return text

    def identify_text(self, query):
        return self._call(IDENTIFY_TEXT.format(query=query))

    def identify_concept(self, description):
        return self._call(IDENTIFY_CONCEPT.format(description=description))

    def identify_hindrance(self, experience):
        return self._call(HINDRANCE_IDENTIFIER.format(experience=experience))

    def prasanga(self, position):
        return self._call(PRASANGA_GENERATOR.format(position=position))

    def classify_two_truths(self, statement):
        return self._call(TWO_TRUTHS_CLASSIFIER.format(statement=statement))

    def check_precept(self, situation):
        return self._call(PRECEPT_CHECKER.format(situation=situation))

    def summarize_text(self, text):
        return self._call(SUMMARIZE_SUTTA.format(text=text[:3000]))

    def answer_with_tradition_scope(self, question, tradition,
                                    graph_context="", passages=""):
        prompt = TRADITION_AWARE_ANSWER.format(
            tradition=tradition,
            graph_context=graph_context,
            passages=passages,
            question=question
        )
        return self._call(prompt, temperature=0.3, expect_json=False)

    def generate_reflection(self, input_text, tradition="general"):
        prompt = REFLECTION_GENERATOR.format(
            input=input_text, tradition=tradition
        )
        return self._call(prompt, temperature=0.7, expect_json=False)
