
# Monarch Dashboard (Local CSV, Vercel-friendly)

A tiny Next.js dashboard that parses your Monarch CSV **in the browser** (no server, no credentials) and renders:
- Monthly spend vs. income
- Your 4-card categories (Housing & Insurance, Connectivity & Utilities, Digital & Lifestyle, AI & Tools)
- Smoking cost heuristic (Gas ≥ $100)
- Large purchase timing (>$1,000 by month; >$500 day-of-month)
- A simple debt payoff sandbox

## Quick Start (Vercel)

1) Create a new GitHub repo and upload this folder.  
2) In Vercel, **Add New Project → Import from GitHub** → pick your repo → Deploy.  
3) Open the app, click **Upload CSV**, and drop in your Monarch export.

> Tip: Monarch → Settings → Data → Export CSV.

## Optional Upgrades

- **Persist uploads**: Switch to Vercel Blob for storing the last CSV.
- **Cron reminders**: Use Vercel Cron to email yourself if you haven't uploaded in 14 days.
- **Interactive payoff model**: Add sliders for APR, extra payment, and debt balances.

## Customize category mapping

Edit `components/Dashboard.tsx` → `CARD_MAP` to tweak merchant-to-card assignments.
