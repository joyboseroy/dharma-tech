"""
core/rag.py — Graph-constrained RAG base class
Standard RAG finds passages by keyword/embedding.
Graph-RAG finds passages constrained by philosophical structure.
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


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


class GraphRAG:
    """
    Retrieves passages constrained by the philosophical graph.

    Standard RAG: find passages containing keywords.
    Graph-RAG: find concepts relevant to query via graph traversal,
               then retrieve only passages linked to those concepts.

    This means a question about "emptiness of emptiness" retrieves
    passages tagged with that specific concept, not all passages
    containing the word "emptiness".
    """

    def __init__(self, texts_dir=None):
        self.passages     = load_jsonl(DATA_DIR / "passages.jsonl")
        self.pedges       = load_jsonl(DATA_DIR / "passage_edges.jsonl")
        self.concepts     = {c["id"]: c for c in load_jsonl(DATA_DIR / "concepts.jsonl")}
        self.edges        = load_jsonl(DATA_DIR / "edges.jsonl")
        self._build_index()

    def _build_index(self):
        # concept -> set of passage ids
        self.concept_to_pids = {}
        for e in self.pedges:
            c = e["target"]
            if c not in self.concept_to_pids:
                self.concept_to_pids[c] = set()
            self.concept_to_pids[c].add(e["source"])

        # passage id -> passage
        self.pid_to_passage = {p["id"]: p for p in self.passages}

        # edge index: source -> [(target, relation, weight, tradition)]
        self.edge_index = {}
        for e in self.edges:
            s = e["source"]
            if s not in self.edge_index:
                self.edge_index[s] = []
            self.edge_index[s].append((
                e["target"], e["relation"],
                e.get("weight", 0.5), e.get("tradition", "")
            ))

    def retrieve(self, concept_id, top_n=5, tradition=None):
        """
        Retrieve passages for a concept.
        Optionally filter by tradition.
        """
        pids = self.concept_to_pids.get(concept_id, set())
        passages = [self.pid_to_passage[pid] for pid in pids
                    if pid in self.pid_to_passage]
        if tradition:
            passages = [p for p in passages
                        if self._passage_in_tradition(p, tradition)]
        # rank by number of relevant concepts mentioned
        passages.sort(key=lambda p: len(p.get("concepts_mentioned", [])),
                      reverse=True)
        return passages[:top_n]

    def retrieve_constrained(self, concept_id, hops=1,
                              min_weight=0.7, top_n=8, tradition=None):
        """
        Retrieve passages for a concept AND its high-weight neighbours.
        This is the core graph-RAG operation:
        - traverse the philosophical graph from concept_id
        - collect all concepts within `hops` via edges with weight >= min_weight
        - retrieve passages tagged with any of those concepts
        - rank by how many relevant concepts each passage mentions
        """
        relevant_concepts = self._get_neighbourhood(
            concept_id, hops=hops, min_weight=min_weight
        )

        # collect all passage ids for relevant concepts
        all_pids = set()
        for c in relevant_concepts:
            all_pids.update(self.concept_to_pids.get(c, set()))

        passages = [self.pid_to_passage[pid] for pid in all_pids
                    if pid in self.pid_to_passage]

        if tradition:
            passages = [p for p in passages
                        if self._passage_in_tradition(p, tradition)]

        # rank by overlap with relevant concept set
        def score(p):
            mentioned = set(p.get("concepts_mentioned", []))
            return len(mentioned & relevant_concepts)

        passages.sort(key=score, reverse=True)
        return passages[:top_n]

    def retrieve_keyword(self, query, top_n=5):
        """
        Fallback: simple keyword search across passage text.
        Less precise than concept-constrained retrieval.
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        scored = []
        for p in self.passages:
            text_words = set(re.findall(r'\w+', p["text"].lower()))
            overlap = len(query_words & text_words)
            if overlap > 0:
                scored.append((overlap, p))
        scored.sort(key=lambda x: -x[0])
        return [p for _, p in scored[:top_n]]

    def passages_for_text(self, text_id, concept_id=None, top_n=10):
        """Get passages from a specific source text, optionally filtered by concept."""
        passages = [p for p in self.passages if p["text_id"] == text_id]
        if concept_id:
            passages = [p for p in passages
                        if concept_id in p.get("concepts_mentioned", [])]
        return passages[:top_n]

    def both_sides_of_tension(self, concept_a, concept_b, top_n=3):
        """
        For a tensions_with edge, retrieve passages from both sides.
        Useful for presenting multiple perspectives without collapsing them.
        """
        side_a = self.retrieve(concept_a, top_n=top_n)
        side_b = self.retrieve(concept_b, top_n=top_n)
        return {"side_a": side_a, "side_b": side_b}

    def _get_neighbourhood(self, start, hops=1, min_weight=0.7):
        """BFS over the edge index to collect nearby concepts."""
        visited = {start}
        frontier = {start}
        for _ in range(hops):
            next_frontier = set()
            for node in frontier:
                for target, relation, weight, tradition in self.edge_index.get(node, []):
                    if weight >= min_weight and target not in visited:
                        visited.add(target)
                        next_frontier.add(target)
            frontier = next_frontier
        return visited

    def _passage_in_tradition(self, passage, tradition):
        """Check if a passage's source text belongs to a tradition."""
        text_id = passage.get("text_id", "")
        tradition_map = {
            "theravada": ["anattalakkhana_sutta", "milindapanha_chariot"],
            "madhyamaka": ["mmk_nagarjuna", "sunyatasaptati_nagarjuna",
                           "bodhicharyavatara_ch9"],
            "prajnaparamita": ["heart_sutra", "diamond_sutra",
                               "ashtasahasrika_prajnaparamita"],
            "yogacara": ["samdhinirmocana_sutra"],
            "mahayana": ["vimalakirti_sutra", "heart_sutra", "diamond_sutra"],
        }
        return text_id in tradition_map.get(tradition, [])

    def format_for_prompt(self, passages, max_chars=2000):
        """Format passages for inclusion in an LLM prompt."""
        lines = []
        total = 0
        for p in passages:
            entry = f"[{p['text_id']}] {p['text'][:400]}"
            if total + len(entry) > max_chars:
                break
            lines.append(entry)
            total += len(entry)
        return "\n\n".join(lines)
