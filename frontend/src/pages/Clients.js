import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import toast from "react-hot-toast";
import { getClients, createClient, updateClient } from "../api/client";

export default function Clients() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", phone: "", notes: "" });

  const { data: clients, isLoading } = useQuery(["clients", search], () => getClients(search));

  const createMut = useMutation(createClient, {
    onSuccess: () => { qc.invalidateQueries("clients"); toast.success("Client added!"); closeModal(); },
    onError: (e) => toast.error(e.response?.data?.error || "Failed to add client"),
  });

  const updateMut = useMutation(({ id, data }) => updateClient(id, data), {
    onSuccess: () => { qc.invalidateQueries("clients"); toast.success("Client updated"); closeModal(); },
  });

  const openNew = () => {
    setEditing(null);
    setForm({ first_name: "", last_name: "", email: "", phone: "", notes: "" });
    setShowModal(true);
  };

  const openEdit = (client) => {
    setEditing(client);
    setForm({ first_name: client.first_name, last_name: client.last_name, email: client.email, phone: client.phone || "", notes: client.notes || "" });
    setShowModal(true);
  };

  const closeModal = () => { setShowModal(false); setEditing(null); };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editing) updateMut.mutate({ id: editing.id, data: form });
    else createMut.mutate(form);
  };

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="page-title">Clients</h1>
          <p className="page-subtitle">Manage your client roster</p>
        </div>
        <button className="btn btn--primary" onClick={openNew}>+ Add Client</button>
      </div>

      <div className="search-bar">
        <input
          className="input"
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span style={{ fontSize: 13, color: "var(--text-dim)" }}>
          {clients?.length || 0} clients
        </span>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="loading">Loading clients…</div>
        ) : clients?.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">◉</div>
            <div>No clients found</div>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Appointments</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {clients?.map((c) => (
                  <tr key={c.id}>
                    <td>{c.first_name} {c.last_name}</td>
                    <td style={{ color: "var(--text-mid)" }}>{c.email}</td>
                    <td style={{ color: "var(--text-mid)" }}>{c.phone || "—"}</td>
                    <td>
                      <span className="badge badge--confirmed">{c.appointment_count}</span>
                    </td>
                    <td style={{ color: "var(--text-dim)", fontSize: 12 }}>
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <button
                        className="btn btn--ghost"
                        style={{ padding: "5px 12px", fontSize: 12 }}
                        onClick={() => openEdit(c)}
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{editing ? "Edit Client" : "New Client"}</div>
            <form onSubmit={handleSubmit}>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">First Name</label>
                  <input className="input" required value={form.first_name}
                    onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name</label>
                  <input className="input" required value={form.last_name}
                    onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input className="input" type="email" required value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Phone</label>
                <input className="input" type="tel" value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Notes</label>
                <textarea className="input" rows={3} value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Allergies, preferences, etc." />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn--ghost" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn--primary">
                  {editing ? "Save Changes" : "Add Client"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}