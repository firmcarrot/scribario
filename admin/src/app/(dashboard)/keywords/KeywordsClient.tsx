"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Upload, Pencil, Trash2 } from "lucide-react";
import { KeywordFormModal } from "./KeywordFormModal";
import { CSVImportModal } from "./CSVImportModal";
import { deleteKeyword } from "./actions";

const ROTATION_COLORS: Record<string, string> = {
  available: "var(--color-success)",
  in_use: "var(--color-warning)",
  cooldown: "var(--color-danger)",
};

interface Keyword {
  id: string;
  keyword: string;
  cluster: string | null;
  search_volume: number | null;
  difficulty: number | null;
  trend: string | null;
  priority: string;
  rotation_status: string;
  times_used: number;
}

export function KeywordsClient({ keywords }: { keywords: Keyword[] }) {
  const router = useRouter();
  const [showAdd, setShowAdd] = useState(false);
  const [showCSV, setShowCSV] = useState(false);
  const [editingKw, setEditingKw] = useState<Keyword | null>(null);

  const handleSaved = () => {
    setShowAdd(false);
    setEditingKw(null);
    router.refresh();
  };

  const handleDelete = async (id: string, keyword: string) => {
    if (!confirm(`Delete keyword "${keyword}"?`)) return;
    await deleteKeyword(id);
    router.refresh();
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Keyword Library</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowCSV(true)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium cursor-pointer"
            style={{
              border: "1px solid var(--color-border)",
              color: "var(--color-text-muted)",
            }}
          >
            <Upload size={14} />
            Import CSV
          </button>
          <button
            onClick={() => setShowAdd(true)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium cursor-pointer"
            style={{ background: "var(--color-accent)", color: "#fff" }}
          >
            <Plus size={14} />
            Add Keyword
          </button>
        </div>
      </div>

      {keywords.length === 0 ? (
        <div
          className="rounded-lg p-8 border text-center"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
            color: "var(--color-text-muted)",
          }}
        >
          No keywords tracked yet. Add keywords to start building your SEO strategy.
        </div>
      ) : (
        <div
          className="rounded-lg border overflow-hidden"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                {["Keyword", "Cluster", "Volume", "Difficulty", "Trend", "Priority", "Status", "Used", ""].map(
                  (h) => (
                    <th
                      key={h}
                      className="text-left px-4 py-3 text-xs font-medium uppercase tracking-wider"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {keywords.map((kw) => (
                <tr
                  key={kw.id}
                  className="hover:opacity-80"
                  style={{ borderBottom: "1px solid var(--color-border)" }}
                >
                  <td
                    className="px-4 py-3 font-medium"
                    style={{ color: "var(--color-text)" }}
                  >
                    {kw.keyword}
                  </td>
                  <td
                    className="px-4 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {kw.cluster || "\u2014"}
                  </td>
                  <td
                    className="px-4 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {kw.search_volume ?? "\u2014"}
                  </td>
                  <td
                    className="px-4 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {kw.difficulty ?? "\u2014"}
                  </td>
                  <td
                    className="px-4 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {kw.trend || "\u2014"}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className="capitalize"
                      style={{
                        color:
                          kw.priority === "high"
                            ? "var(--color-danger)"
                            : kw.priority === "medium"
                              ? "var(--color-warning)"
                              : "var(--color-text-muted)",
                      }}
                    >
                      {kw.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                      style={{
                        color:
                          ROTATION_COLORS[kw.rotation_status] ||
                          "var(--color-text-muted)",
                        background: `color-mix(in srgb, ${ROTATION_COLORS[kw.rotation_status] || "var(--color-text-muted)"} 15%, transparent)`,
                      }}
                    >
                      {kw.rotation_status}
                    </span>
                  </td>
                  <td
                    className="px-4 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {kw.times_used}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      <button
                        onClick={() => setEditingKw(kw)}
                        className="p-1.5 rounded cursor-pointer hover:opacity-70"
                        style={{ color: "var(--color-text-muted)" }}
                        title="Edit"
                      >
                        <Pencil size={14} />
                      </button>
                      <button
                        onClick={() => handleDelete(kw.id, kw.keyword)}
                        className="p-1.5 rounded cursor-pointer hover:opacity-70"
                        style={{ color: "var(--color-danger)" }}
                        title="Delete"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showAdd && (
        <KeywordFormModal onClose={() => setShowAdd(false)} onSaved={handleSaved} />
      )}
      {editingKw && (
        <KeywordFormModal
          keyword={editingKw}
          onClose={() => setEditingKw(null)}
          onSaved={handleSaved}
        />
      )}
      {showCSV && (
        <CSVImportModal
          onClose={() => setShowCSV(false)}
          onImported={() => {
            setShowCSV(false);
            router.refresh();
          }}
        />
      )}
    </div>
  );
}
