from __future__ import annotations

import argparse
from pathlib import Path

from .graph import OpsKnowledgeGraph


def main() -> None:
    parser = argparse.ArgumentParser(description="Ops Knowledge Graph CLI")
    parser.add_argument("--file", default="graph.example.json", help="Arquivo JSON do grafo")
    parser.add_argument("--summary", action="store_true", help="Lista entidades agrupadas por tipo")
    parser.add_argument("--node", help="Mostra detalhes e conexões de um nó específico")
    parser.add_argument("--search", help="Busca por palavra-chave")
    parser.add_argument("--rules", action="store_true", help="Lista todas as regras/guardrails")
    parser.add_argument("--mermaid", action="store_true", help="Exporta diagrama Mermaid")
    args = parser.parse_args()

    kg = OpsKnowledgeGraph.from_json_file(Path(args.file))

    if args.node:
        n = kg.get_node(args.node)
        if not n:
            print(f"Nó '{args.node}' não encontrado.")
            return
        print(f"[{n.type}] {n.name} ({n.id})\n  {n.description}\n  Props: {n.properties}")
        for e in kg.outgoing(n.id):
            print(f"  --[{e.relation}]--> {e.target}")
        for e in kg.incoming(n.id):
            print(f"  <--[{e.relation}]-- {e.source}")
    elif args.search:
        for n in kg.search(args.search):
            print(f"• [{n.type}] {n.name} ({n.id}): {n.description}")
    elif args.rules:
        for r in kg.list_rules():
            print(f"• {r.name} ({r.id}): {r.description}")
    elif args.mermaid:
        print(kg.to_mermaid())
    else:
        grouped: dict[str, list] = {}
        for n in kg.nodes.values():
            grouped.setdefault(n.type, []).append(n)
        for gtype, items in sorted(grouped.items()):
            print(f"\n[{gtype}] ({len(items)})")
            for n in items:
                print(f"  • {n.id} -> {n.name}")


if __name__ == "__main__":
    main()
