#!/usr/bin/env python3
import os
import re
import textwrap
from typing import List, Tuple

from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
from google import genai
from google.genai import types

# =========================
# 1) CONFIG & CLIENT
# =========================

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

SYSTEM_INSTRUCTION = (
    "You are Project Chronos, an AI Archeologist specialized in historical web text and digital slang.\n"
    "Tasks:\n"
    "1) Reconstruct the fragment: expand acronyms, explain old slang/cultural references, and produce a coherent sentence.\n"
    "2) Provide a concise modern-English rewrite (corrected phrase).\n"
    "Output format (no JSON, no code fences):\n"
    "RECONSTRUCTED: <full reconstructed sentence>\n"
    "CORRECTED: <modern cleaned sentence>"
)

def initialize_client() -> genai.Client:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set. Create a .env with GEMINI_API_KEY=...")
    return genai.Client(api_key=api_key)

try:
    client = initialize_client()
    init_error = None
except Exception as e:
    client = None
    init_error = str(e)

# =========================
# 2) HELPERS
# =========================

def parse_output(text: str) -> Tuple[str, str]:
    """Extract RECONSTRUCTED and CORRECTED lines from Gemini text output."""
    reconstructed, corrected = "", ""
    for line in (text or "").splitlines():
        ls = line.strip()
        if ls.upper().startswith("RECONSTRUCTED:"):
            reconstructed = ls.split(":", 1)[1].strip()
        elif ls.upper().startswith("CORRECTED:"):
            corrected = ls.split(":", 1)[1].strip()
    if not corrected:
        corrected = reconstructed
    return reconstructed or "—", corrected or "—"

def fetch_urls_via_gemini(query: str, model: str = DEFAULT_MODEL, k: int = 5) -> List[str]:
    """
    Second Gemini call: require URLs via google_search tool.
    Returns up to k URLs (no hard-coding, parsed from model output).
    """
    if not client:
        return []

    cfg = types.GenerateContentConfig(
        system_instruction=(
            "You are a research assistant. Use the google_search tool.\n"
            "Return ONLY URLs (one per line), no titles, no bullets, no commentary.\n"
            f"Return exactly {k} authoritative sources relevant to the topic."
        ),
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.1,
    )

    prompt = f"Topic/query: {query}\nReturn exactly {k} URLs."

    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=cfg,
        )
        text = (resp.text or "").strip()
    except Exception:
        return []

    # Extract https? URLs, keep order & unique
    urls: List[str] = []
    seen = set()
    for line in text.splitlines():
        m = re.search(r"https?://\S+", line.strip())
        if m:
            u = m.group(0).rstrip(")];,.'\">")
            if u not in seen:
                urls.append(u)
                seen.add(u)
        if len(urls) >= k:
            break
    return urls[:k]

# =========================
# 3) CORE LOGIC (1st call)
# =========================

def reconstruct(fragment: str, model: str = DEFAULT_MODEL):
    """
    First call: get reconstructed + corrected text.
    (No tools here, to keep the prose clean and deterministic.)
    """
    if not client:
        raise RuntimeError(init_error or "Gemini client not initialized")

    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
    )

    prompt = fragment.strip()
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=cfg,
    )
    reconstructed, corrected = parse_output(resp.text or "")
    return reconstructed, corrected

# =========================
# 4) FLASK APP
# =========================

app = Flask(_name_)

@app.get("/")
def index():
    html = textwrap.dedent(f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width,initial-scale=1"/>
      <title>Project Chronos — AI Archeologist</title>
      <style>
        :root {{ --bg:#f6f7fb; --fg:#111; --muted:#666; --card:#fff; --br:#e5e7eb; }}
        * {{ box-sizing: border-box; }}
        body {{
          margin:0; background:var(--bg);
          font-family: system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif;
          color: var(--fg); display:flex; min-height:100vh; align-items:center; justify-content:center;
        }}
        .card {{
          background:var(--card); width: min(900px, 94%); border-radius: 16px;
          box-shadow: 0 8px 30px rgba(0,0,0,.08); padding: 24px;
        }}
        h1 {{ margin: 0 0 8px; font-size: 22px; }}
        p  {{ margin: 0 0 16px; color: var(--muted); }}
        textarea {{
          width: 100%; min-height: 140px; padding: 12px; border: 1px solid var(--br);
          border-radius: 12px; font-size: 16px; resize: vertical; background:#fff;
        }}
        .row {{ display:flex; gap:12px; margin-top:12px; flex-wrap: wrap; }}
        button {{
          font-size: 15px; border: 1px solid var(--br); border-radius: 12px; padding: 10px 14px;
          background: var(--fg); color: #fff; cursor: pointer;
        }}
        .out {{
          margin-top: 16px; padding: 12px; border-radius: 12px; background: #fafafa;
          border: 1px dashed var(--br); min-height: 56px; white-space: pre-wrap;
        }}
        .label {{ font-size:12px; color:var(--muted); margin-top:6px; }}
        .sources {{ margin-top: 8px; padding-left: 16px; }}
        a {{ color:#1a73e8; text-decoration:none; }}
        a:hover {{ text-decoration:underline; }}
        .muted {{ color: var(--muted); font-size: 12px; margin-top: 8px; }}
        .err {{ color:#b00020; }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Project Chronos — AI Archeologist</h1>
        <p>Paste a fragmented/obscure sentence. You’ll get a reconstructed sentence, a cleaned phrase, and 5 URLs found via Gemini’s search.</p>

        <textarea id="input" placeholder="e.g., smh at the top 8 drama, ppl need to chill. g2g ttyl."></textarea>
        <div class="row">
          <button id="run">Reconstruct</button>
        </div>

        <div class="label">Original Fragment</div>
        <div class="out" id="original"></div>

        <div class="label">AI Reconstructed Text</div>
        <div class="out" id="reconstructed"></div>

        <div class="label">Corrected / Cleaned Phrase</div>
        <div class="out" id="corrected"></div>

        <div id="sources"></div>

        <div class="muted">
          Set <code>GEMINI_API_KEY</code> in a <code>.env</code> file.
          {"<div class='muted err'>Client init error: " + init_error + "</div>" if init_error else ""}
        </div>
      </div>

      <script>
        const el = (s) => document.querySelector(s);
        const outOriginal = el("#original");
        const outReconstructed = el("#reconstructed");
        const outCorrected = el("#corrected");
        const sources = el("#sources");

        el("#run").addEventListener("click", async () => {{
          const text = el("#input").value.trim();
          outOriginal.textContent = text || "—";
          outReconstructed.textContent = "Working…";
          outCorrected.textContent = "";
          sources.innerHTML = "";

          try {{
            const res = await fetch("/api/reconstruct", {{
              method: "POST",
              headers: {{ "Content-Type": "application/json" }},
              body: JSON.stringify({{ text }})
            }});
            const data = await res.json();
            if (!res.ok) {{
              outReconstructed.textContent = data.error || "Request failed.";
              return;
            }}
            outReconstructed.textContent = data.reconstructed || "—";
            outCorrected.textContent = data.corrected || data.reconstructed || "—";

            if (data.sources && data.sources.length) {{
              const ul = document.createElement("ul");
              ul.className = "sources";
              data.sources.forEach((u) => {{
                const li = document.createElement("li");
                const a = document.createElement("a");
                a.href = u;
                a.target = "_blank";
                a.rel = "noopener noreferrer";
                a.textContent = u;
                li.appendChild(a);
                ul.appendChild(li);
              }});
              sources.innerHTML = "<div class='muted'>Contextual Sources (Top 5 URLs)</div>";
              sources.appendChild(ul);
            }} else {{
              sources.innerHTML = "<div class='muted'>No URLs returned by Gemini.</div>";
            }}
          }} catch (e) {{
            outReconstructed.textContent = "Request failed.";
          }}
        }});
      </script>
    </body>
    </html>
    """).strip()
    return Response(html, mimetype="text/html")

@app.post("/api/reconstruct")
def api_reconstruct():
    data = request.get_json(silent=True) or {}
    fragment = (data.get("text") or "").strip()
    if not fragment:
        return jsonify({"error": "No text provided."}), 400

    try:
        # 1) First call: reconstruction
        reconstructed, corrected = reconstruct(fragment)

        # 2) Second call: require URLs via search (use corrected phrase if available)
        query = corrected or reconstructed or fragment
        urls = fetch_urls_via_gemini(query, k=5)

        return jsonify({
            "original": fragment,
            "reconstructed": reconstructed,
            "corrected": corrected,
            "sources": urls,  # list of URL strings
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if _name_ == "_main_":
    # pip install flask python-dotenv google-genai
    # echo "GEMINI_API_KEY=your_key_here" > .env
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
