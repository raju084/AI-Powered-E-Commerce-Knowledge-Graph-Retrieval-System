"""
End-to-End E-Commerce Knowledge Graph Retrieval Pipeline.

Flow:
User Question
    ↓
LLM (Question to Graph Query Translation)
    ↓
Graph Query Spec (JSON)
    ↓
Graph Retriever (NetworkX multi-hop traversal & facts extraction)
    ↓
Retrieved Graph Data
    ↓
LLM (Strictly Grounded Answer Generation)
    ↓
Final Answer + Grounding Verification
"""

import time
from typing import Dict, Any, Optional
from backend.knowledge_graph import EcommerceKnowledgeGraph
from backend.query_engine import GraphQueryEngine
from backend.retriever import GraphRetriever
from backend.llm_service import LLMService
from backend.models import PipelineResponse


class KnowledgeGraphPipeline:
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.kg = EcommerceKnowledgeGraph(data)
        self.query_engine = GraphQueryEngine(self.kg)
        self.retriever = GraphRetriever(self.query_engine)
        self.llm = LLMService()

    def query(self, question: str) -> PipelineResponse:
        """
        Executes the full pipeline for a natural language user question:
        User Question → LLM → Graph Query → Retrieve Data → LLM → Answer
        """
        # Step 1: LLM translates natural language question into structured graph query
        graph_query = self.llm.translate_question_to_query(question)

        # Step 2: Retrieve matched nodes, relationships, and facts from Knowledge Graph
        retrieved_data = self.retriever.retrieve(graph_query)

        # Step 3: LLM generates final answer strictly grounded in retrieved graph data
        final_answer = self.llm.generate_grounded_answer(question, retrieved_data)

        # Step 4: Verify factual grounding
        is_grounded, _ = self.retriever.verify_grounding(final_answer, retrieved_data)

        return PipelineResponse(
            question=question,
            graph_query=graph_query,
            retrieved_data=retrieved_data,
            final_answer=final_answer,
            grounded=is_grounded,
            model_used=self.llm.get_provider_name()
        )
