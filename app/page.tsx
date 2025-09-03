
"use client";
import { useState } from "react";
import Papa from "papaparse";
import Dashboard from "@/components/Dashboard";

export default function Page() {
  const [rows, setRows] = useState<any[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    Papa.parse(f, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (res) => {
        // Basic normalization: coerce Date and Amount
        const data = (res.data as any[]).map((r) => ({
          ...r,
          Date: new Date(r["Date"]),
          Amount: Number(r["Amount"]),
          Category: String(r["Category"] || ""),
          Merchant: String(r["Merchant"] || ""),
          Account: String(r["Account"] || ""),
        }));
        setRows(data);
        setErr(null);
        try {
          localStorage.setItem("monarch_csv_cached", JSON.stringify(data));
        } catch {}
      },
      error: (e) => setErr(String(e))
    });
  }

  function loadCache() {
    try {
      const raw = localStorage.getItem("monarch_csv_cached");
      if (!raw) return;
      const data = JSON.parse(raw);
      // Dates back to Date
      data.forEach((d: any) => (d.Date = new Date(d.Date)));
      setRows(data);
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <main className="p-6 md:p-10 max-w-6xl mx-auto">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">Personal Finance Playground</h1>
        <p className="opacity-80">Upload your Monarch CSV. Charts render locally in your browser. No scraping, no secrets.</p>
      </header>

      {!rows && (
        <div className="rounded-2xl bg-[var(--card)] p-6 mb-6">
          <div className="flex gap-4 items-center">
            <input type="file" accept=".csv,text/csv" onChange={onFile} className="block" />
            <button onClick={loadCache} className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20">
              Load last CSV
            </button>
          </div>
          {err && <p className="text-red-400 mt-3">{err}</p>}
          <p className="opacity-70 mt-4 text-sm">Tip: Export from Monarch → Settings → Data → Export CSV.</p>
        </div>
      )}

      {rows && <Dashboard rows={rows} />}
    </main>
  );
}
