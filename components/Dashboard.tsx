"use client";
import { useMemo, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, ReferenceLine
} from "recharts";
import { Row } from "@/types";

const COLORS = ["#60a5fa","#34d399","#fbbf24","#f472b6","#c084fc","#f87171","#a3e635","#22d3ee"];

const monthKey = (d: Date) => {
  const y = d.getFullYear();
  const m = String(d.getMonth()+1).padStart(2,"0");
  return `${y}-${m}`;
};

// Gas stations where >=$100 is fuel (not cigs)
const SMOKING_DENYLIST = ["chevron","shell"];

function inCat(_category: string, row: Row, merchantList: string[]) {
  return merchantList.some(m => row.Merchant.toLowerCase().includes(m.toLowerCase()));
}

function payoffCalc(balance:number, apr:number, minPay:number, extra:number){
  let bal = balance, months = 0, interest = 0;
  const r = apr/12;
  while (bal > 0 && months < 240){
    const int = bal * r;
    interest += int;
    const pay = Math.min(bal + int, minPay + extra);
    bal = bal + int - pay;
    months++;
  }
  return { months, interest: Math.round(interest*100)/100 };
}

// Map your four-card categories by merchant keywords (editable!)
const CARD_MAP: Record<string, string[]> = {
  "Housing & Insurance": ["geico","extra space storage"],
  "Connectivity & Utilities": ["starlink","verizon","at&t","att"],
  "Digital & Lifestyle": [
    "prime video","amazon digital","dreamhost","apple","itunes","icloud","namecheap",
    "spotify","netflix","audible","google one","wikipedia","new york times","xbox","niantic"
  ],
  "AI & Tools": ["cursor","claude","openai","chatgpt","anthropic"]
};

export default function Dashboard({ rows }: { rows: Row[] }) {
  // ⚠️ Hooks at top level (not inside an IIFE)
  const [balance, setBalance] = useState(6900);
  const [apr, setApr] = useState(20);
  const [minPay, setMinPay] = useState(300);
  const [extra, setExtra] = useState(300);
  const payoff = useMemo(
    () => payoffCalc(balance, apr/100, minPay, extra),
    [balance, apr, minPay, extra]
  );

  // 1) Monthly income vs spend
  const monthly = useMemo(() => {
    const map: Record<string,{income:number, spend:number}> = {};
    for (const r of rows) {
      if (!r.Date || isNaN(r.Date.getTime())) continue;
      const k = monthKey(r.Date);
      map[k] = map[k] || { income: 0, spend: 0 };
      if (r.Amount > 0) map[k].income += r.Amount;
      else map[k].spend += Math.abs(r.Amount);
    }
    return Object.entries(map).sort().map(([Month, v]) => ({ Month, ...v }));
  }, [rows]);

  // 2) Four-card buckets
  const byCard = useMemo(() => {
    const sums: Record<string, number> = {
      "Housing & Insurance":0, "Connectivity & Utilities":0, "Digital & Lifestyle":0, "AI & Tools":0, "Other":0
    };
    for (const r of rows) {
      const amount = r.Amount < 0 ? Math.abs(r.Amount) : 0;
      let matched = false;
      for (const [card, merchants] of Object.entries(CARD_MAP)) {
        if (inCat(r.Category, r, merchants) || inCat(r.Merchant, r, merchants)) {
          sums[card] += amount;
          matched = true;
          break;
        }
      }
      if (!matched) sums["Other"] += amount;
    }
    return Object.entries(sums).map(([name, value]) => ({ name, value: Math.round(value*100)/100 }));
  }, [rows]);

  // 3) Smoking heuristic
  const smoking = useMemo(() => {
    const filtered = rows.filter(r =>
      r.Category.toLowerCase().includes("gas") &&
      r.Amount <= -100 &&
      !SMOKING_DENYLIST.some(m => r.Merchant.toLowerCase().includes(m))
    );
    const perMonth: Record<string, number> = {};
    for (const r of filtered) {
      const k = monthKey(r.Date);
      perMonth[k] = (perMonth[k] || 0) + Math.abs(r.Amount);
    }
    const series = Object.entries(perMonth).sort().map(([Month, total]) => ({ Month, total: Math.round(total*100)/100 }));
    const total = series.reduce((a,b)=>a+b.total,0);
    return { series, total: Math.round(total*100)/100, count: filtered.length };
  }, [rows]);

  // 4) > $1,000 spikes (excluding transfers/loan/card payments)
  const spikes = useMemo(() => {
    const skip = new Set(["transfer","loan repayment","credit card payment"]);
    const filtered = rows.filter(r => r.Amount <= -1000 && !skip.has(r.Category.toLowerCase()));
    const byMonth: Record<string, number> = {};
    for (const r of filtered) {
      const k = monthKey(r.Date);
      byMonth[k] = (byMonth[k] || 0) + 1;
    }
    return Object.entries(byMonth).sort().map(([Month, count]) => ({ Month, count }));
  }, [rows]);

  // 5) Day-of-month pattern for > $500 (same exclusions)
  const dayPattern = useMemo(() => {
    const skip = new Set(["transfer","loan repayment","credit card payment"]);
    const filtered = rows.filter(r => r.Amount <= -500 && !skip.has(r.Category.toLowerCase()));
    const days: Record<number, number> = {};
    for (const r of filtered) {
      const d = r.Date.getDate();
      days[d] = (days[d] || 0) + 1;
    }
    return Array.from({length:31}, (_,i)=>({ day: i+1, count: days[i+1] || 0 }));
  }, [rows]);

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-3">Monthly Income vs. Spend</h2>
        <div className="h-64" role="img" aria-label={`Chart showing monthly income vs spending over ${monthly.length} months`}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthly} aria-label="Monthly income vs spending chart">
              <XAxis dataKey="Month" />
              <YAxis />
              <Tooltip
                formatter={(value, name) => [`$${Number(value).toFixed(2)}`, name === 'income' ? 'Income' : 'Spending']}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Bar dataKey="income" stackId="a" fill="#34d399" name="Income" />
              <Bar dataKey="spend" stackId="a" fill="#f87171" name="Spending" />
              <ReferenceLine y={0} stroke="#fff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-2 text-sm opacity-80">
          <span className="inline-flex items-center mr-4">
            <span className="w-3 h-3 bg-green-400 rounded mr-2" aria-hidden="true"></span>
            Income
          </span>
          <span className="inline-flex items-center">
            <span className="w-3 h-3 bg-red-400 rounded mr-2" aria-hidden="true"></span>
            Spending
          </span>
        </div>
      </section>

      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-3">Your 4-Card Categories</h2>
        <div className="h-64" role="img" aria-label={`Pie chart showing spending by category across ${byCard.length} categories`}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={byCard}
                dataKey="value"
                nameKey="name"
                outerRadius={120}
                aria-label="Category spending breakdown"
              >
                {byCard.map((entry, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Amount']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          {byCard.map((entry, i) => (
            <div key={entry.name} className="flex items-center">
              <span
                className="w-3 h-3 rounded mr-2"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
                aria-hidden="true"
              ></span>
              <span>{entry.name}: ${entry.value.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-1">Smoking Cost (Gas ≥ $100)</h2>
        <p className="opacity-80 mb-3">Estimated total: ${"{"+`smoking.total.toFixed(2)`+"}"} • Transactions: {smoking.count}</p>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={smoking.series}>
              <XAxis dataKey="Month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total" fill="#60a5fa" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-3">Large Purchases & Timing</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="h-56">
            <h3 className="mb-1 opacity-80">Count of &gt; $1,000 by Month</h3>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={spikes}>
                <XAxis dataKey="Month" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#fbbf24" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="h-56">
            <h3 className="mb-1 opacity-80">Day-of-Month (&gt;$500)</h3>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dayPattern}>
                <XAxis dataKey="day" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#c084fc" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-1">Debt Payoff (Interactive)</h2>
        <div className="space-y-3">
          <div className="grid md:grid-cols-4 gap-3">
            <label className="block">Balance
              <input className="w-full mt-1 px-3 py-2 rounded-lg bg-white/10"
                     type="number" value={balance}
                     onChange={e=>setBalance(Number(e.target.value))}/>
            </label>
            <label className="block">APR (%)
              <input className="w-full mt-1 px-3 py-2 rounded-lg bg-white/10"
                     type="number" step="0.1" value={apr}
                     onChange={e=>setApr(Number(e.target.value))}/>
            </label>
            <label className="block">Minimum Payment
              <input className="w-full mt-1 px-3 py-2 rounded-lg bg-white/10"
                     type="number" value={minPay}
                     onChange={e=>setMinPay(Number(e.target.value))}/>
            </label>
            <label className="block">Extra Payment
              <input className="w-full mt-1 px-3 py-2 rounded-lg bg-white/10"
                     type="number" value={extra}
                     onChange={e=>setExtra(Number(e.target.value))}/>
            </label>
          </div>
          <p className="opacity-80">
            Est. payoff: <b>{payoff.months}</b> months • Interest: <b>${payoff.interest}</b>
          </p>
        </div>
      </section>
    </div>
  );
}
