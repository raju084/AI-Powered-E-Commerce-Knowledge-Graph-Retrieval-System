"""
Graph Query Engine for executing structured queries against the E-Commerce Knowledge Graph.
Supports multi-hop relational path traversals, entity filtering, aggregations,
and sub-graph extraction for factual grounding.
"""

from typing import Dict, Any, List, Optional
from backend.knowledge_graph import EcommerceKnowledgeGraph
from backend.models import RetrievalResult


class GraphQueryEngine:
    """
    Executes structured graph queries and path traversals on the Knowledge Graph.
    Extracts strictly grounded facts, nodes, and relational edges.
    """

    def __init__(self, kg: EcommerceKnowledgeGraph):
        self.kg = kg

    def execute_query(self, query_spec: Dict[str, Any]) -> RetrievalResult:
        """
        Executes a query specification against the graph.
        Query Spec fields:
          - target_entity: "Product", "Brand", "Category", "Vendor", "Order", "Customer", or "All"
          - filters: dict of node attribute matches, e.g. {"name": "Banana"}
          - traversal: list of hops, e.g. [{"relation": "PRODUCED_BY", "target_name": "TechCore"}]
          - aggregation: optional, e.g. "max_order_value", "banana_entities"
        """
        target_entity = query_spec.get("target_entity", "Product")
        filters = query_spec.get("filters", {})
        traversals = query_spec.get("traversal", [])
        aggregation = query_spec.get("aggregation")

        # Special Case: Audit/Find all Banana occurrences
        if aggregation == "banana_entities" or (
            filters.get("name", "").lower() == "banana" and target_entity in ["All", "Any", "*"]
        ):
            return self._retrieve_all_banana_entities(query_spec)

        # Special Case: Highest value order
        if aggregation == "max_order_value":
            return self._retrieve_highest_value_order(query_spec)

        # General Multi-Hop Relational Traversal
        matched_nodes = []
        relationships = []
        summary_facts = []

        # Candidate pool: start with nodes of target_entity, or all nodes if "All"
        if target_entity in ["All", "Any", "*"]:
            candidates = [attrs for _, attrs in self.kg.graph.nodes(data=True)]
        else:
            candidates = self.kg.find_nodes_by_type(target_entity)

        # Apply direct attribute filters
        filtered_candidates = []
        for cand in candidates:
            match = True
            for k, v in filters.items():
                cand_val = cand.get(k)
                if cand_val is None:
                    match = False
                    break
                if isinstance(v, str) and isinstance(cand_val, str):
                    if v.lower() != cand_val.lower():
                        match = False
                        break
                elif cand_val != v:
                    match = False
                    break
            if match:
                filtered_candidates.append(cand)

        # Apply relationship traversals
        for cand in filtered_candidates:
            cand_id = cand.get("id") or f"{cand.get('entity_type')}:{cand.get('internal_id')}"
            passes_traversal = True
            cand_relations = []
            cand_facts = []

            for hop in traversals:
                rel = hop.get("relation")
                target_type = hop.get("target_type")
                target_name = hop.get("target_name")

                connected = self.kg.get_connected_nodes(cand_id, relation=rel, target_type=target_type)
                
                # If target_name is specified, filter connected nodes
                if target_name:
                    matching_hop = [
                        (edge_attr, node_data)
                        for edge_attr, node_data in connected
                        if node_data.get("name", "").lower() == target_name.lower()
                    ]
                else:
                    matching_hop = connected

                if not matching_hop:
                    passes_traversal = False
                    break

                for edge_attr, node_data in matching_hop:
                    cand_relations.append({
                        "source": cand.get("name", cand_id),
                        "relation": rel,
                        "target": node_data.get("name", node_data.get("id")),
                        "target_type": node_data.get("entity_type")
                    })
                    cand_facts.append(
                        f"{cand.get('entity_type', 'Entity')} '{cand.get('name')}' is connected via {rel} to "
                        f"{node_data.get('entity_type')} '{node_data.get('name')}'."
                    )

            if passes_traversal:
                matched_nodes.append(cand)
                relationships.extend(cand_relations)
                summary_facts.extend(cand_facts)

                # Add self-description fact
                details = [f"{k}={v}" for k, v in cand.items() if k not in ["id", "internal_id"]]
                summary_facts.append(f"Node {cand.get('entity_type')}: '{cand.get('name')}' ({', '.join(details)})")

                # If entity is an Order, also retrieve items inside the order
                if cand.get("entity_type") == "Order":
                    items_connected = self.kg.get_connected_nodes(cand_id, relation="CONTAINS_ITEM")
                    for edge_attr, item_node in items_connected:
                        qty = edge_attr.get("quantity", 1)
                        uprice = edge_attr.get("unit_price", item_node.get("price", 0.0))
                        cand_relations.append({
                            "source": cand.get("name"),
                            "relation": "CONTAINS_ITEM",
                            "target": item_node.get("name")
                        })
                        summary_facts.append(
                            f"Order '{cand.get('name')}' CONTAINS_ITEM: {qty}x Product '{item_node.get('name')}' at ${uprice:.2f} each."
                        )

        is_empty = len(matched_nodes) == 0
        return RetrievalResult(
            query_executed=query_spec,
            matched_nodes=matched_nodes,
            relationships=relationships,
            summary_facts=summary_facts,
            is_empty=is_empty
        )

    def _retrieve_all_banana_entities(self, query_spec: Dict[str, Any]) -> RetrievalResult:
        """Retrieves and correlates all 5 Banana nodes in the knowledge graph."""
        audit = self.kg.count_banana_occurrences()
        matched_nodes = []
        relationships = []
        summary_facts = [
            f"Knowledge Graph Audit: Found exactly {audit['total_occurrences']} occurrences of 'Banana' across graph nodes."
        ]

        for item in audit["occurrences"]:
            nid = item["node_id"]
            node_data = self.kg.get_node(nid)
            if node_data:
                matched_nodes.append(node_data)
                etype = node_data.get("entity_type")
                name = node_data.get("name")
                summary_facts.append(f"Retrieved Banana Entity [{etype}]: ID={nid}, name='{name}'.")

                # Retrieve immediate relationships
                for edge, target in self.kg.get_connected_nodes(nid):
                    relationships.append({
                        "source": f"{etype}:{name}",
                        "relation": edge.get("relation"),
                        "target": f"{target.get('entity_type')}:{target.get('name')}"
                    })
                    summary_facts.append(
                        f"  -> {etype} '{name}' has relation '{edge.get('relation')}' to {target.get('entity_type')} '{target.get('name')}'"
                    )

        return RetrievalResult(
            query_executed=query_spec,
            matched_nodes=matched_nodes,
            relationships=relationships,
            summary_facts=summary_facts,
            is_empty=len(matched_nodes) == 0
        )

    def _retrieve_highest_value_order(self, query_spec: Dict[str, Any]) -> RetrievalResult:
        """Retrieves order with highest total_amount, its customer, and its products."""
        orders = self.kg.find_nodes_by_type("Order")
        if not orders:
            return RetrievalResult(
                query_executed=query_spec, matched_nodes=[], relationships=[], summary_facts=[], is_empty=True
            )

        highest_order = max(orders, key=lambda x: x.get("total_amount", 0.0))
        order_id = highest_order.get("id") or f"Order:{highest_order.get('internal_id')}"

        matched_nodes = [highest_order]
        relationships = []
        summary_facts = [
            f"Highest value order is {highest_order.get('name')} with total amount ${highest_order.get('total_amount'):.2f} on {highest_order.get('order_date')}."
        ]

        # Get Customer
        cust_connections = self.kg.get_connected_nodes(order_id, relation="PLACED_BY")
        for edge, cust in cust_connections:
            matched_nodes.append(cust)
            relationships.append({"source": highest_order.get("name"), "relation": "PLACED_BY", "target": cust.get("name")})
            summary_facts.append(f"Order was placed by Customer '{cust.get('name')}' (Email: {cust.get('email')}, Tier: {cust.get('loyalty_tier')}).")

        # Get Products
        prod_connections = self.kg.get_connected_nodes(order_id, relation="CONTAINS_ITEM")
        for edge, prod in prod_connections:
            matched_nodes.append(prod)
            qty = edge.get("quantity", 1)
            uprice = edge.get("unit_price", prod.get("price", 0.0))
            relationships.append({"source": highest_order.get("name"), "relation": "CONTAINS_ITEM", "target": prod.get("name")})
            summary_facts.append(f"Order contains {qty}x Product '{prod.get('name')}' at ${uprice:.2f} each.")

        return RetrievalResult(
            query_executed=query_spec,
            matched_nodes=matched_nodes,
            relationships=relationships,
            summary_facts=summary_facts,
            is_empty=False
        )
