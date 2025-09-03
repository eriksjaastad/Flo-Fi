
"use client";
import { useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, ReferenceLine
} from "recharts";

type Row = {
  Date: Date;
  Merchant: string;
  Category: string;
  Amount: number;
  Account: string;
};

const COLORS = ["#60a5fa","#34d399","#fbbf24","#f472b6","#c084fc","#f87171","#a3e635","#22d3ee"];

const monthKey = (d: Date) => {
  const y = d.getFullYear();
  const m = String(d.getMonth()+1).padStart(2,"0");
  return `${y}-${m}`;
};

function inCat(category: string, row: Row, merchantList: string[]) {
  return merchantList.some(m => row.Merchant.toLowerCase().includes(m.toLowerCase()));
}

// Map your four-card categories by merchant keywords (editable!)
const CARD_MAP: Record<string, string[]> = {
  "Housing & Insurance": ["geico","extra space storage"],
  "Connectivity & Utilities": ["starlink","verizon","at&t"],
  "Digital & Lifestyle": [
    "prime video","amazon digital","dreamhost","apple","itunes","icloud","namecheap",
    "spotify","netflix","audible","google one","wikipedia","new york times","xbox","niantic"
  ],
  "AI & Tools": ["cursor","claude","openai","whop","chatgpt","anthropic"]
};

export default function Dashboard({ rows }: { rows: Row[] }) {
  // 1) Monthly income vs spend (simple: positives = income/refunds, negatives = spend)
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

  // 2) Category by your 4-card buckets
  const byCard = useMemo(() => {
    const sums: Record<string, number> = { "Housing & Insurance":0, "Connectivity & Utilities":0, "Digital & Lifestyle":0, "AI & Tools":0, "Other":0 };
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

  // 3) Smoking heuristic: Gas category & >= $100 charge
  const smoking = useMemo(() => {
    const filtered = rows.filter(r => r.Category.toLowerCase().includes("gas") && r.Amount <= -100);
    const perMonth: Record<string, number> = {};
    for (const r of filtered) {
      const k = monthKey(r.Date);
      perMonth[k] = (perMonth[k] || 0) + Math.abs(r.Amount);
    }
    const series = Object.entries(perMonth).sort().map(([Month, total]) => ({ Month, total: Math.round(total*100)/100 }));
    const total = series.reduce((a,b)=>a+b.total,0);
    return { series, total: Math.round(total*100)/100, count: filtered.length };
  }, [rows]);

  // 4) Impulse detector: large purchases > $1000 not in Transfer/Loan/Credit Card Payment
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

  // 5) Day-of-month pattern for charges > $500 with same exclusions
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

  // 6) Simple payoff sandbox (set slider in UI in future; fixed extra for starter)
  const payoff = useMemo(() => {
    // Starter stub: assume $6,900 @ 20% APR, $300/mo min, +$300 extra
    const bal0 = 6900, apr=0.20, min=300, extra=300;
    let bal = bal0, months=0, interest=0;
    while (bal > 0 && months < 120) {
      const monthlyRate = apr/12;
      const int = bal * monthlyRate;
      interest += int;
      let pay = Math.min(bal+int, min+extra);
      bal = bal + int - pay;
      months++;
    }
    return { months, interest: Math.round(interest*100)/100 };
  }, []);

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-3">Monthly Income vs. Spend</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthly}>
              <XAxis dataKey="Month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="income" stackId="a" fill="#34d399" />
              <Bar dataKey="spend" stackId="a" fill="#f87171" />
              <ReferenceLine y={0} stroke="#fff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="rounded-2xl bg-[var(--card)] p-6">
        <h2 className="text-xl font-semibold mb-3">Your 4-Card Categories</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={byCard} dataKey="value" nameKey="name" outerRadius={120}>
                {byCard.map((entry, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
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
            <h3 className="mb-1 opacity-80">Count of > $1,000 by Month</h3>
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
            <h3 className="mb-1 opacity-80">Day-of-Month (>$500)</h3>
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
        <h2 className="text-xl font-semibold mb-1">Debt Payoff (Sandbox)</h2>
        <p className="opacity-80 mb-3">Example: ~$6,900 @ 20% APR with $300 min + $300 extra → ~{ "{"+`payoff.months`+"}"} months; interest ≈ ${"{"+`payoff.interest`+"}"} (make this interactive later).</p>
      </section>
    </div>
  );
}
