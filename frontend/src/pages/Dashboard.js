import React from "react";
import { useQuery } from "react-query";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
} from "recharts";
import {
  getFinancialSummary,
  getAppointments,
  getLowStockAlerts,
  getRevenueByCategory,
} from "../api/client";
import { format } from "date-fns";

const COLORS = ["#b48ef0", "#e8c97a", "#6fcfcf", "#e88fa0"];

export default function Dashboard() {
  const today = format(new Date(), "yyyy-MM-dd");

  const { data: summary } = useQuery("summary-month", () =>
    getFinancialSummary("month")
  );
  const { data: appointments } = useQuery("appts-today", () =>
    getAppointments({ date_from: today, date_to: today })
  );
  const { data: lowStock } = useQuery("low-stock", getLowStockAlerts);
  const { data: revCat } = useQuery("rev-category", getRevenueByCategory);

  const todayAppts = appointments || [];
  const alerts = lowStock?.count || 0;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Good morning ✦</h1>
        <p className="page-subtitle">
          {format(new Date(), "EEEE, MMMM d, yyyy")} — Studio Overview
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Monthly Revenue</div>
          <div className="stat-value stat-value--iris">
            ${summary?.revenue?.toLocaleString("en-US", { maximumFractionDigits: 0 }) || "—"}
          </div>
          <div className="stat-delta">This month</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Net Profit</div>
          <div className="stat-value stat-value--gold">
            ${summary?.net_profit?.toLocaleString("en-US", { maximumFractionDigits: 0 }) || "—"}
          </div>
          <div className="stat-delta">{summary?.profit_margin_pct || 0}% margin</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Today's Appointments</div>
          <div className="stat-value stat-value--teal">{todayAppts.length}</div>
          <div className="stat-delta">Scheduled today</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Low Stock Alerts</div>
          <div className="stat-value stat-value--rose">{alerts}</div>
          <div className="stat-delta">Items need reorder</div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-title">Revenue by Service</div>
          {revCat && revCat.length > 0 ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={revCat}
                    dataKey="total"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={3}
                  >
                    {revCat.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: "#1a1720", border: "1px solid #333", borderRadius: 8 }}
                    formatter={(v) => [`$${v.toFixed(2)}`, "Revenue"]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">◎</div>
              <div>No revenue data yet</div>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-title">Today's Schedule</div>
          {todayAppts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">◷</div>
              <div>No appointments today</div>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Client</th>
                    <th>Service</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {todayAppts.slice(0, 6).map((a) => (
                    <tr key={a.id}>
                      <td>{format(new Date(a.scheduled_at), "h:mm a")}</td>
                      <td>{a.client.first_name} {a.client.last_name}</td>
                      <td>{a.service.name}</td>
                      <td>
                        <span className={`badge badge--${a.status}`}>{a.status}</span>
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