"""
E-Commerce Knowledge Graph Implementation using NetworkX.
Creates entities (Products, Brands, Categories, Vendors, Orders, Customers)
and establishes directed relationships between them.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import networkx as nx
from src.dataset import load_dataset


class EcommerceKnowledgeGraph:
    """
    Knowledge Graph representing an E-Commerce domain.
    Utilizes NetworkX MultiDiGraph to support typed entities and directed multi-relational edges.
    """

    def __init__(self, data: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.raw_data = data or load_dataset()
        self.graph = nx.MultiDiGraph()
        self._name_index: Dict[str, List[str]] = {}  # lower(name) -> [node_id, ...]
        self._build_graph()

    def _build_graph(self) -> None:
        """Constructs nodes and relationships from raw dataset."""
        # 1. Add Brands
        for b in self.raw_data.get("brands", []):
            node_id = f"Brand:{b['id']}"
            self.graph.add_node(
                node_id,
                entity_type="Brand",
                internal_id=b["id"],
                name=b["name"],
                country=b.get("country", ""),
                rating=b.get("rating", 0.0)
            )
            self._index_name(b["name"], node_id)

        # 2. Add Categories
        for c in self.raw_data.get("categories", []):
            node_id = f"Category:{c['id']}"
            self.graph.add_node(
                node_id,
                entity_type="Category",
                internal_id=c["id"],
                name=c["name"],
                department=c.get("department", "")
            )
            self._index_name(c["name"], node_id)

        # 3. Add Vendors
        for v in self.raw_data.get("vendors", []):
            node_id = f"Vendor:{v['id']}"
            self.graph.add_node(
                node_id,
                entity_type="Vendor",
                internal_id=v["id"],
                name=v["name"],
                country=v.get("country", ""),
                lead_time_days=v.get("lead_time_days", 0)
            )
            self._index_name(v["name"], node_id)

        # 4. Add Products and their edges to Brand, Category, Vendor
        for p in self.raw_data.get("products", []):
            prod_node = f"Product:{p['id']}"
            self.graph.add_node(
                prod_node,
                entity_type="Product",
                internal_id=p["id"],
                name=p["name"],
                price=p.get("price", 0.0),
                stock=p.get("stock", 0)
            )
            self._index_name(p["name"], prod_node)

            # Edge: Product -> Brand (PRODUCED_BY)
            brand_node = f"Brand:{p['brand_id']}"
            if self.graph.has_node(brand_node):
                self.graph.add_edge(prod_node, brand_node, relation="PRODUCED_BY")
                self.graph.add_edge(brand_node, prod_node, relation="OFFERS_PRODUCT")

            # Edge: Product -> Category (BELONGS_TO)
            cat_node = f"Category:{p['category_id']}"
            if self.graph.has_node(cat_node):
                self.graph.add_edge(prod_node, cat_node, relation="BELONGS_TO")
                self.graph.add_edge(cat_node, prod_node, relation="HAS_PRODUCT")

            # Edge: Product -> Vendor (SUPPLIED_BY)
            vendor_node = f"Vendor:{p['vendor_id']}"
            if self.graph.has_node(vendor_node):
                self.graph.add_edge(prod_node, vendor_node, relation="SUPPLIED_BY")
                self.graph.add_edge(vendor_node, prod_node, relation="SUPPLIES_PRODUCT")

        # 5. Add Customers
        for u in self.raw_data.get("customers", []):
            cust_node = f"Customer:{u['id']}"
            self.graph.add_node(
                cust_node,
                entity_type="Customer",
                internal_id=u["id"],
                name=u["name"],
                email=u.get("email", ""),
                loyalty_tier=u.get("loyalty_tier", "")
            )
            self._index_name(u["name"], cust_node)

        # 6. Add Orders and relationships to Customer and Products
        for o in self.raw_data.get("orders", []):
            order_node = f"Order:{o['id']}"
            self.graph.add_node(
                order_node,
                entity_type="Order",
                internal_id=o["id"],
                name=f"Order {o['id']}",
                order_date=o.get("order_date", ""),
                total_amount=o.get("total_amount", 0.0),
                status=o.get("status", "")
            )
            self._index_name(f"Order {o['id']}", order_node)

            # Edge: Order -> Customer (PLACED_BY)
            cust_node = f"Customer:{o['customer_id']}"
            if self.graph.has_node(cust_node):
                self.graph.add_edge(order_node, cust_node, relation="PLACED_BY")
                self.graph.add_edge(cust_node, order_node, relation="MADE_ORDER")

            # Edge: Order -> Product (CONTAINS_ITEM)
            for item in o.get("items", []):
                prod_node = f"Product:{item['product_id']}"
                if self.graph.has_node(prod_node):
                    self.graph.add_edge(
                        order_node,
                        prod_node,
                        relation="CONTAINS_ITEM",
                        quantity=item.get("quantity", 1),
                        unit_price=item.get("unit_price", 0.0)
                    )
                    self.graph.add_edge(
                        prod_node,
                        order_node,
                        relation="APPEARS_IN_ORDER"
                    )

    def _index_name(self, name: str, node_id: str) -> None:
        """Maintains a case-insensitive name-to-node index for fast retrieval."""
        key = name.strip().lower()
        if key not in self._name_index:
            self._name_index[key] = []
        if node_id not in self._name_index[key]:
            self._name_index[key].append(node_id)

    def find_nodes_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Retrieves nodes matching a given name (case-insensitive)."""
        key = name.strip().lower()
        node_ids = self._name_index.get(key, [])
        return [{"id": nid, **self.graph.nodes[nid]} for nid in node_ids]

    def find_nodes_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Retrieves all nodes of a specific entity type."""
        results = []
        for nid, attrs in self.graph.nodes(data=True):
            if attrs.get("entity_type", "").lower() == entity_type.lower():
                results.append({"id": nid, **attrs})
        return results

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Gets node attributes by its full node id."""
        if self.graph.has_node(node_id):
            return {"id": node_id, **self.graph.nodes[node_id]}
        return None

    def get_connected_nodes(
        self,
        node_id: str,
        relation: Optional[str] = None,
        target_type: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Returns list of (edge_data, target_node) connected from node_id.
        Optional filtering by relationship name and target entity type.
        """
        results = []
        if not self.graph.has_node(node_id):
            return results

        for _, target_id, edge_attrs in self.graph.out_edges(node_id, data=True):
            if relation and edge_attrs.get("relation") != relation:
                continue
            target_attrs = self.graph.nodes[target_id]
            if target_type and target_attrs.get("entity_type", "").lower() != target_type.lower():
                continue
            results.append((edge_attrs, {"id": target_id, **target_attrs}))
        return results

    def count_banana_occurrences(self) -> Dict[str, Any]:
        """
        Audits the knowledge graph to verify the EXACT 5 banana requirement.
        Scans all node attributes and edge attributes.
        """
        matches = []
        for nid, attrs in self.graph.nodes(data=True):
            for k, v in attrs.items():
                if isinstance(v, str) and "banana" in v.lower():
                    matches.append({
                        "node_id": nid,
                        "entity_type": attrs.get("entity_type"),
                        "attribute": k,
                        "value": v
                    })

        return {
            "total_occurrences": len(matches),
            "expected": 5,
            "is_valid": len(matches) == 5,
            "occurrences": matches
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns statistical overview of the Knowledge Graph."""
        entity_counts = {}
        for _, attrs in self.graph.nodes(data=True):
            etype = attrs.get("entity_type", "Unknown")
            entity_counts[etype] = entity_counts.get(etype, 0) + 1

        relation_counts = {}
        for _, _, attrs in self.graph.edges(data=True):
            rel = attrs.get("relation", "Unknown")
            relation_counts[rel] = relation_counts.get(rel, 0) + 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "entity_breakdown": entity_counts,
            "relationship_breakdown": relation_counts
        }

    def to_visualization_dict(self) -> Dict[str, Any]:
        """Exports graph structure in D3 / Vis-Network format for Web UI rendering."""
        color_palette = {
            "Product": "#3b82f6",     # Blue
            "Brand": "#10b981",       # Emerald Green
            "Category": "#8b5cf6",    # Purple
            "Vendor": "#f59e0b",      # Amber
            "Order": "#ef4444",       # Red
            "Customer": "#06b6d4"     # Cyan
        }

        nodes = []
        for nid, attrs in self.graph.nodes(data=True):
            etype = attrs.get("entity_type", "Unknown")
            name = attrs.get("name", nid)
            # Highlight Banana node with a glowing golden-yellow border/color
            is_banana = (name.lower() == "banana")
            nodes.append({
                "id": nid,
                "label": name,
                "group": etype,
                "title": f"<b>{etype}</b>: {name}<br/>ID: {nid}<br/>" + "<br/>".join(
                    f"{k}: {v}" for k, v in attrs.items() if k not in ["name", "entity_type"]
                ),
                "color": {
                    "background": "#fbbf24" if is_banana else color_palette.get(etype, "#94a3b8"),
                    "border": "#d97706" if is_banana else "#1e293b",
                    "highlight": {"background": "#fde047", "border": "#b45309"}
                },
                "shape": "dot",
                "size": 28 if is_banana else 20,
                "font": {"color": "#f8fafc", "size": 12, "face": "Inter"}
            })

        # To keep visualization clean, only include primary forward edges (not back-edges)
        primary_relations = {"BELONGS_TO", "PRODUCED_BY", "SUPPLIED_BY", "PLACED_BY", "CONTAINS_ITEM"}
        edges = []
        for u, v, attrs in self.graph.edges(data=True):
            rel = attrs.get("relation", "")
            if rel in primary_relations:
                edges.append({
                    "from": u,
                    "to": v,
                    "label": rel,
                    "arrows": "to",
                    "font": {"size": 9, "align": "middle", "color": "#94a3b8"},
                    "color": {"color": "#475569", "highlight": "#38bdf8"}
                })

        return {"nodes": nodes, "edges": edges}
