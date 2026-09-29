# 🛒 AI-Powered E-Commerce Knowledge Graph & Retrieval System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![NetworkX](https://img.shields.io/badge/Graph-NetworkX-orange?style=for-the-badge)](https://networkx.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A production-grade Knowledge Graph + LLM system that answers natural language questions about e-commerce data with full grounding and verification.**

[Features](#-features) • [Architecture](#️-architecture) • [Setup](#-setup--installation) • [API](#-api-reference) • [Demo](#-benchmark-results)

</div>

---

## 📌 Overview

This system converts natural language questions into structured graph queries, traverses multi-hop entity relationships across an e-commerce knowledge graph, and delivers strictly grounded answers using LLMs (Gemini / OpenAI / Groq). Every answer is verified against the graph — no hallucinations.

```
User Question → LLM Query Translation → Graph Traversal → Grounded Synthesis → Verified Answer
```

---

## ✨ Features

- 🔍 **Natural Language Querying** — Ask plain English questions about products, orders, brands, vendors
- 🧠 **Knowledge Graph Engine** — 40 nodes, 100 directed edges across 6 entity types (NetworkX)
- 🤖 **Multi-LLM Support** — Gemini, OpenAI, Groq with automatic fallback chain
- ✅ **Grounding Verification** — Every answer is cross-checked against graph facts
- 🌐 **REST API** — FastAPI backend on port 8000 with full OpenAPI docs
- ⚛️ **React Dashboard** — Beautiful Vite-powered frontend with interactive graph explorer
- 🔌 **Offline Mode** — Semantic fallback engine works without any API keys
- 📊 **Benchmark Suite** — 6 curated e-commerce queries with full result traces

---

## 🏗️ Architecture

### Five-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Retrieval Pipeline                        │
│                                                                 │
│  1. Natural Language Input                                      │
│         │                                                       │
│         ▼                                                       │
│  2. LLM Query Translation  ──► JSON QuerySpec                   │
│         │                                                       │
│         ▼                                                       │
│  3. Graph Retrieval  ──► NetworkX traverses nodes & edges       │
│         │                                                       │
│         ▼                                                       │
│  4. Grounded Synthesis  ──► LLM answers using ONLY graph facts  │
│         │                                                       │
│         ▼                                                       │
│  5. Grounding Verification  ──► All entity refs checked         │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Backend API** | FastAPI + Uvicorn |
| **Graph Engine** | NetworkX 3.x |
| **LLM Integration** | Google Gemini / OpenAI / Groq |
| **Frontend** | React 18 + Vite |
| **Data Validation** | Pydantic v2 |
| **HTTP Client** | httpx + requests |
| **Config** | python-dotenv |

---

## 🗂️ Project Structure

```
AI-Powered-E-Commerce-Knowledge-Graph-Retrieval-System/
│
├── backend/                    # Core engine
│   ├── __init__.py
│   ├── dataset.py              # E-commerce graph data (40 nodes, 100 edges)
│   ├── knowledge_graph.py      # NetworkX graph builder & traversal engine
│   ├── llm_service.py          # Multi-LLM provider (Gemini/OpenAI/Groq/Offline)
│   ├── models.py               # Pydantic data models & schemas
│   ├── pipeline.py             # End-to-end 5-stage pipeline orchestrator
│   ├── query_engine.py         # JSON QuerySpec parser & graph query executor
│   └── retriever.py            # Fact retrieval & grounding verifier
│
├── frontend/                   # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx             # Main dashboard application
│   │   ├── index.css           # Global styles & design system
│   │   └── main.jsx            # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── data/                       # Additional data assets
├── server.py                   # FastAPI server entry point (port 8000)
├── main.py                     # CLI entry point & benchmark runner
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not committed)
├── sample_queries_results.md   # Full benchmark traces
└── README.md
```

---

## 🧩 Knowledge Graph Schema

**40 nodes · 100 directed edges · 6 entity types**

| Entity Type | Key Attributes | Count |
|:------------|:---------------|:-----:|
| `Product` | id, name, price, stock | ~12 |
| `Brand` | id, name, country, rating | ~8 |
| `Category` | id, name, department | ~6 |
| `Vendor` | id, name, country, lead_time_days | ~6 |
| `Customer` | id, name, email, loyalty_tier | ~6 |
| `Order` | id, order_date, total_amount, status | ~6 |

### Directed Relationships

```
Product  ──PRODUCED_BY──►  Brand
Product  ──BELONGS_TO──►   Category
Product  ──SUPPLIED_BY──►  Vendor
Order    ──PLACED_BY──►    Customer
Order    ──CONTAINS_ITEM──► Product
```

---

## 🤖 LLM Provider Fallback Chain

The system automatically selects the best available provider:

```
GEMINI_API_KEY valid   ──►  gemini-2.0-flash
       │ fails
OPENAI_API_KEY set     ──►  gpt-4o-mini
       │ not set
GROQ_API_KEY set       ──►  llama-3.x (via Groq)
       │ not set
no keys                ──►  offline_semantic_engine (no API needed)
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- At least one LLM API key (optional — offline mode works without)

### 1. Clone the Repository

```bash
git clone https://github.com/raju084/AI-Powered-E-Commerce-Knowledge-Graph-Retrieval-System.git
cd AI-Powered-E-Commerce-Knowledge-Graph-Retrieval-System
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# Choose one or more — system auto-selects best available
GEMINI_API_KEY=your-gemini-key-here
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=your-groq-key-here
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Backend (Port 8000)

```bash
python server.py
```

Backend will be live at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 5. Start the Frontend (Port 5173)

```bash
cd frontend
npm install
npm run dev
```

Frontend dashboard at: `http://localhost:5173`

### 6. CLI Usage

```bash
# Run all 6 benchmark questions
python main.py

# Interactive query mode
python main.py --interactive
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/` | Health check & system status |
| `POST` | `/query` | Submit a natural language query |
| `GET` | `/graph/nodes` | List all graph nodes |
| `GET` | `/graph/edges` | List all graph edges |
| `GET` | `/graph/stats` | Graph statistics |
| `GET` | `/docs` | Interactive OpenAPI docs (Swagger UI) |

### Example Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Which products are supplied by Apex Global?"}'
```

```json
{
  "answer": "The products supplied by Apex Global are: Smart Air Fryer Pro and Wireless Mechanical Keyboard.",
  "grounded": true,
  "facts_used": 4,
  "provider": "gemini"
}
```

---

## 📊 Benchmark Results

| # | Question | Answer |
|:--|:---------|:-------|
| 1 | Products from TechCore supplied by Apex Global? | Smart Air Fryer Pro, Wireless Mechanical Keyboard |
| 2 | All entities named Banana and their relations? | 5 Banana nodes — Brand, Category, Vendor, Product, Customer |
| 3 | Highest value order — customer and products? | Alice Smith — Order O01, $1,748 |
| 4 | Apple products supplied by Foxconn Logistics? | MacBook Pro 16, iPhone 15 Pro |
| 5 | Orders placed by Customer Banana? | Order O06 — 10× Banana at $0.49 |
| 6 | Products supplied by Pacific Freight Partners? | AirPods Pro 2, WH-1000XM5, Ultra-Quiet Humidifier |

📄 Full traces with reasoning steps: [sample_queries_results.md](./sample_queries_results.md)

---

## 🍌 The "5 Banana" Audit

A fun integrity check — the word **Banana** appears as a node name exactly **5 times**, all interconnected:

| Entity | ID | Details |
|:-------|:---|:--------|
| Brand | B06 | Ecuador · Rating 4.9 |
| Category | C06 | Department: Fresh Produce |
| Vendor | V05 | Costa Rica · Lead Time 2 days |
| Product | P11 | Price $0.49 · Stock 500 |
| Customer | U06 | VIP tier · client.tropical@freshmail.org |

> This audit runs automatically on every server startup. Use the **"Find 5 Bananas"** button in the dashboard to visualize all connections.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using FastAPI · NetworkX · React · Google Gemini

⭐ Star this repo if you found it useful!

</div>
