import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": process.env.REACT_APP_API_KEY || "dev-api-key-change-in-production",
  },
});

// ── Appointments ─────────────────────────────────────────────
export const getAppointments = (params = {}) =>
  api.get("/appointments/", { params }).then((r) => r.data);

export const getAppointment = (id) =>
  api.get(`/appointments/${id}`).then((r) => r.data);

export const createAppointment = (data) =>
  api.post("/appointments/", data).then((r) => r.data);

export const updateAppointment = (id, data) =>
  api.patch(`/appointments/${id}`, data).then((r) => r.data);

export const cancelAppointment = (id) =>
  api.delete(`/appointments/${id}`).then((r) => r.data);

export const getAvailability = (date) =>
  api.get("/appointments/availability", { params: { date } }).then((r) => r.data);

// ── Clients ──────────────────────────────────────────────────
export const getClients = (search = "") =>
  api.get("/clients/", { params: { search } }).then((r) => r.data);

export const getClient = (id) =>
  api.get(`/clients/${id}`).then((r) => r.data);

export const createClient = (data) =>
  api.post("/clients/", data).then((r) => r.data);

export const updateClient = (id, data) =>
  api.put(`/clients/${id}`, data).then((r) => r.data);

// ── Inventory ────────────────────────────────────────────────
export const getInventory = (params = {}) =>
  api.get("/inventory/", { params }).then((r) => r.data);

export const getLowStockAlerts = () =>
  api.get("/inventory/alerts").then((r) => r.data);

export const updateInventoryItem = (id, data) =>
  api.patch(`/inventory/${id}`, data).then((r) => r.data);

// ── Finance ──────────────────────────────────────────────────
export const getFinancialSummary = (period = "month") =>
  api.get("/finance/summary", { params: { period } }).then((r) => r.data);

export const getRevenueByCategory = () =>
  api.get("/finance/revenue-by-category").then((r) => r.data);

export const getTransactions = (params = {}) =>
  api.get("/finance/transactions", { params }).then((r) => r.data);

// ── Notifications ────────────────────────────────────────────
export const sendConfirmation = (appointmentId) =>
  api.post(`/notifications/appointment-confirmation/${appointmentId}`).then((r) => r.data);

export const sendReminder = (appointmentId) =>
  api.post(`/notifications/reminder/${appointmentId}`).then((r) => r.data);

export default api;