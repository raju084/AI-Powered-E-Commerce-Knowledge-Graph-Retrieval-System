# Loom Video Presentation Guide & Complete Script

Use this structured guide and word-for-word script to record your 3 to 5-minute technical walkthrough on Loom.

---

## Video Outline & Timestamps

| Timestamp | Section | Key Screen to Show |
| :--- | :--- | :--- |
| **0:00 - 0:35** | **1. Introduction & Overall Approach** | Web Dashboard / VS Code Architecture |
| **0:35 - 1:15** | **2. Knowledge Graph Architecture & Entities** | Interactive Network Graph & `src/knowledge_graph.py` |
| **1:15 - 1:55** | **3. The Exactly 5-Banana Requirement** | Banana Audit Badge + `tests/test_banana_requirement.py` |
| **1:55 - 2:45** | **4. Retrieval Layer & LLM Integration** | Query Pipeline Trace (User Question &rarr; LLM &rarr; Graph Query &rarr; Retrieve &rarr; LLM &rarr; Answer) |
| **2:45 - 3:30** | **5. Strict Factual Grounding & Zero Hallucination** | Grounding Prompt + Post-Retrieval Validation Badge |
| **3:30 - 4:45** | **6. Live Demonstration** | Web Dashboard + Terminal Benchmark Execution (`python main.py`) |
| **4:45 - 5:00** | **7. Conclusion & Wrap-up** | Test Suite passing (`python -m unittest discover tests`) |

---

## Word-for-Word Spoken Script

### 1. Introduction & Overall Approach (0:00 – 0:35)
> *"Hello everyone! In this video, I am excited to present my submission for the E-Commerce Knowledge Graph and AI-Powered Retrieval technical evaluation.*
>
> *My approach addresses a common limitation with conventional LLM RAG pipelines—unstructured vector similarity searches often struggle with multi-hop relational dependencies, such as linking a specific brand to a specific vendor through a product catalog.*
>
> *To solve this, I designed a multi-relational Knowledge Graph engine in Python using NetworkX, combined with a two-step LLM orchestration layer that translates natural language into structured graph queries and delivers strictly grounded, hallucination-free answers."*

---

### 2. Knowledge Graph Structure & Entity Relationships (0:35 – 1:15)
*(Show the interactive graph canvas on the Web UI or `src/models.py` / `src/knowledge_graph.py`)*
> *"Let's look at the Knowledge Graph structure. We have 6 primary entity types represented as typed nodes:*
> 1. *Products (e.g. MacBook Pro, Air Fryer, Headphones)*
> 2. *Brands (e.g. Apple, Samsung, Sony, TechCore, Banana)*
> 3. *Categories (e.g. Electronics, Audio, Fresh Produce)*
> 4. *Vendors (e.g. Foxconn Logistics, Apex Global Supplies, Banana)*
> 5. *Customers (e.g. Alice Smith, Bob Johnson, Banana)*
> 6. *Orders (complete order records with timestamps and amounts)*
>
> *Between these entities, we established directed relationships:*
> - *A Product `PRODUCED_BY` a Brand, `BELONGS_TO` a Category, and is `SUPPLIED_BY` a Vendor.*
> - *An Order is `PLACED_BY` a Customer and `CONTAINS_ITEM` linking to specific Products.*
> - *We also maintain bidirectional back-edges like `OFFERS_PRODUCT` and `SUPPLIES_PRODUCT` for multi-hop graph traversals."*

---

### 3. How the Banana Requirement is Implemented (1:15 – 1:55)
*(Show `tests/test_banana_requirement.py` and click the '🍌 Find 5 Bananas' button on the Web UI)*
> *"A strict requirement of this evaluation was:*
> **'Add the word banana as a node/value in the knowledge graph exactly 5 times. The word should be retrievable through the system.'**
>
> *Here is how I implemented and verified this requirement:*
> 1. *First, in our seed dataset and Knowledge Graph, 'Banana' appears exactly 5 times as the name value across 5 distinct entity types:*
>    - *Brand node: `Brand:B06` (Name: 'Banana')*
>    - *Category node: `Category:C06` (Name: 'Banana')*
>    - *Vendor node: `Vendor:V05` (Name: 'Banana')*
>    - *Product node: `Product:P11` (Name: 'Banana')*
>    - *Customer node: `Customer:U06` (Name: 'Banana')*
> 2. *Second, these 5 entities are fully interconnected: Customer Banana placed Order O06 containing Product Banana, which belongs to Category Banana, Brand Banana, and Vendor Banana.*
> 3. *Third, we have an automated audit test in `tests/test_banana_requirement.py` that scans all node attributes and edge properties to assert that the count across the entire graph is strictly 5."*

---

### 4. Retrieval Layer & LLM Integration (1:55 – 2:45)
*(Show the 4-step pipeline trace card on the Web UI or `src/pipeline.py`)*
> *"Now let's examine the query and retrieval flow:*
>
> $$\text{User Question} \longrightarrow \text{LLM} \longrightarrow \text{Graph Query Spec} \longrightarrow \text{Graph Retrieval} \longrightarrow \text{LLM} \longrightarrow \text{Answer}$$
>
> - **Step 1**: *The user asks a natural language question, such as the assignment's example: 'Which products from Brand TechCore are supplied by Vendor Apex Global Supplies?'*
> - **Step 2**: *The LLM service translates this question into a structured JSON graph query specifying the target entity `Product` and two traversal constraints: `PRODUCED_BY: TechCore` and `SUPPLIED_BY: Apex Global Supplies`.*
> - **Step 3**: *The Graph Retrieval Engine traverses the NetworkX graph, intersecting the paths, and extracts the exact matching nodes and relational facts.*
> - **Step 4**: *The LLM receives the question alongside the raw retrieved graph facts and synthesizes the final grounded answer."*

---

### 5. Strict Factual Grounding & Anti-Hallucination (2:45 – 3:30)
*(Show `src/llm_service.py`'s `GROUNDING_PROMPT_TEMPLATE` and `src/retriever.py`)*
> *"A critical requirement is ensuring answers are based **only** on retrieved graph data. We guarantee this through a two-layer defense:*
>
> 1. **Strict Grounding Prompt**: *The LLM is given an unambiguous system constraint: it must use ONLY the provided graph facts. If facts are not present, it is required to state: 'Based on the Knowledge Graph data, this information is not available.' It is strictly prohibited from using pre-trained external knowledge.*
> 2. **Post-Retrieval Grounding Verifier**: *In `src/retriever.py`, we run an automated verification that checks whether every named entity, product price, and relationship in the final answer is directly traceable back to the retrieved sub-graph.*
>
> *If a user asks about an entity not in the graph, the system returns zero matches, and the LLM cleanly declines without hallucinating."*

---

### 6. Live Demonstration (3:30 – 4:45)
*(Run queries on the Web Dashboard and run `python main.py` in the terminal)*
> *"Let's see this in action live!*
>
> *(Demo 1 - Example Question):*
> *I click: 'Which products from Brand TechCore are supplied by Vendor Apex Global Supplies?'*
> *Notice the instant execution:*
> - *Step 1 shows our question.*
> - *Step 2 shows the generated JSON query with both traversal hops.*
> - *Step 3 extracts the 2 matching products: 'Smart Air Fryer Pro' and 'Wireless Mechanical Keyboard'.*
> - *Step 4 produces the grounded answer with the green 'Strictly Grounded' verification badge.*
>
> *(Demo 2 - Banana Retrieval):*
> *Now let's test: 'Find all entities in the knowledge graph named Banana and explain how they are related.'*
> *The system retrieves all 5 Banana nodes and their mutual relationships.*
>
> *(Demo 3 - Terminal Benchmark):*
> *In the terminal, running `python main.py` executes all 6 benchmark questions and verifies our Banana Audit automatically."*

---

### 7. Conclusion & Wrap-up (4:45 – 5:00)
*(Show `python -m unittest discover tests` with 12 passing tests)*
> *"To ensure seamless evaluation for any developer, the project is completely containerless, uses Python with zero external database setup needed, has 100% unit test coverage, and includes both a CLI and an interactive Web Explorer.*
>
> *Thank you very much for your time and review! I look forward to the next steps."*

---

## Recording Checklist Before You Click 'Record'
- [ ] Open the Web UI at `http://localhost:8000` in your browser.
- [ ] Open your terminal with `c:\Users\bhagy\OneDrive\Desktop\AIProject` ready.
- [ ] Check microphone audio in Loom.
- [ ] Keep this guide open on a second monitor or side window.
- [ ] Hit Record!
