"""
Main Entry Point for the E-Commerce Knowledge Graph & AI Retrieval System.
Runs sample evaluation questions, audits the 5-Banana requirement,
and provides an interactive CLI query interface.
"""

import sys
import json
import argparse
from typing import List, Dict, Any
from src.pipeline import KnowledgeGraphPipeline
from src.dataset import export_sample_data


SAMPLE_QUESTIONS = [
    {
        "id": 1,
        "title": "Canonical Assignment Example (Brand X supplied by Vendor Y)",
        "question": "Which products from Brand TechCore are supplied by Vendor Apex Global Supplies?"
    },
    {
        "id": 2,
        "title": "Exact 5-Banana Requirement Audit & Retrieval",
        "question": "Find all entities in the knowledge graph named 'Banana' and explain how they are related."
    },
    {
        "id": 3,
        "title": "Multi-Hop Traversal (Highest Value Order + Customer + Products)",
        "question": "Which customer placed the highest value order, and what products were included in that order?"
    },
    {
        "id": 4,
        "title": "Brand-to-Vendor Relationship Query",
        "question": "Which products from Brand Apple are supplied by Vendor Foxconn Logistics?"
    },
    {
        "id": 5,
        "title": "Customer Purchase & Order History (Banana Customer)",
        "question": "What orders were placed by Customer 'Banana' and which items did they buy?"
    },
    {
        "id": 6,
        "title": "Vendor Supply Portfolio & Pricing",
        "question": "What products are supplied by Vendor Pacific Freight Partners and what are their prices?"
    }
]


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_separator(char="=", length=80):
    print(char * length)


def run_sample_questions(pipeline: KnowledgeGraphPipeline) -> List[Dict[str, Any]]:
    """Runs all benchmark sample questions and prints complete pipeline execution trace."""
    print_separator("=")
    print("      E-COMMERCE KNOWLEDGE GRAPH - AI RETRIEVAL BENCHMARK")
    print_separator("=")
    print(f"Active LLM Engine: {pipeline.llm.get_provider_name().upper()}")
    summary = pipeline.kg.get_summary()
    print(f"Total Graph Nodes: {summary['total_nodes']} | Total Relational Edges: {summary['total_edges']}")
    print("Node Breakdown:", summary["entity_breakdown"])
    print_separator("-")

    # Run Banana Audit Check
    banana_audit = pipeline.kg.count_banana_occurrences()
    print(f"\n[BANANA AUDIT] Found {banana_audit['total_occurrences']} / 5 expected occurrences.")
    for item in banana_audit["occurrences"]:
        print(f"   * Node [{item['entity_type']}]: Name='{item['value']}' (ID: {item['node_id']})")
    assert banana_audit["is_valid"], "Banana requirement violation: count != 5"
    print("   [SUCCESS] Banana requirement verified: EXACTLY 5 occurrences exist in the graph.\n")

    results = []
    for item in SAMPLE_QUESTIONS:
        q_id = item["id"]
        title = item["title"]
        q_text = item["question"]

        print_separator("-")
        print(f"SAMPLE QUESTION {q_id}: [{title}]")
        print(f"Question: \"{q_text}\"\n")

        print("Flow Execution:")
        print("  1. [User Question]  -> Sent to LLM")
        response = pipeline.query(q_text)

        print(f"  2. [LLM to Graph]   -> Generated Query Spec:")
        print("     " + json.dumps(response.graph_query, indent=2).replace("\n", "\n     "))

        print(f"  3. [Graph Retrieve] -> Retrieved {len(response.retrieved_data.matched_nodes)} matched nodes, {len(response.retrieved_data.relationships)} relationships")
        print("     Facts Extracted:")
        for fact in response.retrieved_data.summary_facts[:4]:
            print(f"       * {fact}")
        if len(response.retrieved_data.summary_facts) > 4:
            print(f"       * ... (+{len(response.retrieved_data.summary_facts) - 4} more facts)")

        print(f"  4. [LLM Grounding]  -> Verified Grounded: {response.grounded}")
        print(f"  5. [Final Answer]:\n{response.final_answer}\n")

        results.append({
            "id": q_id,
            "title": title,
            "question": q_text,
            "graph_query": response.graph_query,
            "retrieved_nodes_count": len(response.retrieved_data.matched_nodes),
            "retrieved_nodes": response.retrieved_data.matched_nodes,
            "facts": response.retrieved_data.summary_facts,
            "final_answer": response.final_answer,
            "grounded": response.grounded,
            "model_used": response.model_used
        })

    # Save results to JSON file
    with open("sample_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Results saved to 'sample_results.json'")

    return results


def interactive_cli(pipeline: KnowledgeGraphPipeline):
    """Allows user to type arbitrary questions into the pipeline."""
    print_separator("=")
    print("        INTERACTIVE KNOWLEDGE GRAPH ASSISTANT (CLI MODE)")
    print_separator("=")
    print("Type your questions in natural language. (Type 'exit' or 'quit' to stop).\n")

    while True:
        try:
            q = input("\nAsk a question: ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Exiting. Have a great day!")
                break

            response = pipeline.query(q)
            print("\n" + "─" * 60)
            print(f"Generated Graph Query: {json.dumps(response.graph_query)}")
            print(f"Retrieved Nodes Count: {len(response.retrieved_data.matched_nodes)}")
            print("─" * 60)
            print(f"Answer:\n{response.final_answer}")
            print("─" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(description="E-Commerce Knowledge Graph AI Retrieval System")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive CLI query mode")
    parser.add_argument("--export-data", action="store_true", help="Export dataset JSON and CSV files to data/ folder")
    parser.add_argument("--web", action="store_true", help="Launch web visual dashboard")
    args = parser.parse_args()

    # Ensure dataset is generated
    export_sample_data("data")

    pipeline = KnowledgeGraphPipeline()

    if args.interactive:
        interactive_cli(pipeline)
    elif args.web:
        import uvicorn
        print("Starting Knowledge Graph Web Dashboard at http://localhost:8000 ...")
        uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
    else:
        run_sample_questions(pipeline)


if __name__ == "__main__":
    main()
