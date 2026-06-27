#!/usr/bin/env python3
"""Smoke test GUI focus-safe : ouvre la fenêtre CACHÉE (hidden=True → aucun vol de focus),
laisse le JS booter (pont pywebview), lit le DOM pour prouver que ça s'affiche, puis détruit."""
import sys
import time

import webview
from app import UI, Api

api = Api()
out = {}


def probe(window):
    time.sleep(3.0)  # laisse pywebviewready + boot() peupler le DOM via le pont JS↔Python
    try:
        out["title"] = window.evaluate_js("document.title")
        out["count"] = window.evaluate_js("document.getElementById('st-count').textContent")
        out["size"] = window.evaluate_js("document.getElementById('st-size').textContent")
        out["cards"] = window.evaluate_js("document.querySelectorAll('.card').length")
        out["proj_options"] = window.evaluate_js("document.getElementById('proj').options.length")
    except Exception as e:
        out["error"] = str(e)
    finally:
        window.destroy()


w = webview.create_window("Claude Memory (smoke)", UI, js_api=api, hidden=True,
                          width=1180, height=770)
webview.start(probe, w)

print("GUI smoke result:", out)
ok = (not out.get("error")
      and out.get("count") not in (None, "", "—")     # boot a peuplé le compteur via le pont
      and (out.get("cards") or 0) > 0                  # la liste de souvenirs s'est rendue
      and (out.get("proj_options") or 0) >= 1)
print("GUI SMOKE", "OK ✅" if ok else "ÉCHEC ❌",
      f"(count={out.get('count')}, cards={out.get('cards')}, projets={out.get('proj_options')})")
sys.exit(0 if ok else 1)
