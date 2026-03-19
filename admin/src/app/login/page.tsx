"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const errorParam = searchParams.get("error");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const supabase = createClient();
    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    router.push("/");
    router.refresh();
  };

  return (
    <div
      className="w-full max-w-sm rounded-lg border p-8"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <h1
        className="text-2xl font-bold text-center mb-1"
        style={{ color: "var(--color-accent)" }}
      >
        Scribario
      </h1>
      <p
        className="text-sm text-center mb-6"
        style={{ color: "var(--color-text-muted)" }}
      >
        Admin Command Center
      </p>

      {(error || errorParam === "not_authorized") && (
        <div
          className="text-sm rounded-md px-3 py-2 mb-4 border"
          style={{
            color: "var(--color-danger)",
            borderColor: "var(--color-danger)",
            background: "rgba(239, 68, 68, 0.1)",
          }}
        >
          {error || "You are not authorized to access this admin panel."}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            className="block text-xs font-medium mb-1.5"
            style={{ color: "var(--color-text-muted)" }}
          >
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors"
            style={{
              background: "var(--color-bg)",
              borderColor: "var(--color-border)",
              color: "var(--color-text)",
            }}
            onFocus={(e) =>
              (e.currentTarget.style.borderColor = "var(--color-accent)")
            }
            onBlur={(e) =>
              (e.currentTarget.style.borderColor = "var(--color-border)")
            }
          />
        </div>
        <div>
          <label
            className="block text-xs font-medium mb-1.5"
            style={{ color: "var(--color-text-muted)" }}
          >
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors"
            style={{
              background: "var(--color-bg)",
              borderColor: "var(--color-border)",
              color: "var(--color-text)",
            }}
            onFocus={(e) =>
              (e.currentTarget.style.borderColor = "var(--color-accent)")
            }
            onBlur={(e) =>
              (e.currentTarget.style.borderColor = "var(--color-border)")
            }
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md py-2 text-sm font-medium transition-opacity cursor-pointer disabled:opacity-50"
          style={{
            background: "var(--color-accent)",
            color: "#ffffff",
          }}
        >
          {loading ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: "var(--color-bg)" }}
    >
      <Suspense>
        <LoginForm />
      </Suspense>
    </div>
  );
}
