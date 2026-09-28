"""
Test Suite: Dedicated verification of the Banana Requirement.
Requirement:
"Add the word banana as a node/value in the knowledge graph exactly 5 times.
 The word should be retrievable through the system."
"""

import unittest
from src.dataset import SAMPLE_DATA, audit_banana_occurrences
from src.knowledge_graph import EcommerceKnowledgeGraph
from src.pipeline import KnowledgeGraphPipeline


class TestBananaRequirement(unittest.TestCase):
    def setUp(self):
        self.kg = EcommerceKnowledgeGraph(SAMPLE_DATA)
        self.pipeline = KnowledgeGraphPipeline(SAMPLE_DATA)

    def test_raw_data_banana_count_is_exactly_5(self):
        """Validates that the raw e-commerce dataset has exactly 5 occurrences of 'banana'."""
        count = audit_banana_occurrences(SAMPLE_DATA)
        self.assertEqual(count, 5, f"Expected exactly 5 occurrences of 'banana' in dataset, found {count}")

    def test_graph_banana_count_is_exactly_5(self):
        """Validates that the knowledge graph nodes & attributes have exactly 5 occurrences."""
        audit = self.kg.count_banana_occurrences()
        self.assertTrue(audit["is_valid"], f"Graph banana audit failed: {audit}")
        self.assertEqual(audit["total_occurrences"], 5)

        # Verify the 5 distinct entity types
        entity_types = {item["entity_type"] for item in audit["occurrences"]}
        expected_types = {"Brand", "Category", "Vendor", "Product", "Customer"}
        self.assertEqual(entity_types, expected_types, f"Expected banana in {expected_types}, got {entity_types}")

        # Verify each occurrence is named 'Banana'
        for item in audit["occurrences"]:
            self.assertEqual(item["value"], "Banana")
            self.assertEqual(item["attribute"], "name")

    def test_banana_entities_are_interconnected(self):
        """Validates that the Banana entities have real graph relationships."""
        # Product P11 (Banana) should be linked to Brand B06, Category C06, Vendor V05
        prod_connections = self.kg.get_connected_nodes("Product:P11")
        rel_targets = {(edge["relation"], target["name"]) for edge, target in prod_connections}

        self.assertIn(("PRODUCED_BY", "Banana"), rel_targets)
        self.assertIn(("BELONGS_TO", "Banana"), rel_targets)
        self.assertIn(("SUPPLIED_BY", "Banana"), rel_targets)

    def test_banana_retrieval_through_pipeline(self):
        """Validates that the banana entities are retrievable through the AI pipeline."""
        question = "What are all the entities in the knowledge graph named Banana and how are they related?"
        response = self.pipeline.query(question)

        self.assertTrue(response.grounded)
        self.assertIn("Banana", response.final_answer)
        # All 5 nodes should be in retrieved_data
        retrieved_names = [n.get("name") for n in response.retrieved_data.matched_nodes]
        banana_count_in_retrieval = sum(1 for name in retrieved_names if name == "Banana")
        self.assertGreaterEqual(banana_count_in_retrieval, 5)


if __name__ == "__main__":
    unittest.main()
