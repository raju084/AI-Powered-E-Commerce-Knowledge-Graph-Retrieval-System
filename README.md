# E-Commerce Knowledge Graph and AI Retrieval Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Graph](https://img.shields.io/badge/Graph-NetworkX-green.svg)](https://networkx.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](https://react.dev/)
[![Banana](https://img.shields.io/badge/Banana%20Audit-Exact%205%20Verified-gold.svg)]()

A complete, production-grade Knowledge Graph and AI-powered retrieval system for e-commerce. Converts natural language questions into structured graph queries, traverses multi-hop entity relationships, and delivers strictly grounded answers.

---

## Architecture

Five-stage pipeline:

1. **Natural Language Input** - User asks a question
2. **Graph Query Translation** - LLM generates a JSON QuerySpec
3. **Graph Retrieval** - NetworkX traverses nodes and extracts facts
4. **Grounded Synthesis** - LLM answers using ONLY retrieved facts
5. **Grounding Verification** - Verifier checks all entity references

---

## Knowledge Graph Schema

40 nodes, 100 directed edges across 6 entity types:

| Entity | Key Attributes |
| :--- | :--- |
| Product | id, name, price, stock |
| Brand | id, name, country, rating |
| Category | id, name, department |
| Vendor | id, name, country, lead_time_days |
| Customer | id, name, email, loyalty_tier |
| Order | id, order_date, total_amount, status |

Directed Relationships:
- Product PRODUCED_BY Brand
- Product BELONGS_TO Category
- Product SUPPLIED_BY Vendor
- Order PLACED_BY Customer
- Order CONTAINS_ITEM Product

---

## The Exactly 5-Banana Requirement

The word Banana appears exactly 5 times as a node name:

| Entity | ID | Details |
|---|---|---|
| Brand | B06 | Ecuador, Rating 4.9 |
| Category | C06 | Department: Fresh Produce |
| Vendor | V05 | Costa Rica, Lead Time 2 days |
| Product | P11 | Price .49, Stock 500 |
| Customer | U06 | VIP tier, client.tropical@freshmail.org |

All 5 Banana nodes are interconnected. The audit runs on every startup. Use the Find 5 Bananas button in the dashboard.

---

## LLM Provider Fallback

Providers selected automatically:

`
GEMINI_API_KEY valid   ->  gemini
  | fails
OPENAI_API_KEY set     ->  openai
  | not set
GROQ_API_KEY set       ->  groq
  | not set
no keys                ->  offline_semantic_engine
`

Set your key in .env:
`
OPENAI_API_KEY=sk-your-key
`

---

## Setup and Running

### Install Python dependencies
`ash
pip install -r requirements.txt
`

### Start Backend (port 8000)
`ash
python server.py
`

### Start Frontend (port 3000)
`ash
cd frontend
npm install
npm run dev
`

### CLI
`ash
python main.py                # Run all 6 benchmark questions
python main.py --interactive  # Interactive query mode
`

---

## Benchmark Results

| # | Question | Answer |
| :- | :--- | :--- |
| 1 | Products from TechCore supplied by Apex Global? | Smart Air Fryer Pro, Wireless Mechanical Keyboard |
| 2 | All entities named Banana and their relations? | 5 Banana nodes - Brand, Category, Vendor, Product, Customer |
| 3 | Highest value order - customer and products? | Alice Smith - Order O01 ,748 |
| 4 | Apple products supplied by Foxconn Logistics? | MacBook Pro 16, iPhone 15 Pro |
| 5 | Orders placed by Customer Banana? | Order O06 - 10x Banana at .49 |
| 6 | Products supplied by Pacific Freight Partners? | AirPods Pro 2, WH-1000XM5, Ultra-Quiet Humidifier |

Full traces: [sample_queries_results.md](./sample_queries_results.md)

---

## Project Structure

`
AIProject/
backend/          Core engine (pipeline, llm_service, knowledge_graph, query_engine, retriever)
frontend/         React + Vite dashboard (App.jsx, index.css)
tests/            Test package
server.py         FastAPI server - port 8000
main.py           CLI entry point and benchmark runner
requirements.txt  Python dependencies
sample_queries_results.md  Full benchmark traces
README.md
`
