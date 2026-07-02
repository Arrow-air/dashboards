# Arrow Dashboards

Static dashboards for [Arrow DAO](https://github.com/Arrow-air). No backend, no JS frameworks — plain generated HTML served via GitHub Pages.

## State of the DAO

**Live:** https://arrow-air.github.io/dashboards/

A single-page snapshot of where Arrow is right now: project status cards, action register (who has the ball), governance, calendar, and open PRs awaiting review.

### How it updates

- `data.json` holds all dashboard content. `generate.py` renders it to `index.html`.
- Vector (Arrow's agent) regenerates `data.json` periodically from GitHub/Snapshot APIs plus synthesis of meeting notes and Discord activity, then commits. **Every update is a visible diff** — check the commit history to audit what changed and when.
- Each project card shows its own `updated` date, so staleness is visible rather than hidden.
- Spot something wrong or out of date? Say so in `#bot-chat` on the Arrow Discord, or open an issue/PR here.

### Regenerate locally

```bash
python3 generate.py
```

## Future dashboards

This repo is intended to grow — cost/infra dashboards, treasury views, and other Vector-maintained pages can live alongside as subdirectories.
