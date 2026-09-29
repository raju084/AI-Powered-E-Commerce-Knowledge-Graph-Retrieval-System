# 🏗️ Project Architecture — E-Commerce Knowledge Graph & AI Retrieval Engine

## Overview

A full-stack AI system that converts **natural language questions** into **structured graph queries**, traverses a **NetworkX knowledge graph**, and returns **strictly grounded answers** via an LLM.

---

## System Layers

```mermaid
flowchart TD
    User["👤 User\n(Browser)"]
    
    subgraph Frontend ["Frontend — React + Vite (localhost:3000)"]
        AppJSX["App.jsx\nGraph Visualizer + QA Chat UI"]
        CSS["index.css\nDark Theme Design System"]
    end

    subgraph API ["API Layer — FastAPI (localhost:8000)"]
        Server["server.py\nREST API + CORS + Static Serve"]
        EP1["GET /api/graph\nGraph nodes & edges"]
        EP2["GET /api/stats\nSummary + Banana audit"]
        EP3["GET /api/sample-questions\nBenchmark questions"]
        EP4["POST /api/query\nNL Question → Answer"]
    end

    subgraph Pipeline ["Backend Pipeline — backend/pipeline.py"]
        LLM["LLMService\nllm_service.py\nGemini → OpenAI → Groq → Offline"]
        KG["EcommerceKnowledgeGraph\nknowledge_graph.py\nNetworkX Graph"]
        QE["GraphQueryEngine\nquery_engine.py\nNode filter + traversal"]
        RET["GraphRetriever\nretriever.py\nFact extraction + grounding check"]
    end

    subgraph Data ["Data Layer — data/"]
        D1["products.csv"]
        D2["brands.csv"]
        D3["categories.csv"]
        D4["vendors.csv"]
        D5["customers.csv"]
        D6["orders.csv"]
    end

    User -->|HTTP| Frontend
    Frontend -->|REST API calls| API
    Server --> EP1 & EP2 & EP3 & EP4
    EP4 --> Pipeline
    EP1 & EP2 --> KG
    LLM -->|"Step 1: NL → Query Spec (JSON)"| QE
    QE -->|"Step 2: Traverse graph"| RET
    RET -->|"Step 3: Facts"| LLM
    LLM -->|"Step 4: Grounded Answer"| Server
    Data -->|"dataset.py loads on startup"| KG
```

---

## Query Pipeline (Step-by-Step)

```mermaid
sequenceDiagram
    participant U as User
    participant F as React Frontend
    participant A as FastAPI /api/query
    participant L as LLMService (OpenAI)
    participant G as Knowledge Graph
    participant R as Retriever

    U->>F: Types natural language question
    F->>A: POST { "question": "..." }
    A->>L: translate_question_to_query(question)
    L-->>A: Graph Query Spec (JSON)
    A->>R: retrieve(graph_query)
    R->>G: Filter nodes + multi-hop traversal
    G-->>R: Matched nodes, edges, facts
    R-->>A: RetrievalResult
    A->>L: generate_grounded_answer(question, facts)
    L-->>A: Grounded natural language answer
    A->>R: verify_grounding(answer, facts)
    R-->>A: is_grounded: true/false
    A-->>F: JSON response (answer + trace)
    F-->>U: Renders pipeline trace + final answer
```

---

## File Structure

| File | Role |
|---|---|
| [`server.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/server.py) | FastAPI app, REST endpoints, CORS, static serving |
| [`main.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/main.py) | CLI entry point, benchmark runner |
| [`backend/pipeline.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/pipeline.py) | Orchestrates full NL→Graph→Answer pipeline |
| [`backend/llm_service.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/llm_service.py) | LLM provider abstraction (Gemini/OpenAI/Groq/Offline) |
| [`backend/knowledge_graph.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/knowledge_graph.py) | NetworkX graph, entity CRUD, Banana audit |
| [`backend/query_engine.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/query_engine.py) | Query spec executor, node filtering, multi-hop traversal |
| [`backend/retriever.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/retriever.py) | Fact summarization, grounding verification |
| [`backend/dataset.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/dataset.py) | Sample data generator, CSV export |
| [`backend/models.py`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/backend/models.py) | Pydantic data models (PipelineResponse, etc.) |
| [`frontend/src/App.jsx`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/frontend/src/App.jsx) | React UI — graph canvas + QA chat interface |
| [`frontend/src/index.css`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/frontend/src/index.css) | Dark-mode design system (CSS variables) |
| [`.env`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/.env) | API keys (GEMINI, OPENAI, GROQ) |
| [`data/`](file:///c:/Users/bhagy/OneDrive/Desktop/AIProject/data) | CSV seed data (6 entity types) |

---

## Knowledge Graph Schema

```mermaid
erDiagram
    PRODUCT ||--o{ BRAND : "PRODUCED_BY"
    PRODUCT ||--o{ CATEGORY : "BELONGS_TO"
    PRODUCT ||--o{ VENDOR : "SUPPLIED_BY"
    ORDER ||--o{ CUSTOMER : "PLACED_BY"
    ORDER ||--o{ PRODUCT : "CONTAINS_ITEM"

    PRODUCT {
        string id
        string name
        float price
        int stock
    }
    BRAND {
        string id
        string name
        string country
        float rating
    }
    VENDOR {
        string id
        string name
        string country
        int lead_time_days
    }
    CUSTOMER {
        string id
        string name
        string email
        string loyalty_tier
    }
    ORDER {
        string id
        date order_date
        float total_amount
        string status
    }
    CATEGORY {
        string id
        string name
        string department
    }
```

---

## LLM Provider Fallback Chain

```
GEMINI_API_KEY set + valid ping  →  gemini
      ↓ (fails)
OPENAI_API_KEY set               →  openai   ← currently active
      ↓ (not set)
GROQ_API_KEY set                 →  groq
      ↓ (not set)
No keys                          →  offline_semantic_engine (deterministic rule-based)
```

---

## Graph Stats
| Metric | Value |
|---|---|
| Total Nodes | 40 |
| Total Edges | 100 |
| Entity Types | Product, Brand, Category, Vendor, Customer, Order |
| Special Requirement | Exactly **5** nodes named `"Banana"` (one per entity type except Order) |
