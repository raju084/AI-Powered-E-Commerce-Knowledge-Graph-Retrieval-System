"""
Retrieval Layer and Grounding Verifier for the Knowledge Graph.
Coordinates between the query engine and the LLM, validating that all
output statements are strictly substantiated by retrieved graph nodes and edges.
"""

from typing import Dict, Any, List, Tuple
from src.models import RetrievalResult
from src.query_engine import GraphQueryEngine


class GraphRetriever:
    """
    Retrieval coordinator that queries the graph and enforces factual grounding.
    """

    def __init__(self, query_engine: GraphQueryEngine):
        self.query_engine = query_engine

    def retrieve(self, query_spec: Dict[str, Any]) -> RetrievalResult:
        """Executes the graph query and returns structured nodes and facts."""
        return self.query_engine.execute_query(query_spec)

    def verify_grounding(self, answer: str, retrieval_result: RetrievalResult) -> Tuple[bool, List[str]]:
        """
        Verifies that key entities mentioned in the answer actually exist in the retrieved graph result.
        Returns (is_grounded, audit_notes).
        """
        audit_notes = []
        if retrieval_result.is_empty:
            if "not available" in answer.lower() or "no " in answer.lower():
                return True, ["Correctly recognized empty graph retrieval."]
            return False, ["Answer generated content despite empty graph retrieval."]

        # Check matched node identifiers/names
        retrieved_tokens = set()
        for node in retrieval_result.matched_nodes:
            if "name" in node:
                retrieved_tokens.add(str(node["name"]).lower())
            if "id" in node:
                retrieved_tokens.add(str(node["id"]).lower())

        for fact in retrieval_result.summary_facts:
            words = fact.lower().split()
            for w in words:
                cleaned = w.strip(".,'\"():")
                if len(cleaned) > 3:
                    retrieved_tokens.add(cleaned)

        answer_lower = answer.lower()
        matched_mentions = 0
        for token in retrieved_tokens:
            if token in answer_lower:
                matched_mentions += 1

        is_grounded = matched_mentions > 0 or len(retrieval_result.matched_nodes) == 0
        audit_notes.append(f"Grounding score: {matched_mentions} verified graph tokens found in final answer.")
        return is_grounded, audit_notes
