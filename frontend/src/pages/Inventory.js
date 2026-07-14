import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import toast from "react-hot-toast";
import { getInventory, updateInventoryItem } from "../api/client";

export default function Inventory() {
  const qc = useQueryClient();
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [qty, setQty] = useState("");

  const { data: items, isLoading } = useQuery(
    ["inventory", lowStockOnly],
    () => getInventory(lowStockOnly ? { low_stock: "true" } : {})
  );

  const updateMut = useMutation(({ id, data }) => updateInventoryItem(id, data), {
    onSuccess: () => {
      qc.invalidateQueries("inventory");
      toast.success("Stock updated");
      setEditItem(null);
    },
  });

  const handleRestock = (item) => {
    setEditItem(item);
    setQty(item.quantity);
  };

  const submitRestock = () => {
    updateMut.mutate({ id: editItem.id, data: { quantity: parseInt(qty) } });
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Inventory</h1>
        <p className="page-subtitle">Track product stock and reorder levels</p>
      </div>

      <div className="search-bar">
        <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", fontSize: 13, color: "var(--text-mid)" }}>
          <input
            type="checkbox"
            checked={lowStockOnly}
            onChange={(e) => setLowStockOnly(e.target.checked)}
            style={{ accentColor: "var(--iris)" }}
          />
          Show low stock only
        </label>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="loading">Loading inventory…</div>
        ) : items?.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">◫</div>
            <div>No inventory items found</div>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Stock</th>
                  <th>Reorder At</th>
                  <th>Unit Cost</th>
                  <th>Supplier</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items?.map((item) => (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td style={{ color: "var(--text-mid)" }}>{item.category || "—"}</td>
                    <td>
                      <span style={{ fontVariantNumeric: "tabular-nums", fontWeight: 600 }}>
                        {item.quantity}
                      </span>
                    </td>
                    <td style={{ color: "var(--text-dim)" }}>{item.reorder_threshold}</td>
                    <td style={{ color: "var(--text-mid)" }}>
                      {item.unit_cost ? `$${item.unit_cost.toFixed(2)}` : "—"}
                    </td>
                    <td style={{ color: "var(--text-mid)" }}>{item.supplier || "—"}</td>
                    <td>
                      {item.low_stock ? (
                        <span className="badge badge--low">Low Stock</span>
                      ) : (
                        <span className="badge badge--confirmed">In Stock</span>
                      )}
                    </td>
                    <td>
                      <button
                        className="btn btn--ghost"
                        style={{ padding: "5px 12px", fontSize: 12 }}
                        onClick={() => handleRestock(item)}
                      >
                        Restock
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {editItem && (
        <div className="modal-overlay" onClick={() => setEditItem(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">Restock: {editItem.name}</div>
            <div className="form-group">
              <label className="form-label">New Quantity</label>
              <input
                type="number"
                className="input"
                min="0"
                value={qty}
                onChange={(e) => setQty(e.target.value)}
              />
            </div>
            <div style={{ fontSize: 13, color: "var(--text-dim)", marginBottom: 16 }}>
              Current stock: {editItem.quantity} units · Reorder threshold: {editItem.reorder_threshold}
            </div>
            <div className="modal-actions">
              <button className="btn btn--ghost" onClick={() => setEditItem(null)}>Cancel</button>
              <button className="btn btn--primary" onClick={submitRestock}>
                Update Stock
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}