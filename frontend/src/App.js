import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { Toaster } from "react-hot-toast";
import Dashboard from "./pages/Dashboard";
import Appointments from "./pages/Appointments";
import Clients from "./pages/Clients";
import Inventory from "./pages/Inventory";
import Finance from "./pages/Finance";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } },
});

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: "◈" },
  { to: "/appointments", label: "Appointments", icon: "◷" },
  { to: "/clients", label: "Clients", icon: "◉" },
  { to: "/inventory", label: "Inventory", icon: "◫" },
  { to: "/finance", label: "Finance", icon: "◎" },
];

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app-shell">
          <aside className="sidebar">
            <div className="sidebar-brand">
              <span className="brand-gem">✦</span>
              <div>
                <div className="brand-name">Studio</div>
                <div className="brand-sub">Iridescent</div>
              </div>
            </div>
            <nav className="sidebar-nav">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    `nav-item ${isActive ? "nav-item--active" : ""}`
                  }
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
            <div className="sidebar-footer">
              <div className="studio-status">
                <span className="status-dot" />
                Studio Open
              </div>
            </div>
          </aside>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/appointments" element={<Appointments />} />
              <Route path="/clients" element={<Clients />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/finance" element={<Finance />} />
            </Routes>
          </main>
        </div>
        <Toaster position="top-right" />
      </Router>
    </QueryClientProvider>
  );
}