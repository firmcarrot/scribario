"use client";

import { useState } from "react";
import { importKeywordsFromCSV } from "./actions";

interface Props {
  onClose: () => void;
  onImported: () => void;
}

export function CSVImportModal({ onClose, onImported }: Props) {
  const [csvText, setCsvText] = useState("");
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<{
    imported: number;
    skipped: number;
    errors: string[];
  } | null>(null);

  const handleImport = async () => {
    if (!csvText.trim()) return;
    setImporting(true);
    const res = await importKeywordsFromCSV(csvText);
    setResult(res);
    setImporting(false);

    if (res.imported > 0) {
      setTimeout(() => onImported(), 1500);
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 1_000_000) {
      setResult({ imported: 0, skipped: 0, errors: ["File too large. Max 1MB."] });
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      // Strip BOM if present
      setCsvText(text.replace(/^\uFEFF/, ""));
    };
    reader.readAsText(file);
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      style={{ background: "rgba(0,0,0,0.6)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="rounded-xl p-6 border w-full max-w-lg flex flex-col gap-4"
        style={{
          background: "var(--color-bg-card)",
          borderColor: "var(--color-border)",
        }}
      >
        <h2
          className="text-lg font-bold"
          style={{ color: "var(--color-text)" }}
        >
          Import Keywords from CSV
        </h2>

        <div className="flex flex-col gap-2">
          <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            Required column: <code>keyword</code>. Optional: <code>cluster</code>,{" "}
            <code>search_volume</code>, <code>difficulty</code>, <code>trend</code>,{" "}
            <code>priority</code>. Max 1000 rows.
          </p>

          <label
            className="flex items-center gap-2 px-3 py-2 rounded-lg border text-sm cursor-pointer"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-muted)",
            }}
          >
            <span>Upload CSV file</span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFile}
              className="hidden"
            />
          </label>

          <textarea
            value={csvText}
            onChange={(e) => setCsvText(e.target.value)}
            placeholder={`keyword,cluster,search_volume,difficulty,trend,priority\nai social media,automation,1200,35,rising,high`}
            rows={8}
            className="w-full px-3 py-2 rounded-lg text-xs font-mono border outline-none resize-y"
            style={{
              background: "var(--color-bg)",
              borderColor: "var(--color-border)",
              color: "var(--color-text)",
            }}
          />
        </div>

        {result && (
          <div
            className="rounded-lg p-3 text-sm"
            style={{
              background:
                result.imported > 0
                  ? "rgba(52,199,89,0.1)"
                  : "rgba(255,59,48,0.1)",
              color:
                result.imported > 0
                  ? "var(--color-success)"
                  : "var(--color-danger)",
            }}
          >
            <p className="font-medium">
              {result.imported} imported, {result.skipped} skipped
            </p>
            {result.errors.length > 0 && (
              <ul className="mt-1 text-xs list-disc list-inside">
                {result.errors.slice(0, 5).map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
                {result.errors.length > 5 && (
                  <li>...and {result.errors.length - 5} more</li>
                )}
              </ul>
            )}
          </div>
        )}

        <div className="flex gap-3 justify-end mt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm cursor-pointer"
            style={{ color: "var(--color-text-muted)" }}
          >
            Close
          </button>
          <button
            onClick={handleImport}
            disabled={importing || !csvText.trim()}
            className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-50"
            style={{ background: "var(--color-accent)", color: "#fff" }}
          >
            {importing ? "Importing..." : "Import"}
          </button>
        </div>
      </div>
    </div>
  );
}
