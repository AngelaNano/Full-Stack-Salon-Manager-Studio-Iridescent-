import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { format } from "date-fns";
import toast from "react-hot-toast";
import {
  getAppointments,
  createAppointment,
  updateAppointment,
  cancelAppointment,
  getClients,
  sendConfirmation,
} from "../api/client";

const SERVICES = [
  { id: 1, name: "Haircut & Style", duration_minutes: 60, price: 85 },
  { id: 2, name: "Color Treatment", duration_minutes: 120, price: 180 },
  { id: 3, name: "Blowout", duration_minutes: 45, price: 55 },
  { id: 4, name: "Deep Conditioning", duration_minutes: 45, price: 65 },
  { id: 5, name: "Balayage", duration_minutes: 180, price: 280 },
];

const STATUS_OPTIONS = ["pending", "confirmed", "completed", "cancelled"];

export default function Appointments() {
  const qc = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState("");
  const [form, setForm] = useState({
    client_id: "",
    service_id: "",
    scheduled_at: "",
    notes: "",
  });

  const { data: appointments, isLoading } = useQuery(
    ["appointments", filterStatus],
    () => getAppointments(filterStatus ? { status: filterStatus } : {})
  );
  const { data: clients } = useQuery("clients", () => getClients());

  const createMut = useMutation(createAppointment, {
    onSuccess: () => {
      qc.invalidateQueries("appointments");
      toast.success("Appointment booked!");
      setShowModal(false);
      setForm({ client_id: "", service_id: "", scheduled_at: "", notes: "" });
    },
    onError: (e) => toast.error(e.response?.data?.error || "Booking failed"),
  });

  const cancelMut = useMutation(cancelAppointment, {
    onSuccess: () => {
      qc.invalidateQueries("appointments");
      toast.success("Appointment cancelled");
    },
  });

  const statusMut = useMutation(({ id, status }) => updateAppointment(id, { status }), {
    onSuccess: () => {
      qc.invalidateQueries("appointments");
      toast.success("Status updated");
    },
  });

  const confirmMut = useMutation(sendConfirmation, {
    onSuccess: () => toast.success("Confirmation email sent"),
    onError: () => toast.error("Email send failed"),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMut.mutate(form);
  };

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="page-title">Appointments</h1>
          <p className="page-subtitle">Schedule and manage client bookings</p>
        </div>
        <button className="btn btn--primary" onClick={() => setShowModal(true)}>
          + New Booking
        </button>
      </div>

      <div className="search-bar">
        <select
          className="select"
          style={{ width: 180 }}
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="loading">Loading appointments…</div>
        ) : appointments?.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">◷</div>
            <div>No appointments found</div>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Client</th>
                  <th>Service</th>
                  <th>Price</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments?.map((a) => (
                  <tr key={a.id}>
                    <td>{format(new Date(a.scheduled_at), "MMM d, yyyy h:mm a")}</td>
                    <td>{a.client.first_name} {a.client.last_name}</td>
                    <td>{a.service.name}</td>
                    <td>${a.service.price}</td>
                    <td>
                      <select
                        className="select"
                        style={{ width: 130, padding: "4px 8px", fontSize: 12 }}
                        value={a.status}
                        onChange={(e) => statusMut.mutate({ id: a.id, status: e.target.value })}
                      >
                        {STATUS_OPTIONS.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          className="btn btn--ghost"
                          style={{ padding: "5px 10px", fontSize: 12 }}
                          onClick={() => confirmMut.mutate(a.id)}
                        >
                          ✉ Confirm
                        </button>
                        <button
                          className="btn btn--danger"
                          style={{ padding: "5px 10px", fontSize: 12 }}
                          onClick={() => cancelMut.mutate(a.id)}
                        >
                          Cancel
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">New Appointment</div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Client</label>
                <select
                  className="select"
                  required
                  value={form.client_id}
                  onChange={(e) => setForm({ ...form, client_id: e.target.value })}
                >
                  <option value="">Select client…</option>
                  {clients?.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.first_name} {c.last_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Service</label>
                <select
                  className="select"
                  required
                  value={form.service_id}
                  onChange={(e) => setForm({ ...form, service_id: e.target.value })}
                >
                  <option value="">Select service…</option>
                  {SERVICES.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} — ${s.price} ({s.duration_minutes} min)
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Date & Time</label>
                <input
                  type="datetime-local"
                  className="input"
                  required
                  value={form.scheduled_at}
                  onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Notes</label>
                <textarea
                  className="input"
                  rows={3}
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Optional notes…"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn--ghost" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn--primary" disabled={createMut.isLoading}>
                  {createMut.isLoading ? "Booking…" : "Book Appointment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}