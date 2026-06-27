# Commercialization brief — desktop "persistent memory" for Claude Code / AI agents

> Real research (WebSearch + WebFetch, primary sources), 2026-06-27. Every number has a URL.
> **Bottom line: NO-GO as a paid product. GO only as an OSS reputation/funnel asset, or a B2B multi-agent wedge.**

## 1. Competitors (verified one by one)

**Memory layers (cloud + OSS SDK):**
| Product | Pricing | Traction |
|---|---|---|
| **Mem0** (mem0.ai) | Free → $19 → $79 → $249/mo | **59.6k★**, **$24M raised** (YC/Peak/Basis Set), 186M API calls Q3-2025 |
| **Letta** (ex-MemGPT) | Free → $20/mo | 23.5k★, $10M seed @ $70M — pivoting to "Letta Code" |
| **Zep / Graphiti** | Free → $104 → $312/mo | Graphiti 28.1k★; only ~$500K raised (weakest) |
| **Cognee** | Free → $5/workspace | 23.9k★, $7.5M seed (Feb 2026) |
| **Supermemory** | $19 → $399/mo | 27.8k★ (MIT), $2.6M seed (Jeff Dean, Logan Kilpatrick) |
| **Pieces for Developers** | free + ~$19/mo | **desktop app**, 9-month long-term memory, ~$26M raised |

**Native memory (the lethal part):**
- **Cursor "Memories"** — built-in since v0.51 (~May 2025), free in-product.
- **Windsurf** — "Memories" via Cascade, included in free tier.
- **Anthropic / Claude Code** — **Auto memory is ON BY DEFAULT (v2.1.59+)**: writes & reads
  `~/.claude/projects/<project>/memory/MEMORY.md` itself, managed via `/memory`
  ([code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)). Plus the `memory_20250818`
  tool API, free chat memory for all (2026-03-02), and the official MCP memory server
  (**290,508 npm downloads/month**).

## 2. Market heat: demand is real, dollars are modest, the "TAM" is fake
- **Real demand**: Mem0 186M calls/quarter (+30% MoM); 290k/mo MCP-memory downloads; all 3 giants ship native memory
  (Google Vertex "Memory Bank" went paid 2026-01-28 at $0.25/1000 memories).
- **Modest dollars**: total VC into pure-play memory ≈ **~$45M**, all seed/Series-A, no mega-round.
  Peak HN signal = "Show HN: Mem0" at 201 points; everything else <50.
- **Fake TAM**: the "$28–69 B" figures come from invented-category reports (SkyQuest/Mordor) with inconsistent
  baselines — **do not cite as fact**.

## 3. The gap — nearly nonexistent
"Local markdown memory for Claude Code" is **already saturated with free**:
- **claude-mem** — free OSS plugin, **~65k★**, already the dominant local option with a web viewer.
- **AgentMemory** — 24.2k★, Obsidian-compatible markdown mirror, native to Claude Code.
- **jayzeng/agentmemory** — "plain markdown, no database, no cloud, no lock-in" — *exactly* the local-first pitch, free.
- **Basic Memory** — local markdown, the only one monetizing → **$15/mo, but for CLOUD SYNC** (which a no-cloud stance forbids).

The only thin slice = a real **desktop GUI** (others use Obsidian or a localhost dashboard). That's a packaging/UX gap,
**not a capability gap** — and the only proven willingness-to-pay is cloud sync. Scary precedent: **Rewind.ai (the
local-Mac-memory darling) shut down 2025-12-19** and moved to cloud after the Limitless/Meta acquisition.

## 4. Verdict + 3 costed scenarios
- **A — Open-core + cloud sync $10/mo**: 2-3% conversion on 1,000 users = ~$200-300 MRR. Needs ~10k users for $2-3k MRR. Slow, and you'd be selling the cloud you criticized.
- **B — One-time desktop license $39**: 100 sales = $3,900 one-time, no recurring. CAC eats it vs free claude-mem.
- **C — B2B team / multi-agent orchestration $50/seat/mo**: 5 teams × 5 seats = $1,250 MRR. More defensible, long sales cycle, and you cross funded Supermemory/Mem0.

**Primary risk (already realized, not future):** Anthropic ships native memory **free, by default**, with the *same*
`MEMORY.md` file structure any wrapper would invent. Commoditization + platform-risk collapse together.

## 5. Differentiators — credible?
- **Local-first + OSS**: not a paid advantage — it's what claude-mem/jayzeng give away.
- **Native to Claude Code**: anti-moat — that's exactly where Anthropic is strongest.
- **Multi-agent (Grok/Cursor/Antigravity)**: **the only credible wedge** — each tool's native memory is siloed; a
  portable cross-tool/cross-machine layer is the real edge — but Supermemory ($2.6M) and Mem0 ($24M) are already there.

## Recommendation — NO-GO (cash-first)
1. **NO-GO** as a paid app: commoditized; Anthropic ships native memory free by default; 3 free OSS tools cover the pitch.
2. The only proven WTP is **cloud sync** — incompatible with a local-no-cloud identity.
3. **GO-conditional** only on the **portable multi-agent** wedge (Claude+Grok+Cursor+Antigravity), sold **B2B**, not solo.
4. Otherwise ship it **as pure OSS** = reputation / build-in-public / funnel into DreamNova consulting — not a direct cash line.
5. Don't burn dev cash on a product the incumbent gives away free this quarter.
