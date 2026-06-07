"""
core/db.py — Shared FalkorDB connection and Buddhist graph helpers
All dharma-tech projects import from here.
"""

import json
from pathlib import Path

try:
    from falkordb import FalkorDB as _FalkorDB
    HAS_FALKOR = True
except ImportError:
    HAS_FALKOR = False

DATA_DIR = Path(__file__).parent.parent / "data"


class DharmaDB:
    """
    Thin wrapper around FalkorDB for Buddhist graph operations.
    Falls back to in-memory NetworkX if FalkorDB not available.
    """

    def __init__(self, host="localhost", port=6379):
        self.host = host
        self.port = port
        self._client = None
        self._graphs = {}
        self._nx_graphs = {}

    def _connect(self):
        if self._client is None:
            if not HAS_FALKOR:
                raise RuntimeError(
                    "FalkorDB not installed. Run: pip install falkordb\n"
                    "Or start Docker: docker run -p 6379:6379 falkordb/falkordb"
                )
            self._client = _FalkorDB(host=self.host, port=self.port)
        return self._client

    def graph(self, name="emptiness"):
        if name not in self._graphs:
            self._graphs[name] = self._connect().select_graph(name)
        return self._graphs[name]

    def query(self, cypher, graph_name="emptiness", params=None):
        g = self.graph(graph_name)
        result = g.query(cypher, params or {})
        return result.result_set

    def load_emptiness_graph(self, graph_name="emptiness"):
        """Load the emptiness-graph data files into FalkorDB."""
        g = self.graph(graph_name)

        concepts = self._load_jsonl(DATA_DIR / "concepts.jsonl")
        texts    = self._load_jsonl(DATA_DIR / "corpus_manifest.jsonl")
        edges    = self._load_jsonl(DATA_DIR / "edges.jsonl")

        for c in concepts:
            label      = c["label"].replace("'", "\\'")
            definition = c.get("definition", "")[:300].replace("'", "\\'")
            tradition  = str(c.get("tradition", [])).replace("'", "\\'")
            category   = c.get("category", "").replace("'", "\\'")
            g.query(
                f"MERGE (:Concept {{id:'{c['id']}', label:'{label}', "
                f"tradition:'{tradition}', category:'{category}', "
                f"definition:'{definition}'}})"
            )

        for t in texts:
            title     = t["title"].replace("'", "\\'")
            tradition = t.get("tradition", "").replace("'", "\\'")
            g.query(
                f"MERGE (:Text {{id:'{t['id']}', title:'{title}', "
                f"tradition:'{tradition}'}})"
            )

        for e in edges:
            rel       = e["relation"].upper().replace("-", "_")
            tradition = e.get("tradition", "").replace("'", "\\'")
            weight    = e.get("weight", 0.5)
            notes     = e.get("notes", "")[:200].replace("'", "\\'")
            g.query(
                f"MATCH (a {{id:'{e['source']}'}}) "
                f"MATCH (b {{id:'{e['target']}'}}) "
                f"MERGE (a)-[:{rel} {{tradition:'{tradition}', "
                f"weight:{weight}, notes:'{notes}'}}]->(b)"
            )

        print(f"Loaded emptiness graph into FalkorDB graph '{graph_name}'")
        result = g.query("MATCH (n) RETURN count(n) AS nodes")
        print(f"  Nodes: {result.result_set[0][0]}")
        result = g.query("MATCH ()-[r]->() RETURN count(r) AS edges")
        print(f"  Edges: {result.result_set[0][0]}")

    def passages_for_concept(self, concept_id, top_n=5, texts_dir=None):
        """Return top passages mentioning a concept, from local files."""
        pedges   = self._load_jsonl(DATA_DIR / "passage_edges.jsonl")
        passages = self._load_jsonl(DATA_DIR / "passages.jsonl")

        pids = {e["source"] for e in pedges if e["target"] == concept_id}
        results = [p for p in passages if p["id"] in pids]
        return results[:top_n]

    def concept_neighbours(self, concept_id, graph_name="emptiness"):
        """Get all concepts connected to this one with relation types."""
        rows = self.query(
            f"MATCH (n {{id:'{concept_id}'}})-[r]-(m) "
            f"RETURN m.id, m.label, type(r), r.tradition, r.weight",
            graph_name=graph_name
        )
        return [
            {"id": r[0], "label": r[1], "relation": r[2],
             "tradition": r[3], "weight": r[4]}
            for r in rows
        ]

    def tradition_subgraph(self, tradition, graph_name="emptiness"):
        """Get all edges belonging to a tradition."""
        rows = self.query(
            f"MATCH (a)-[r]->(b) "
            f"WHERE r.tradition = '{tradition}' "
            f"RETURN a.label, type(r), b.label, r.weight "
            f"ORDER BY r.weight DESC",
            graph_name=graph_name
        )
        return [{"source": r[0], "relation": r[1], "target": r[2], "weight": r[3]}
                for r in rows]

    def tensions(self, graph_name="emptiness"):
        """Get all doctrinal tensions."""
        rows = self.query(
            "MATCH (a)-[r:TENSIONS_WITH]->(b) "
            "RETURN a.label, b.label, r.notes",
            graph_name=graph_name
        )
        return [{"a": r[0], "b": r[1], "notes": r[2]} for r in rows]

    def path_between(self, source_id, target_id, max_hops=4,
                     graph_name="emptiness"):
        """Find shortest path between two concepts."""
        rows = self.query(
            f"MATCH path = (a {{id:'{source_id}'}})-[*1..{max_hops}]->"
            f"(b {{id:'{target_id}'}}) "
            f"RETURN [n in nodes(path) | n.label] AS labels, "
            f"[r in relationships(path) | type(r)] AS relations "
            f"LIMIT 3",
            graph_name=graph_name
        )
        return [{"labels": r[0], "relations": r[1]} for r in rows]

    @staticmethod
    def _load_jsonl(path):
        records = []
        if not Path(path).exists():
            return records
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    records.append(json.loads(line))
        return records
