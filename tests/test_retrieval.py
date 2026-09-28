"""
Unit tests for the Retrieval System and Grounding Engine.
"""

import unittest
from src.pipeline import KnowledgeGraphPipeline


class TestRetrievalSystem(unittest.TestCase):
    def setUp(self):
        self.pipeline = KnowledgeGraphPipeline()

    def test_canonical_brand_vendor_query(self):
        """
        Tests the example query from assignment instructions:
        'Which products from Brand X are supplied by Vendor Y?'
        Example: Brand 'TechCore' supplied by Vendor 'Apex Global Supplies'
        """
        question = "Which products from Brand TechCore are supplied by Vendor Apex Global Supplies?"
        response = self.pipeline.query(question)

        self.assertTrue(response.grounded)
        self.assertFalse(response.retrieved_data.is_empty)

        # Expected products: Smart Air Fryer Pro (P07) and Wireless Mechanical Keyboard (P09)
        matched_names = [n["name"] for n in response.retrieved_data.matched_nodes]
        self.assertIn("Smart Air Fryer Pro", matched_names)
        self.assertIn("Wireless Mechanical Keyboard", matched_names)
        self.assertIn("Smart Air Fryer Pro", response.final_answer)

    def test_brand_apple_foxconn_query(self):
        """Tests products from Apple supplied by Foxconn Logistics."""
        question = "Which products from Brand Apple are supplied by Vendor Foxconn Logistics?"
        response = self.pipeline.query(question)

        self.assertTrue(response.grounded)
        matched_names = [n["name"] for n in response.retrieved_data.matched_nodes]
        self.assertIn("MacBook Pro 16", matched_names)
        self.assertIn("iPhone 15 Pro", matched_names)
        # AirPods Pro 2 is supplied by Pacific Freight Partners, NOT Foxconn, so it should not match
        self.assertNotIn("AirPods Pro 2", matched_names)

    def test_highest_value_order_query(self):
        """Tests retrieval of highest value order and customer/product multi-hop."""
        question = "Which customer placed the highest value order, and what products were included?"
        response = self.pipeline.query(question)

        self.assertTrue(response.grounded)
        self.assertIn("Alice Smith", response.final_answer)
        self.assertIn("2748", response.final_answer)

    def test_empty_retrieval_handling(self):
        """Tests that nonexistent queries return a clean, unhallucinated response."""
        # Querying an empty match
        query_spec = {
            "target_entity": "Product",
            "filters": {"name": "NonExistentGadgetXYZ"},
            "traversal": []
        }
        retrieval = self.pipeline.retriever.retrieve(query_spec)
        self.assertTrue(retrieval.is_empty)

        ans = self.pipeline.llm.generate_grounded_answer("Is NonExistentGadgetXYZ available?", retrieval)
        self.assertIn("not available", ans.lower())


if __name__ == "__main__":
    unittest.main()
