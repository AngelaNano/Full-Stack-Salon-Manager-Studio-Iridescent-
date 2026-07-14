import React, { useState } from "react";
import { useQuery } from "react-query";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { getFinancialSummary, getTransactions, getRevenueByCategory } from "../api/client";

const TOOLTIP_STYLE = {
  contentStyle: { background: "#1a1720", border: "1px solid #333", borderRadius: 8, fontSize: 13 },
};

export default function Finance() {
  const [period, setPeriod] = useState("month");

  const { data: summary } = useQuery(["summary", period], () => getFinancialSummary(period));
  const { data: transactions } = useQuery("transactions", () => getTransactions({ limit: 20 }));
  const { data: revCat } = useQuery("rev-category", getRevenueByCategory);

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="page-title">Finance</h1>
          <p className="page-subtitle">Revenue, expenses, and profitability</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {["week", "month", "year"].map((p) => (
            <button
              key={p}
              className={`btn ${period === p ? "btn--primary" : "btn--ghost"}`}
              style={{ padding: "7px 14px", fontSize: 12 }}
              onClick={() => setPeriod(p)}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Revenue</div>
          <div className="stat-value stat-value--iris">
            ${summary?.revenue?.toLocaleString("en-US", { maximumFractionDigits: 0 }) || "—"}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Expenses</div>
          <div className="stat-value stat-value--rose">
            ${summary?.expenses?.toLocaleString("en-US", { maximumFractionDigits: 0 }) || "—"}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Net Profit</div>
          <div className="stat-value stat-value--gold">
            ${summary?.net_profit?.toLocaleString("en-US", { maximumFractionDigits: 0 }) || "—"}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Profit Margin</div>
          <div className="stat-value stat-value--teal">
            {summary?.profit_margin_pct || 0}%
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-title">Revenue by Category</div>
          {revCat && revCat.length > 0 ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revCat} margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="category" tick={{ fill: "#5a5370", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#5a5370", fontSize: 11 }} />
                  <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [`$${v.toFixed(2)}`, "Revenue"]} />
                  <Bar dataKey="total" fill="#b48ef0" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="empty-state"><div className="empty-state-icon">◎</div><div>No data yet</div></div>
          )}
        </div>

        <div className="card">
          <div className="card-title">Recent Transactions</div>
          {transactions?.length === 0 ? (
            <div className="empty-state"><div className="empty-state-icon">◎</div><div>No transactions</div></div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions?.slice(0, 8).map((t) => (
                    <tr key={t.id}>
                      <td style={{ fontSize: 12, color: "var(--text-dim)" }}>
                        {new Date(t.transaction_date).toLocaleDateString()}
                      </td>
                      <td>
                        <span className={`badge ${t.type === "revenue" ? "badge--confirmed" : "badge--low"}`}>
                          {t.type}
                        </span>
                      </td>
                      <td style={{ color: "var(--text-mid)" }}>{t.category || "—"}</td>
                      <td style={{ color: t.type === "revenue" ? "var(--teal)" : "var(--rose)", fontWeight: 600 }}>
                        {t.type === "expense" ? "-" : "+"}${t.amount.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}