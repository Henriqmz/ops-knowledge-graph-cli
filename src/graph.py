from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    name: str
    description: str
    properties: dict[str, Any]


@dataclass(frozen=True)
class GraphEdge:
    source: str
    relation: str
    target: str


class OpsKnowledgeGraph:
    """In-memory queryable graph of services, infrastructure, and operational guardrails."""

    def __init__(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        self.nodes = {n.id: n for n in nodes}
        self.edges = edges

    @classmethod
    def from_json_file(cls, path: Path) -> "OpsKnowledgeGraph":
        raw = json.loads(path.read_text(encoding="utf-8"))
        nodes = [
            GraphNode(
                id=n["id"],
                type=n["type"],
                name=n["name"],
                description=n.get("description", ""),
                properties=n.get("properties", {}),
            )
            for n in raw.get("nodes", [])
        ]
        edges = [
            GraphEdge(source=e["source"], relation=e["relation"], target=e["target"])
            for e in raw.get("edges", [])
        ]
        return cls(nodes, edges)

    def get_node(self, node_id: str) -> GraphNode | None:
        return self.nodes.get(node_id)

    def outgoing(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self.edges if e.source == node_id]

    def incoming(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self.edges if e.target == node_id]

    def list_rules(self) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.type.lower() == "rule"]

    def search(self, term: str) -> list[GraphNode]:
        q = term.strip().lower()
        if not q:
            return list(self.nodes.values())
        hits = []
        for n in self.nodes.values():
            haystack = f"{n.id} {n.type} {n.name} {n.description} {json.dumps(n.properties)}".lower()
            if q in haystack:
                hits.append(n)
        return hits

    def to_mermaid(self) -> str:
        lines = ["flowchart LR"]
        for n in self.nodes.values():
            safe_name = n.name.replace('"', "'")
            lines.append(f'    {n.id.replace("-", "_")}["{safe_name}"]')
        for e in self.edges:
            s = e.source.replace("-", "_")
            t = e.target.replace("-", "_")
            lines.append(f"    {s} -->|{e.relation}| {t}")
        return "\n".join(lines)
