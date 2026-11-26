from __future__ import annotations

import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from .graph import OpsKnowledgeGraph

STUDIO_HTML = """<!doctype html>
<html lang="pt-BR" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ops Knowledge Graph Explorer — AI Agent Operational Memory</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet" />
  <style>
    :root, [data-theme="dark"] {
      --bg: #050a0f; --surface: #0b1219; --surface-2: #111b24; --surface-hover: #172430;
      --text: #f0f7fc; --muted: #9ab3c8; --accent: #d4f1ff; --accent-ink: #050a0f;
      --accent-soft: rgba(212, 241, 255, 0.12); --accent-border: rgba(212, 241, 255, 0.35);
      --border: rgba(212, 241, 255, 0.14); --code-bg: #03070b;
    }
    [data-theme="light"] {
      --bg: #f0f7fc; --surface: #ffffff; --surface-2: #e3eef6; --surface-hover: #d5e5f1;
      --text: #050a0f; --muted: #395064; --accent: #050a0f; --accent-ink: #f0f7fc;
      --accent-soft: rgba(5, 10, 15, 0.08); --accent-border: rgba(5, 10, 15, 0.3);
      --border: rgba(5, 10, 15, 0.14); --code-bg: #f5faff;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: "Plus Jakarta Sans", system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
    .shell-header {
      padding: 18px max(24px, calc((100% - 1180px) / 2)); border-bottom: 1px solid var(--border);
      background: var(--surface); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem;
    }
    .brand { display: flex; align-items: center; gap: 0.85rem; }
    .logo { width: 38px; height: 38px; border-radius: 10px; background: var(--accent); color: var(--accent-ink); display: grid; place-items: center; font-weight: 900; font-size: 0.84rem; }
    .brand-title { font-weight: 800; font-size: 1.08rem; }
    .brand-sub { font-size: 0.78rem; color: var(--muted); }
    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem;
      padding: 0.54rem 0.96rem; border-radius: 9px; border: 1px solid var(--border);
      background: var(--surface-2); color: var(--text); font: inherit; font-size: 0.82rem; font-weight: 700; cursor: pointer;
    }
    .btn:hover { background: var(--surface-hover); border-color: var(--accent-border); }
    .shell-body { width: min(1180px, calc(100% - 48px)); margin: 0 auto; padding: 26px 0 44px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.9rem; margin-bottom: 20px; }
    .kpi { background: var(--surface-2); border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: 12px; padding: 0.95rem 1.1rem; }
    .kpi-label { font-size: 0.72rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
    .kpi-val { font-size: 1.65rem; font-weight: 800; color: var(--accent); margin-top: 0.2rem; }
    .grid { display: grid; grid-template-columns: 350px minmax(0, 1fr); gap: 20px; align-items: start; }
    .card { background: var(--surface-2); border: 1px solid var(--border); border-radius: 14px; padding: 1.2rem; }
    .input { width: 100%; padding: 0.58rem 0.8rem; border-radius: 9px; border: 1px solid var(--border); background: var(--bg); color: var(--text); font: inherit; font-size: 0.85rem; margin-bottom: 10px; }
    .node-item {
      padding: 11px; border-radius: 10px; border: 1px solid var(--border); background: var(--surface);
      margin-bottom: 8px; cursor: pointer; transition: all 0.15s;
    }
    .node-item:hover { background: var(--surface-hover); }
    .node-item.active { border-color: var(--accent); border-left: 4px solid var(--accent); }
    .mono { font-family: "JetBrains Mono", monospace; font-size: 0.75rem; color: var(--muted); }
    .pill { display: inline-block; font-family: "JetBrains Mono", monospace; font-size: 0.69rem; padding: 2px 8px; border-radius: 999px; background: var(--accent-soft); border: 1px solid var(--accent-border); color: var(--accent); }
    pre { margin: 0.6rem 0 0; padding: 0.9rem; border-radius: 10px; background: var(--code-bg); border: 1px solid var(--border); font-family: "JetBrains Mono", monospace; font-size: 0.78rem; overflow-x: auto; color: var(--text); }
    .edge-box { padding: 8px 11px; border-radius: 8px; background: var(--surface); border: 1px solid var(--border); margin-top: 6px; font-size: 0.83rem; }
    @media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header class="shell-header">
    <div class="brand">
      <span class="logo">KG</span>
      <div>
        <div class="brand-title">Ops Knowledge Graph Explorer</div>
        <div class="brand-sub">Memória Estruturada para Agentes de IA · Topologia de Serviços · Guardrails</div>
      </div>
    </div>
    <button id="themeToggle" type="button" class="btn" style="border-radius:999px">
      <span id="themeIcon">☀</span> <span id="themeLabel">Modo Claro</span>
    </button>
  </header>

  <main class="shell-body">
    <section class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Entidades (Nós)</div><div class="kpi-val" id="kNodes">--</div></div>
      <div class="kpi"><div class="kpi-label">Relações (Arestas)</div><div class="kpi-val" id="kEdges">--</div></div>
      <div class="kpi"><div class="kpi-label">Serviços Ativos</div><div class="kpi-val" id="kSvcs">--</div></div>
      <div class="kpi"><div class="kpi-label">Guardrails Críticos</div><div class="kpi-val" id="kRules">--</div></div>
    </section>

    <div class="grid">
      <aside class="card">
        <input id="searchBox" class="input" placeholder="Buscar nó, propriedade ou regra..." />
        <div id="nodesList"></div>
      </aside>

      <section style="display:flex;flex-direction:column;gap:18px">
        <div class="card" id="inspectorCard"></div>
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <h3 style="margin:0;font-size:0.96rem">Diagrama de Topologia Exportado (Mermaid)</h3>
            <button id="copyMermaidBtn" type="button" class="btn" style="padding:0.34rem 0.7rem;font-size:0.76rem">Copiar Mermaid</button>
          </div>
          <pre id="mermaidCode"></pre>
        </div>
      </section>
    </div>
  </main>

  <script>
    const root = document.documentElement;
    function applyTheme(t) {
      root.setAttribute("data-theme", t);
      localStorage.setItem("kg-theme", t);
      document.getElementById("themeIcon").textContent = t === "light" ? "☾" : "☀";
      document.getElementById("themeLabel").textContent = t === "light" ? "Modo Escuro" : "Modo Claro";
    }
    applyTheme(localStorage.getItem("kg-theme") || "dark");
    document.getElementById("themeToggle").addEventListener("click", () => {
      applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });

    let graphData = null;
    let selectedId = null;

    async function boot() {
      graphData = await (await fetch("/api/graph")).json();
      selectedId = graphData.nodes[0]?.id || null;
      document.getElementById("kNodes").textContent = graphData.nodes.length;
      document.getElementById("kEdges").textContent = graphData.edges.length;
      document.getElementById("kSvcs").textContent = graphData.nodes.filter(n => n.type === "Service").length;
      document.getElementById("kRules").textContent = graphData.nodes.filter(n => n.type === "Rule").length;
      document.getElementById("mermaidCode").textContent = graphData.mermaid;
      renderNodes();
      renderInspector();
    }

    function renderNodes() {
      const q = document.getElementById("searchBox").value.trim().toLowerCase();
      const box = document.getElementById("nodesList");
      box.innerHTML = "";
      graphData.nodes
        .filter(n => !q || JSON.stringify(n).toLowerCase().includes(q))
        .forEach(n => {
          const div = document.createElement("div");
          div.className = "node-item" + (n.id === selectedId ? " active" : "");
          div.innerHTML = `<span class="pill">${n.type}</span><div style="font-weight:700;margin-top:4px">${n.name}</div><div class="mono">${n.id}</div>`;
          div.addEventListener("click", () => { selectedId = n.id; renderNodes(); renderInspector(); });
          box.appendChild(div);
        });
    }

    function renderInspector() {
      const n = graphData.nodes.find(x => x.id === selectedId);
      const card = document.getElementById("inspectorCard");
      if (!n) return;
      const outEdges = graphData.edges.filter(e => e.source === n.id);
      const inEdges = graphData.edges.filter(e => e.target === n.id);
      const relHtml = [
        ...outEdges.map(e => `<div class="edge-box"><span class="mono">${e.source}</span> <strong>--[${e.relation}]→</strong> <span class="pill">${e.target}</span></div>`),
        ...inEdges.map(e => `<div class="edge-box"><span class="pill">${e.source}</span> <strong>--[${e.relation}]→</strong> <span class="mono">${e.target}</span></div>`),
      ].join("") || '<div class="mono">Nenhuma aresta conectada.</div>';

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="pill">${n.type}</span>
          <span class="mono">${n.id}</span>
        </div>
        <h2 style="margin:8px 0 4px;font-size:1.2rem">${n.name}</h2>
        <p style="margin:0 0 12px;color:var(--muted);font-size:0.9rem">${n.description}</p>
        <div class="mono" style="margin-bottom:4px">Propriedades Metadados:</div>
        <pre>${JSON.stringify(n.properties, null, 2)}</pre>
        <div class="mono" style="margin:14px 0 4px">Dependências e Governança Relacional:</div>
        ${relHtml}
      `;
    }

    document.getElementById("searchBox").addEventListener("input", renderNodes);
    document.getElementById("copyMermaidBtn").addEventListener("click", async () => {
      await navigator.clipboard.writeText(graphData.mermaid);
      const b = document.getElementById("copyMermaidBtn");
      b.textContent = "Copiado!";
      setTimeout(() => { b.textContent = "Copiar Mermaid"; }, 1800);
    });
    boot();
  </script>
</body>
</html>
"""


def run_studio(graph_file: Path = Path("graph.example.json"), port: int = 8026, host: str = "127.0.0.1") -> None:
    kg = OpsKnowledgeGraph.from_json_file(graph_file)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            pass

        def do_GET(self) -> None:
            if self.path == "/api/graph":
                payload: dict[str, Any] = {
                    "nodes": [asdict(n) for n in kg.nodes.values()],
                    "edges": [asdict(e) for e in kg.edges],
                    "mermaid": kg.to_mermaid(),
                }
                raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return
            raw_html = STUDIO_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw_html)))
            self.end_headers()
            self.wfile.write(raw_html)

    httpd = HTTPServer((host, port), Handler)
    print(f"Ops Knowledge Graph Explorer em http://{host}:{port}")
    httpd.serve_forever()
