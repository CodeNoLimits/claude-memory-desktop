#!/usr/bin/env python3
"""
claude_memory_core.py — Couche données de Claude Memory.
=========================================================
Lit / écrit / cherche la mémoire persistante de Claude Code : les fichiers markdown
`~/.claude/projects/<projet>/memory/*.md` (un fait par fichier, frontmatter) + l'index `MEMORY.md`.

Aucune dépendance externe (stdlib pure) → testable headless, portable.
La GUI (app.py) n'est qu'une vitrine au-dessus de ces fonctions.
"""
from __future__ import annotations

import glob
import os
import re
import time

HOME = os.path.expanduser("~")
INDEX_NAME = "MEMORY.md"
ARCHIVE_NAME = "MEMORY_ARCHIVE.md"


# ──────────────────────────────────────────────────────────────────────────────
# Découverte des dossiers de mémoire (multi-projets)
# ──────────────────────────────────────────────────────────────────────────────
def discover_memory_dirs() -> list[str]:
    """Tous les dossiers memory de Claude Code sur la machine."""
    pats = [
        os.path.join(HOME, ".claude", "projects", "*", "memory"),
        os.path.join(HOME, ".claude", "memory"),
    ]
    dirs = []
    for p in pats:
        for d in glob.glob(p):
            if os.path.isdir(d):
                dirs.append(d)
    return sorted(set(dirs))


def default_memory_dir() -> str | None:
    """Le dossier 'actif' : celui qui a un MEMORY.md, sinon le plus fourni."""
    dirs = discover_memory_dirs()
    if not dirs:
        return None
    with_index = [d for d in dirs if os.path.exists(os.path.join(d, INDEX_NAME))]
    pool = with_index or dirs
    return max(pool, key=lambda d: len(glob.glob(os.path.join(d, "*.md"))))


# ──────────────────────────────────────────────────────────────────────────────
# Parsing frontmatter (tolérant, sans PyYAML)
# ──────────────────────────────────────────────────────────────────────────────
def _split_frontmatter(text: str) -> tuple[str, str]:
    """Renvoie (bloc_frontmatter, corps). Bloc vide si pas de frontmatter."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end].strip("\n")
            body = text[end + 4:].lstrip("\n")
            return fm, body
    return "", text


def _field(fm: str, key: str) -> str:
    """Première valeur `key:` trouvée dans le frontmatter (gère metadata.type imbriqué)."""
    m = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def parse_memory(path: str) -> dict:
    """Métadonnées + corps d'un fichier mémoire."""
    try:
        text = open(path, encoding="utf-8").read()
    except Exception as e:
        return {"path": path, "name": os.path.basename(path), "error": str(e)}
    fm, body = _split_frontmatter(text)
    name = _field(fm, "name") or os.path.splitext(os.path.basename(path))[0]
    desc = _field(fm, "description")
    mtype = _field(fm, "type") or "note"
    st = os.stat(path)
    # 1ʳᵉ ligne de titre lisible si pas de description
    if not desc:
        for line in body.splitlines():
            s = line.strip().lstrip("#").strip()
            if s:
                desc = s[:160]
                break
    return {
        "path": path,
        "file": os.path.basename(path),
        "name": name,
        "title": _pretty_title(name),
        "description": desc,
        "type": mtype.lower(),
        "size": st.st_size,
        "mtime": st.st_mtime,
        "body": body,
        "is_index": os.path.basename(path) in (INDEX_NAME, ARCHIVE_NAME),
    }


def _pretty_title(name: str) -> str:
    t = name.replace("_", " ").replace("-", " ").strip()
    return t[:1].upper() + t[1:] if t else name


# ──────────────────────────────────────────────────────────────────────────────
# Lecture / liste / recherche
# ──────────────────────────────────────────────────────────────────────────────
def list_memories(memory_dir: str, include_index: bool = False) -> list[dict]:
    out = []
    for path in glob.glob(os.path.join(memory_dir, "*.md")):
        base = os.path.basename(path)
        if base in (INDEX_NAME, ARCHIVE_NAME) and not include_index:
            continue
        meta = parse_memory(path)
        meta.pop("body", None)  # liste = léger
        out.append(meta)
    out.sort(key=lambda m: m.get("mtime", 0), reverse=True)
    return out


def search(memory_dir: str, query: str, limit: int = 200) -> list[dict]:
    """Recherche plein-texte, classée (nom > description > corps)."""
    q = (query or "").strip().lower()
    if not q:
        return list_memories(memory_dir)
    terms = [t for t in re.split(r"\s+", q) if t]
    results = []
    for path in glob.glob(os.path.join(memory_dir, "*.md")):
        if os.path.basename(path) in (INDEX_NAME, ARCHIVE_NAME):
            continue
        meta = parse_memory(path)
        hay_name = (meta["name"] + " " + meta["title"]).lower()
        hay_desc = meta["description"].lower()
        hay_body = meta.get("body", "").lower()
        score = 0
        for t in terms:
            if t in hay_name:
                score += 10
            if t in hay_desc:
                score += 4
            if t in hay_body:
                score += 1 + hay_body.count(t) * 0.05
        if score > 0:
            meta.pop("body", None)
            meta["score"] = round(score, 2)
            results.append(meta)
    results.sort(key=lambda m: m["score"], reverse=True)
    return results[:limit]


def read_memory(path: str) -> dict:
    return parse_memory(path)


def read_index(memory_dir: str) -> str:
    p = os.path.join(memory_dir, INDEX_NAME)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


# ──────────────────────────────────────────────────────────────────────────────
# Écriture / édition / suppression
# ──────────────────────────────────────────────────────────────────────────────
def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")
    return s or "memoire_" + str(int(time.time()))


VALID_TYPES = ("user", "feedback", "project", "reference", "note")


def add_memory(memory_dir: str, name: str, description: str, mtype: str,
               body: str, add_to_index: bool = True) -> dict:
    """Crée un fichier mémoire (frontmatter) + (option) pointeur dans MEMORY.md."""
    os.makedirs(memory_dir, exist_ok=True)
    slug = slugify(name)
    mtype = (mtype or "note").lower()
    if mtype not in VALID_TYPES:
        mtype = "note"
    path = os.path.join(memory_dir, slug + ".md")
    if os.path.exists(path):
        slug = f"{slug}_{int(time.time())}"
        path = os.path.join(memory_dir, slug + ".md")
    content = (
        "---\n"
        f"name: {slug}\n"
        f"description: {description.strip()}\n"
        "metadata:\n"
        f"  type: {mtype}\n"
        "---\n\n"
        f"{body.strip()}\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    if add_to_index:
        _append_index_pointer(memory_dir, slug, _pretty_title(name or slug), description)
    return parse_memory(path)


def update_memory(path: str, content: str) -> dict:
    """Réécrit le contenu COMPLET d'un fichier (frontmatter + corps)."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return parse_memory(path)


def delete_memory(path: str) -> dict:
    """Supprime un fichier mémoire. Jamais l'index."""
    base = os.path.basename(path)
    if base in (INDEX_NAME, ARCHIVE_NAME):
        raise PermissionError("L'index ne peut pas être supprimé ici.")
    if os.path.exists(path):
        os.remove(path)
    return {"deleted": path, "ok": True}


def _append_index_pointer(memory_dir: str, slug: str, title: str, description: str) -> None:
    p = os.path.join(memory_dir, INDEX_NAME)
    line = f"- [{title}](./{slug}.md) — {description.strip()}\n"
    section = "\n## 🆕 Ajoutés via Claude Memory\n"
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write("# Memory Index\n" + section + line)
        return
    text = open(p, encoding="utf-8").read()
    if "## 🆕 Ajoutés via Claude Memory" in text:
        text = text.rstrip("\n") + "\n" + line
    else:
        text = text.rstrip("\n") + "\n" + section + line
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


# ──────────────────────────────────────────────────────────────────────────────
# Stats
# ──────────────────────────────────────────────────────────────────────────────
def stats(memory_dir: str) -> dict:
    mems = list_memories(memory_dir, include_index=False)
    by_type: dict[str, int] = {}
    total = 0
    for m in mems:
        by_type[m["type"]] = by_type.get(m["type"], 0) + 1
        total += m.get("size", 0)
    idx = os.path.join(memory_dir, INDEX_NAME)
    return {
        "dir": memory_dir,
        "count": len(mems),
        "total_bytes": total,
        "total_human": _human(total),
        "by_type": by_type,
        "index_bytes": os.path.getsize(idx) if os.path.exists(idx) else 0,
        "has_index": os.path.exists(idx),
    }


def _human(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "o" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}To"


# ──────────────────────────────────────────────────────────────────────────────
# Selftest (headless, prouve la couche données sans GUI)
# ──────────────────────────────────────────────────────────────────────────────
def selftest(tmp_dir: str | None = None) -> dict:
    import tempfile
    d = tmp_dir or tempfile.mkdtemp(prefix="cm_selftest_")
    res = {"steps": [], "ok": True}

    def step(name, cond):
        res["steps"].append((name, bool(cond)))
        if not cond:
            res["ok"] = False

    m = add_memory(d, "Test Fact Alpha", "un fait de test", "reference",
                   "Ceci est le corps du test.\nLigne 2.")
    step("add_memory crée le fichier", os.path.exists(m["path"]))
    step("frontmatter name parsé", m["name"] == "test_fact_alpha")
    step("type parsé", m["type"] == "reference")
    lst = list_memories(d)
    step("list_memories voit 1 entrée", len(lst) == 1)
    found = search(d, "alpha")
    step("search trouve par nom", len(found) == 1 and found[0]["name"] == "test_fact_alpha")
    found2 = search(d, "corps")
    step("search trouve par corps", len(found2) == 1)
    update_memory(m["path"], open(m["path"], encoding="utf-8").read() + "\najout.")
    step("update_memory écrit", "ajout." in read_memory(m["path"])["body"])
    st = stats(d)
    step("stats compte 1", st["count"] == 1)
    step("index pointeur ajouté", os.path.exists(os.path.join(d, INDEX_NAME)))
    delete_memory(m["path"])
    step("delete_memory supprime", not os.path.exists(m["path"]))
    res["dir"] = d
    res["passed"] = sum(1 for _, ok in res["steps"] if ok)
    res["total"] = len(res["steps"])
    return res


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        r = selftest()
        for name, ok in r["steps"]:
            print(("✅" if ok else "❌"), name)
        print(f"\nSELFTEST {r['passed']}/{r['total']}", "OK" if r["ok"] else "ÉCHEC")
        sys.exit(0 if r["ok"] else 1)
    # défaut : dump stats du dossier actif
    d = default_memory_dir()
    print(json.dumps(stats(d) if d else {"error": "aucun dossier mémoire"}, ensure_ascii=False, indent=2))
