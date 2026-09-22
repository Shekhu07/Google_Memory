# AI-Powered Discovery Engine Upgrade Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Retrieval Discovery Engine (`https://retrieval-discovery-engine.vercel.app`) into a state-of-the-art interactive AI discovery platform featuring real-time memory failure risk diagnostics, a filterable browser of all 144 real retrieval attempts, visual pipeline funnels, and dual-model audit analytics.

---

### Task 1: Export Specific Episodes Dataset
- [ ] Export 144 verified retrieval attempts from `data/interim/episodes.jsonl` into `engineapp/apps/web/public/data/episodes_specific.json`.
- [ ] Verify file size (~46 KB) and JSON validity.

### Task 2: Build Interactive Components
- [ ] `FunnelChart.tsx`: Ingestion pipeline visual flow (85,140 &rarr; 5,305 &rarr; 1,333 &rarr; 720 &rarr; 144).
- [ ] `EpisodeExplorer.tsx`: Searchable, filterable real episode browser with quotes, cues, and failure stages.
- [ ] `MemoryDiagnostic.tsx`: Enhanced AI memory diagnostic with failure risk score, predicted failure mode, and recovery advice.
- [ ] `AuditVisualizer.tsx`: Dual-model cross-family audit inspector (GPT-OSS vs Qwen).

### Task 3: Modern Page Integration & Styling
- [ ] Update `engineapp/apps/web/app/page.tsx` with modern 4-tab dashboard layout.
- [ ] Add design system styles in `engineapp/apps/web/app/globals.css`.

### Task 4: Compilation, Parity & Vercel Deployment
- [ ] Run `npm run build` in `engineapp/apps/web`.
- [ ] Deploy to Vercel production: `cd engineapp && npx vercel deploy --prod --project retrieval-discovery-engine -y`.
- [ ] Smoke test live URL `https://retrieval-discovery-engine.vercel.app`.
