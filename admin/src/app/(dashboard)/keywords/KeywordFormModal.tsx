"use client";

import { useState } from "react";
import { createKeyword, updateKeyword } from "./actions";

interface Keyword {
  id: string;
  keyword: string;
  cluster: string | null;
  search_volume: number | null;
  difficulty: number | null;
  trend: string | null;
  priority: string | null;
}

interface Props {
  keyword?: Keyword | null;
  onClose: () => void;
  onSaved: () => void;
}

export function KeywordFormModal({ keyword, onClose, onSaved }: Props) {
  const isEdit = !!keyword;
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    keyword: keyword?.keyword || "",
    cluster: keyword?.cluster || "",
    search_volume: keyword?.search_volume?.toString() || "",
    difficulty: keyword?.difficulty?.toString() || "",
    trend: keyword?.trend || "stable",
    priority: keyword?.priority || "medium",
  });

  const handleSubmit = async () => {
    if (!form.keyword.trim()) {
      setError("Keyword is required");
      return;
    }

    setSaving(true);
    setError("");

    const data = {
      keyword: form.keyword.trim(),
      cluster: form.cluster.trim() || null,
      search_volume: form.search_volume ? parseInt(form.search_volume, 10) : null,
      difficulty: form.difficulty ? parseInt(form.difficulty, 10) : null,
      trend: form.trend,
      priority: form.priority,
    };

    const result = isEdit
      ? await updateKeyword(keyword!.id, data)
      : await createKeyword(data);

    setSaving(false);

    if (result.error) {
      setError(result.error);
      return;
    }

    onSaved();
  };

  const inputStyle = {
    background: "var(--color-bg)",
    borderColor: "var(--color-border)",
    color: "var(--color-text)",
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      style={{ background: "rgba(0,0,0,0.6)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="rounded-xl p-6 border w-full max-w-md flex flex-col gap-4"
        style={{
          background: "var(--color-bg-card)",
          borderColor: "var(--color-border)",
        }}
      >
        <h2
          className="text-lg font-bold"
          style={{ color: "var(--color-text)" }}
        >
          {isEdit ? "Edit Keyword" : "Add Keyword"}
        </h2>

        {error && (
          <p className="text-sm px-3 py-2 rounded" style={{ background: "rgba(255,59,48,0.15)", color: "var(--color-danger)" }}>
            {error}
          </p>
        )}

        <div className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Keyword *"
            value={form.keyword}
            onChange={(e) => setForm({ ...form, keyword: e.target.value })}
            className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Cluster"
            value={form.cluster}
            onChange={(e) => setForm({ ...form, cluster: e.target.value })}
            className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
            style={inputStyle}
          />
          <div className="grid grid-cols-2 gap-3">
            <input
              type="number"
              placeholder="Search volume"
              value={form.search_volume}
              onChange={(e) => setForm({ ...form, search_volume: e.target.value })}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={inputStyle}
            />
            <input
              type="number"
              placeholder="Difficulty (0-100)"
              value={form.difficulty}
              onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
              min={0}
              max={100}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={inputStyle}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <select
              value={form.trend}
              onChange={(e) => setForm({ ...form, trend: e.target.value })}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={inputStyle}
            >
              <option value="rising">Rising</option>
              <option value="stable">Stable</option>
              <option value="declining">Declining</option>
            </select>
            <select
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={inputStyle}
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3 justify-end mt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm cursor-pointer"
            style={{ color: "var(--color-text-muted)" }}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-50"
            style={{ background: "var(--color-accent)", color: "#fff" }}
          >
            {saving ? "Saving..." : isEdit ? "Update" : "Add"}
          </button>
        </div>
      </div>
    </div>
  );
}
