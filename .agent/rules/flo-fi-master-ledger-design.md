# flo-fi — Master Ledger (All History)  
*Design doc / README to start a new project*

## Why
Monarch’s “Download data” may not include **all time**. Rather than juggling multiple CSVs, flo-fi keeps a **single master ledger** and **merges + dedupes** each new export so the dashboard always shows **All History**.

---

## Goals
- ✅ One **master dataset** that grows over time  
- ✅ On upload: **merge + dedupe** by a **stable ID**  
- ✅ Dashboard defaults to **All History**  
- ✅ Show **coverage banner** (e.g., “Data through: 2025-09-05”)  
- ✅ Stay simple: Vercel + Next.js + Vercel Blob (no DB required)

---

## Stack
- **Next.js (App Router)** on Vercel  
- **Vercel Blob** for `master.json` storage (private)  
- **Client** uploads parsed rows as JSON → **API** merges & writes  
- **Basic Auth middleware** to lock the site

---

## Data model
Each transaction row (normalized on the **client before upload**):
```ts
type Tx = {
  Date: string;                 // ISO string (e.g., "2025-08-15")
  Amount: number;               // negative = expense, positive = income/refund
  Merchant: string;
  Category: string;
  Account: string;
  OriginalStatement?: string;   // optional, use if present in CSV
  _id?: string;                 // stable ID (computed)
};
```

### Stable ID (dedupe key)
Concatenate key fields and hash them. Example key:
```
${Date}|${Amount}|${Merchant}|${Account}|${OriginalStatement ?? ""}
```
Hash with a simple fast 32-bit hash (sufficient for personal use).

---

## API endpoints
- `POST /api/upload` — accepts JSON `{ rows: Tx[] }`, merges into `master.json`, returns `{ added, total }`
- `GET  /api/transactions` — returns the **entire master** (or page/slice if you add paging)
- `GET  /api/coverage` — returns `{ firstDate, lastDate, total }`

---

## Environment variables (Vercel → Project → Settings → Env)
- `BASIC_AUTH_USER` / `BASIC_AUTH_PASS` — for middleware login  
- `VERCEL_BLOB_READ_WRITE_TOKEN` — write access for Vercel Blob

---

## File layout
```
app/
  api/
    upload/route.ts
    transactions/route.ts
    coverage/route.ts
  page.tsx          // client: uploads CSV, fetches master, renders charts
  layout.tsx
lib/
  blob.ts           // helpers to read/write master.json
  hash.ts           // stableId()
middleware.ts       // basic auth
public/
  robots.txt
```

---

## Code: hashing helper (`lib/hash.ts`)
```ts
// lib/hash.ts
export function stableKey(t: {
  Date: string; Amount: number; Merchant: string; Account: string; OriginalStatement?: string
}) {
  return `${t.Date}|${t.Amount}|${t.Merchant}|${t.Account}|${t.OriginalStatement ?? ""}`;
}

// Simple 32-bit hash (djb2-ish)
export function hash32(s: string) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h) ^ s.charCodeAt(i);
  // convert to unsigned hex
  return (h >>> 0).toString(16);
}

export function stableId(t: any) {
  return hash32(stableKey(t));
}
```

## Code: Vercel Blob helpers (`lib/blob.ts`)
```ts
// lib/blob.ts
import { list, put } from "@vercel/blob";

const MASTER_KEY = "flofi/master.json";

export async function readMaster() {
  const { blobs } = await list({ prefix: MASTER_KEY });
  if (!blobs.length) return { rows: [] as any[] };
  const url = blobs[0].url;
  const resp = await fetch(url, { cache: "no-store" });
  const json = await resp.json();
  return json as { rows: any[] };
}

export async function writeMaster(master: { rows: any[] }) {
  // private access; requires VERCEL_BLOB_READ_WRITE_TOKEN
  await put(MASTER_KEY, JSON.stringify(master), {
    access: "private",
    contentType: "application/json",
    token: process.env.VERCEL_BLOB_READ_WRITE_TOKEN,
  });
}
```

## Code: upload & merge (`app/api/upload/route.ts`)
```ts
// app/api/upload/route.ts
export const runtime = "edge";

import { NextResponse } from "next/server";
import { readMaster, writeMaster } from "@/lib/blob";
import { stableId } from "@/lib/hash";

type Tx = {
  Date: string; Amount: number; Merchant: string; Category: string; Account: string;
  OriginalStatement?: string; _id?: string;
};

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const rows: Tx[] = body?.rows ?? [];
    // Normalize Date to YYYY-MM-DD
    rows.forEach(r => {
      const d = new Date(r.Date);
      r.Date = isNaN(+d) ? "" : d.toISOString().slice(0, 10);
      r._id = stableId(r);
    });

    const master = await readMaster();
    const existing = new Set(master.rows.map((r: Tx) => r._id));

    let added = 0;
    for (const r of rows) {
      if (!r._id) continue;
      if (!existing.has(r._id)) {
        master.rows.push(r);
        existing.add(r._id);
        added++;
      }
    }

    // Optional: sort master by date ascending
    master.rows.sort((a: Tx, b: Tx) => a.Date.localeCompare(b.Date));

    await writeMaster(master);
    return NextResponse.json({ added, total: master.rows.length });
  } catch (e: any) {
    return NextResponse.json({ error: String(e) }, { status: 400 });
  }
}
```

## Code: serve transactions & coverage
```ts
// app/api/transactions/route.ts
export const runtime = "edge";
import { NextResponse } from "next/server";
import { readMaster } from "@/lib/blob";

export async function GET() {
  const master = await readMaster();
  return NextResponse.json(master);
}

// app/api/coverage/route.ts
export const runtime = "edge";
import { NextResponse } from "next/server";
import { readMaster } from "@/lib/blob";

export async function GET() {
  const { rows } = await readMaster();
  if (!rows.length) return NextResponse.json({ firstDate: null, lastDate: null, total: 0 });
  const firstDate = rows[0].Date;
  const lastDate  = rows[rows.length - 1].Date;
  return NextResponse.json({ firstDate, lastDate, total: rows.length });
}
```

## Code: Basic auth (`middleware.ts`)
```ts
// middleware.ts
import { NextRequest, NextResponse } from "next/server";

export function middleware(req: NextRequest) {
  const res = NextResponse.next();
  res.headers.set("X-Robots-Tag", "noindex, nofollow");

  const user = process.env.BASIC_AUTH_USER;
  const pass = process.env.BASIC_AUTH_PASS;
  if (!user || !pass) return res;

  const header = req.headers.get("authorization") || "";
  const [scheme, encoded] = header.split(" ");
  if (scheme === "Basic" && encoded) {
    const decoded = atob(encoded);
    const [u, p] = decoded.split(":");
    if (u === user && p === pass) return res;
  }
  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="flo-fi"' },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt).*)"],
};
```

## Code: robots (`public/robots.txt`)
```
User-agent: *
Disallow: /
```

---

## Client changes (high level)
- After parsing Monarch CSV **client-side**, POST to `/api/upload`:
```ts
await fetch("/api/upload", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ rows: parsedRows }),
});
```
- Fetch master for charts:
```ts
const master = await fetch("/api/transactions", { cache: "no-store" }).then(r=>r.json());
```
- Add **coverage banner** in UI:
```tsx
const cov = await fetch("/api/coverage").then(r=>r.json());
// Render: Data coverage: {cov.firstDate} → {cov.lastDate} • {cov.total} transactions
```

---

## Merge logic (pseudocode)
```
newRows = parse(CSV)
normalize dates to YYYY-MM-DD
for each row: row._id = stableId(row)

master = readMaster()
index = Set(master.rows.map(_id))

added = 0
for row in newRows:
  if row._id not in index:
    master.rows.push(row)
    index.add(row._id)

sort master by Date
writeMaster(master)
return { added, total: master.rows.length }
```

---

## Security & privacy
- **Basic Auth** gates the entire site
- **Vercel Blob** object is `private`; only your token can write  
- CSV parsing stays **client-side**; only normalized JSON is uploaded

---

## Roadmap
- Weekly **cron reminder** if no uploads in 14 days
- **Backups**: periodically copy `master.json` to `master-YYYYMMDD.json`
- **Subscription detector** + auto calendar export (.ics)
- **Model cost tracker** (AI usage)
- **Budget guardrails**: alerts on “danger days” & smoking threshold

---

## Quick start checklist
- [ ] Add env vars in Vercel (`BASIC_AUTH_*`, `VERCEL_BLOB_READ_WRITE_TOKEN`)  
- [ ] Create `lib/hash.ts`, `lib/blob.ts`, API routes, middleware, robots.txt  
- [ ] Wire client upload → `/api/upload`  
- [ ] Read `/api/transactions` for charts; show coverage from `/api/coverage`  
- [ ] Deploy → log in → upload new Monarch CSV → **All History** unlocked ✅

## Related Documentation

- [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md) - secrets management
- [[PROJECT_KICKOFF_GUIDE]] - project setup
- [Automation Reliability](patterns/automation-reliability.md) - automation
- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
- [[sales_strategy]] - sales/business
- [Safety Systems](patterns/safety-systems.md) - security
- [README](README) - Flo-Fi
