#!/usr/bin/env python3
"""
Claude Memory — app desktop (fenêtre native macOS via pywebview/WKWebView).
La mémoire persistante de Claude Code, visible et gérable : parcourir, chercher,
ajouter, éditer, supprimer les souvenirs markdown de `~/.claude/.../memory/`.

Lancement : .venv/bin/python app.py        (ouvre la fenêtre)
Selftest  : .venv/bin/python app.py --selftest   (prouve la logique, AUCUNE fenêtre → safe anti-focus)
"""
import os
import shutil
import subprocess
import sys

import claude_memory_core as core

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(HERE, "ui", "index.html")


def _tool(name):
    """Résout un outil DreamNova (nova-browse / nova-nofocus) s'il est présent, sinon None."""
    p = os.path.expanduser(f"~/etz-chaim/bin/{name}")
    if os.path.exists(p):
        return p
    return shutil.which(name)


class Api:
    """Pont exposé au JS via window.pywebview.api.* — tout retour est JSON-sérialisable."""

    def __init__(self):
        self.memory_dir = core.default_memory_dir() or os.path.join(
            os.path.expanduser("~/.claude"), "memory")

    # — données mémoire —
    def dirs(self):
        return {"dirs": core.discover_memory_dirs(), "current": self.memory_dir}

    def set_dir(self, d):
        self.memory_dir = d
        return {"ok": True, "current": d}

    def stats(self):
        return core.stats(self.memory_dir)

    def list(self):
        return core.list_memories(self.memory_dir)

    def search(self, q):
        return core.search(self.memory_dir, q)

    def read(self, path):
        return core.read_memory(path)

    def add(self, name, description, mtype, body, add_to_index=True):
        try:
            return {"ok": True, "memory": core.add_memory(
                self.memory_dir, name, description, mtype, body, add_to_index)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def update(self, path, content):
        try:
            return {"ok": True, "memory": core.update_memory(path, content)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete(self, path):
        try:
            return core.delete_memory(path)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def index(self):
        return {"content": core.read_index(self.memory_dir)}

    def reveal(self, path):
        try:
            subprocess.run(["open", "-R", path], check=False)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # — outils suite DreamNova (bonus, headless) —
    def protect_focus(self):
        t = _tool("nova-nofocus")
        try:
            if t:
                r = subprocess.run([t], capture_output=True, text=True, timeout=20)
                return {"ok": True, "out": (r.stdout or r.stderr).strip()[:600]}
            # fallback générique sans l'outil DreamNova
            subprocess.run(["osascript", "-e",
                'tell application "System Events" to set visible of (every process whose '
                'name is in {"Google Chrome","Google Chrome Beta","Chromium","Google Chrome for Testing"}) to false'],
                capture_output=True, timeout=15)
            return {"ok": True, "out": "Navigateurs d'agents cachés (fallback)."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def browser_status(self):
        t = _tool("nova-browse")
        if not t:
            return {"ok": False, "error": "nova-browse non installé sur cette machine"}
        try:
            r = subprocess.run([t, "status", "--pretty"], capture_output=True, text=True, timeout=20)
            return {"ok": True, "out": (r.stdout or r.stderr).strip()[:600]}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def _selftest():
    r = core.selftest()
    ui_ok = os.path.exists(UI)
    api_ok = all(hasattr(Api, m) for m in
                 ("list", "search", "add", "update", "delete", "stats", "read", "reveal"))
    try:
        import webview  # noqa: F401
        wv_ok = True
    except Exception:
        wv_ok = False
    print(f"core selftest : {r['passed']}/{r['total']} {'OK' if r['ok'] else 'ÉCHEC'}")
    print(f"ui/index.html : {'présent' if ui_ok else 'ABSENT'}")
    print(f"API methods   : {'complètes' if api_ok else 'INCOMPLÈTES'}")
    print(f"pywebview     : {'importable' if wv_ok else 'ABSENT'}")
    ok = r["ok"] and ui_ok and api_ok and wv_ok
    print("\nAPP SELFTEST", "OK ✅" if ok else "ÉCHEC ❌")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    import webview
    api = Api()
    webview.create_window(
        "Claude Memory",
        UI,
        js_api=api,
        width=1180, height=770, min_size=(920, 600),
        background_color="#0d0d12",
    )
    webview.start()


if __name__ == "__main__":
    main()
