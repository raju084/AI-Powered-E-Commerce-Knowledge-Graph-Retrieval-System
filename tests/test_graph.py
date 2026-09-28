"""
Unit tests for the Knowledge Graph structure, entity creation, and relationships.
"""

import unittest
from src.dataset import SAMPLE_DATA
from src.knowledge_graph import EcommerceKnowledgeGraph


class TestKnowledgeGraphStructure(unittest.TestCase):
    def setUp(self):
        self.kg = EcommerceKnowledgeGraph(SAMPLE_DATA)

    def test_all_entity_types_present(self):
        """Verifies Products, Brands, Categories, Vendors, Orders, Customers exist."""
        summary = self.kg.get_summary()
        breakdown = summary["entity_breakdown"]
        required_entities = {"Product", "Brand", "Category", "Vendor", "Order", "Customer"}

        for entity in required_entities:
            self.assertIn(entity, breakdown, f"Missing entity type: {entity}")
            self.assertGreater(breakdown[entity], 0, f"Entity {entity} has 0 nodes")

    def test_all_relationship_types_present(self):
        """Verifies required directed relationships are correctly instantiated."""
        summary = self.kg.get_summary()
        rel_breakdown = summary["relationship_breakdown"]
        required_relations = {
            "PRODUCED_BY",
            "BELONGS_TO",
            "SUPPLIED_BY",
            "PLACED_BY",
            "CONTAINS_ITEM"
        }

        for rel in required_relations:
            self.assertIn(rel, rel_breakdown, f"Missing relationship: {rel}")
            self.assertGreater(rel_breakdown[rel], 0)

    def test_product_relationship_integrity(self):
        """Tests that product P01 has valid brand, category, and vendor edges."""
        prod = self.kg.get_node("Product:P01")
        self.assertIsNotNone(prod)
        self.assertEqual(prod["name"], "MacBook Pro 16")

        connections = self.kg.get_connected_nodes("Product:P01")
        rels = {edge["relation"]: target["name"] for edge, target in connections}

        self.assertEqual(rels.get("PRODUCED_BY"), "Apple")
        self.assertEqual(rels.get("BELONGS_TO"), "Electronics")
        self.assertEqual(rels.get("SUPPLIED_BY"), "Foxconn Logistics")

    def test_order_relationship_integrity(self):
        """Tests that order O01 links to Customer and contains items."""
        order = self.kg.get_node("Order:O01")
        self.assertIsNotNone(order)

        connections = self.kg.get_connected_nodes("Order:O01")
        cust_rels = [target["name"] for edge, target in connections if edge["relation"] == "PLACED_BY"]
        item_rels = [target["name"] for edge, target in connections if edge["relation"] == "CONTAINS_ITEM"]

        self.assertIn("Alice Smith", cust_rels)
        self.assertIn("MacBook Pro 16", item_rels)


if __name__ == "__main__":
    unittest.main()
