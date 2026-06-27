# 🧠 Claude Memory — + DreamNova Claude-Code power tools

A native **macOS desktop app** that makes Claude Code's persistent memory **visible and manageable**:
browse, full-text search, add, edit and delete the markdown "memories" Claude Code keeps in
`~/.claude/projects/<project>/memory/`. Plus two headless power-tools bundled in `tools/`.

> Built in one session (2026-06-27) on top of Claude Code's own file-based memory. Local-first,
> zero cloud, your memories never leave your disk.

![type: desktop app](https://img.shields.io/badge/desktop-macOS-blue) ![local-first](https://img.shields.io/badge/local--first-no%20cloud-success) ![license: MIT](https://img.shields.io/badge/license-MIT-green)

## What it does
- **Browse** every memory as a card (type badge, title, description), newest first.
- **Search** full-text across names, descriptions and bodies, ranked.
- **Add / edit / delete** memories — writes the same markdown + frontmatter Claude Code reads,
  and appends a pointer to `MEMORY.md` (the index Claude loads each session).
- **Multi-project**: auto-discovers every `~/.claude/projects/*/memory/` and lets you switch.
- **Bonus buttons**: 🛡️ *Focus* (hide agent browsers / anti focus-steal) and 🕹️ *Browser*
  (headless browser-controller status) — wired to the bundled tools below.

Native window via **pywebview / WKWebView** (dark + gold UI). No Electron.

## Install / run (macOS)
```bash
git clone https://github.com/CodeNoLimits/claude-memory.git
cd claude-memory
python3 -m venv --system-site-packages .venv      # reuses system pyobjc (AppKit/Quartz)
.venv/bin/pip install pywebview pyobjc-framework-WebKit
.venv/bin/python app.py                            # opens the window
```
Prove it without opening a window (CI / headless):
```bash
.venv/bin/python app.py --selftest    # core 10/10 + UI + API + pywebview
.venv/bin/python claude_memory_core.py selftest
```
Double-clickable `.app` bundle: see `packaging/` notes (a minimal bundle launches `.venv/bin/python app.py`).

## Architecture
| File | Role |
|---|---|
| `claude_memory_core.py` | Data layer — discover dirs, parse frontmatter, list/search/CRUD, stats. **Zero deps, fully unit-tested.** |
| `app.py` | pywebview window + `Api` bridge (JS ↔ Python). `--selftest` proves logic with **no window** (focus-safe). |
| `ui/index.html` | Single-file dark/gold UI (search, list, detail, edit, new-memory modal, mini-markdown). |
| `gui_smoke.py` | Loads the real UI in a **hidden** window and asserts the DOM rendered (proven: 400 cards). |

## Bundled power tools (`tools/`)
- **`nova-browse`** — universal headless browser controller for any terminal ("see & drive the web like
  Claude-browser", but fully hidden). Zero-dependency CDP client (works on any `python3 ≥ 3.6`).
  `nova-browse goto <url> · read · snapshot · click · fill · see · act`.
- **`nova-nofocus`** — one command to stop agent browsers from stealing your keyboard focus, now + permanently.
- **`focus_guard.py`** — the launchd daemon behind it (hides any agent browser the instant it becomes visible).

## Honest note on commercialization
We did real market research before shipping. **Verdict: this is an OSS / reputation asset, not a paid product** —
Anthropic now ships native auto-memory *for free by default* in Claude Code, and free OSS tools (claude-mem, 65k★)
already cover the "local markdown memory" pitch. The only defensible paid wedge is **portable multi-agent memory**
(Claude + Grok + Cursor + Antigravity) sold B2B. Full analysis with sources: [`docs/COMMERCIALIZATION.md`](docs/COMMERCIALIZATION.md).

## License
MIT — see [LICENSE](LICENSE). Built by [DreamNova](https://github.com/CodeNoLimits) (David Amor).
