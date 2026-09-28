# E-Commerce Knowledge Graph: Sample Queries & Evaluation Results

This document contains the execution traces for benchmark questions evaluating the Knowledge Graph and AI Retrieval system.

Each evaluation demonstrates the full end-to-end pipeline:
$$\text{User Question} \longrightarrow \text{LLM Translation} \longrightarrow \text{Structured Graph Query} \longrightarrow \text{Graph Data Retrieval} \longrightarrow \text{LLM Grounded Answer}$$

---

### Verification: The Banana Requirement Audit
- **Rule**: *"Add the word banana as a node/value in the knowledge graph exactly 5 times. The word should be retrievable through the system."*
- **Audit Verification Result**: **PASS (5 / 5 Occurrences)**
  1. `Brand:B06` — `entity_type: Brand`, `name: "Banana"` (Country: Ecuador)
  2. `Category:C06` — `entity_type: Category`, `name: "Banana"` (Department: Fresh Produce)
  3. `Vendor:V05` — `entity_type: Vendor`, `name: "Banana"` (Country: Costa Rica)
  4. `Product:P11` — `entity_type: Product`, `name: "Banana"` (Price: $1.49, Stock: 500)
  5. `Customer:U06` — `entity_type: Customer`, `name: "Banana"` (Email: client.tropical@freshmail.org)

---

## Sample Query 1: Canonical Assignment Example (Brand X supplied by Vendor Y)

- **Question**: *"Which products from Brand TechCore are supplied by Vendor Apex Global Supplies?"*
- **Flow**:
  1. **User Question**: `Which products from Brand TechCore are supplied by Vendor Apex Global Supplies?`
  2. **LLM Translation to Graph Query**:
     ```json
     {
       "target_entity": "Product",
       "filters": {},
       "traversal": [
         {
           "relation": "PRODUCED_BY",
           "target_type": "Brand",
           "target_name": "TechCore"
         },
         {
           "relation": "SUPPLIED_BY",
           "target_type": "Vendor",
           "target_name": "Apex Global Supplies"
         }
       ]
     }
     ```
  3. **Graph Retrieval**:
     - **Matched Nodes**:
       - `Product:P07` (`Smart Air Fryer Pro`, Price: $189.00)
       - `Product:P09` (`Wireless Mechanical Keyboard`, Price: $129.00)
     - **Retrieved Facts**:
       - `Product 'Smart Air Fryer Pro' is connected via PRODUCED_BY to Brand 'TechCore'.`
       - `Product 'Smart Air Fryer Pro' is connected via SUPPLIED_BY to Vendor 'Apex Global Supplies'.`
       - `Product 'Wireless Mechanical Keyboard' is connected via PRODUCED_BY to Brand 'TechCore'.`
       - `Product 'Wireless Mechanical Keyboard' is connected via SUPPLIED_BY to Vendor 'Apex Global Supplies'.`
  4. **Strict Grounding Verification**: `True (Zero Hallucination)`
  5. **Final Grounded Answer**:
     ```text
     Based on the Knowledge Graph data, the matching products are:
     - 'Smart Air Fryer Pro' (ID: Product:P07, Price: $189.00)
     - 'Wireless Mechanical Keyboard' (ID: Product:P09, Price: $129.00)

     Graph Verification Facts:
       * Product 'Smart Air Fryer Pro' is connected via PRODUCED_BY to Brand 'TechCore'.
       * Product 'Smart Air Fryer Pro' is connected via SUPPLIED_BY to Vendor 'Apex Global Supplies'.
       * Product 'Wireless Mechanical Keyboard' is connected via PRODUCED_BY to Brand 'TechCore'.
       * Product 'Wireless Mechanical Keyboard' is connected via SUPPLIED_BY to Vendor 'Apex Global Supplies'.
     ```

---

## Sample Query 2: Exact 5-Banana Requirement Retrieval & Relationship Analysis

- **Question**: *"Find all entities in the knowledge graph named 'Banana' and explain how they are related."*
- **Flow**:
  1. **User Question**: `Find all entities in the knowledge graph named 'Banana' and explain how they are related.`
  2. **LLM Translation to Graph Query**:
     ```json
     {
       "target_entity": "All",
       "filters": {
         "name": "Banana"
       },
       "traversal": [],
       "aggregation": "banana_entities"
     }
     ```
  3. **Graph Retrieval**:
     - **Matched Nodes**:
       - `Brand:B06` (Brand: 'Banana')
       - `Category:C06` (Category: 'Banana')
       - `Vendor:V05` (Vendor: 'Banana')
       - `Product:P11` (Product: 'Banana')
       - `Customer:U06` (Customer: 'Banana')
     - **Relationships Traversed**:
       - `(Product:Banana)-[:PRODUCED_BY]->(Brand:Banana)`
       - `(Product:Banana)-[:BELONGS_TO]->(Category:Banana)`
       - `(Product:Banana)-[:SUPPLIED_BY]->(Vendor:Banana)`
       - `(Order:O06)-[:PLACED_BY]->(Customer:Banana)`
       - `(Order:O06)-[:CONTAINS_ITEM]->(Product:Banana)`
  4. **Strict Grounding Verification**: `True`
  5. **Final Grounded Answer**:
     ```text
     Retrieved from the Knowledge Graph: Exactly 5 entities named 'Banana' were found across the graph:
     1. Brand: 'Banana' (ID: Brand:B06)
     2. Category: 'Banana' (ID: Category:C06)
     3. Vendor: 'Banana' (ID: Vendor:V05)
     4. Product: 'Banana' (ID: Product:P11)
     5. Customer: 'Banana' (ID: Customer:U06)

     Relationships in Graph:
     - Product 'Banana' (P11) belongs to Category 'Banana' (C06), is produced by Brand 'Banana' (B06), and is supplied by Vendor 'Banana' (V05).
     - Customer 'Banana' (U06) placed Order O06 containing 10x Product 'Banana'.
     All 5 'Banana' nodes are interconnected within the Knowledge Graph.
     ```

---

## Sample Query 3: Multi-Hop Order Aggregation & Item Traversal

- **Question**: *"Which customer placed the highest value order, and what products were included in that order?"*
- **Flow**:
  1. **User Question**: `Which customer placed the highest value order, and what products were included in that order?`
  2. **LLM Translation to Graph Query**:
     ```json
     {
       "target_entity": "Order",
       "filters": {},
       "traversal": [],
       "aggregation": "max_order_value"
     }
     ```
  3. **Graph Retrieval**:
     - **Order**: `Order:O01` ($2,748.00, Date: 2026-03-01)
     - **Customer**: `Customer:U01` (`Alice Smith`, Gold Tier)
     - **Items**:
       - `Product:P01` (`MacBook Pro 16`, 1x at $2,499.00)
       - `Product:P05` (`AirPods Pro 2`, 1x at $249.00)
  4. **Strict Grounding Verification**: `True`
  5. **Final Grounded Answer**:
     ```text
     Highest value order is Order O01 with total amount $2748.00 on 2026-03-01.
     Order was placed by Customer 'Alice Smith' (Email: alice.smith@example.com, Tier: Gold).
     Order contains 1x Product 'MacBook Pro 16' at $2499.00 each.
     Order contains 1x Product 'AirPods Pro 2' at $249.00 each.
     ```

---

## Sample Query 4: Brand-to-Vendor Relationship Filter

- **Question**: *"Which products from Brand Apple are supplied by Vendor Foxconn Logistics?"*
- **Flow**:
  1. **User Question**: `Which products from Brand Apple are supplied by Vendor Foxconn Logistics?`
  2. **LLM Translation to Graph Query**:
     ```json
     {
       "target_entity": "Product",
       "filters": {},
       "traversal": [
         {
           "relation": "PRODUCED_BY",
           "target_type": "Brand",
           "target_name": "Apple"
         },
         {
           "relation": "SUPPLIED_BY",
           "target_type": "Vendor",
           "target_name": "Foxconn Logistics"
         }
       ]
     }
     ```
  3. **Graph Retrieval**:
     - Matched: `MacBook Pro 16` ($2499.00) and `iPhone 15 Pro` ($1199.00).
     - *Note*: `AirPods Pro 2` is manufactured by Apple but supplied by *Pacific Freight Partners*, so it was strictly excluded by graph traversal!
  4. **Strict Grounding Verification**: `True`
  5. **Final Grounded Answer**:
     ```text
     Based on the Knowledge Graph data, the matching products are:
     - 'MacBook Pro 16' (ID: Product:P01, Price: $2499.00)
     - 'iPhone 15 Pro' (ID: Product:P02, Price: $1199.00)

     Graph Verification Facts:
       * Product 'MacBook Pro 16' is connected via PRODUCED_BY to Brand 'Apple'.
       * Product 'MacBook Pro 16' is connected via SUPPLIED_BY to Vendor 'Foxconn Logistics'.
       * Product 'iPhone 15 Pro' is connected via PRODUCED_BY to Brand 'Apple'.
       * Product 'iPhone 15 Pro' is connected via SUPPLIED_BY to Vendor 'Foxconn Logistics'.
     ```

---

## Sample Query 5: Customer Order History & Item Extraction

- **Question**: *"What orders were placed by Customer 'Banana' and which items did they buy?"*
- **Flow**:
  1. **User Question**: `What orders were placed by Customer 'Banana' and which items did they buy?`
  2. **LLM Translation to Graph Query**:
     ```json
     {
       "target_entity": "Order",
       "filters": {},
       "traversal": [
         {
           "relation": "PLACED_BY",
           "target_type": "Customer",
           "target_name": "Banana"
         }
       ]
     }
     ```
  3. **Graph Retrieval**:
     - `Order:O06` placed by Customer 'Banana'.
     - Items in order: 10x Product 'Banana' at $1.49 each (Total: $14.90).
  4. **Strict Grounding Verification**: `True`
  5. **Final Grounded Answer**:
     ```text
     Based on the Knowledge Graph data:
     - Order 'Order O06' is connected via PLACED_BY to Customer 'Banana'.
     - Node Order: 'Order O06' (entity_type=Order, name=Order O06, order_date=2026-03-20, total_amount=14.9, status=DELIVERED)
     - Order 'Order O06' CONTAINS_ITEM: 10x Product 'Banana' at $1.49 each.
     ```

---

## Sample Query 6: Vendor Supply Portfolio & Pricing

- **Question**: *"What products are supplied by Vendor Pacific Freight Partners and what are their prices?"*
- **Flow**:
  1. **User Question**: `What products are supplied by Vendor Pacific Freight Partners and what are their prices?`
  2. **LLM Translation to Graph Query**:
     ```json
     {
       "target_entity": "Product",
       "filters": {},
       "traversal": [
         {
           "relation": "SUPPLIED_BY",
           "target_type": "Vendor",
           "target_name": "Pacific Freight Partners"
         }
       ]
     }
     ```
  3. **Graph Retrieval**:
     - `AirPods Pro 2` (ID: Product:P05, Price: $249.00)
     - `WH-1000XM5 Headphones` (ID: Product:P06, Price: $399.00)
     - `Ultra-Quiet Humidifier` (ID: Product:P10, Price: $79.00)
  4. **Strict Grounding Verification**: `True`
  5. **Final Grounded Answer**:
     ```text
     Based on the Knowledge Graph data, the matching products are:
     - 'AirPods Pro 2' (ID: Product:P05, Price: $249.00)
     - 'WH-1000XM5 Headphones' (ID: Product:P06, Price: $399.00)
     - 'Ultra-Quiet Humidifier' (ID: Product:P10, Price: $79.00)

     Graph Verification Facts:
       * Product 'AirPods Pro 2' is connected via SUPPLIED_BY to Vendor 'Pacific Freight Partners'.
       * Product 'WH-1000XM5 Headphones' is connected via SUPPLIED_BY to Vendor 'Pacific Freight Partners'.
       * Product 'Ultra-Quiet Humidifier' is connected via SUPPLIED_BY to Vendor 'Pacific Freight Partners'.
     ```
