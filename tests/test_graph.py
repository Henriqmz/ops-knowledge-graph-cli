from pathlib import Path

from src.graph import OpsKnowledgeGraph


def test_graph_queries_and_mermaid():
    kg = OpsKnowledgeGraph.from_json_file(Path("graph.example.json"))
    assert kg.get_node("payments-worker") is not None
    assert len(kg.list_rules()) == 1
    assert any(n.id == "lead-sync-worker" for n in kg.search("oauth"))
    assert len(kg.incoming("prod-vps-01")) == 2
    diagram = kg.to_mermaid()
    assert "flowchart LR" in diagram
    assert "GOVERNED_BY" in diagram
