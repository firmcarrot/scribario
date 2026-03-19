"use client";

import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";

export default function Header() {
  const router = useRouter();
  const supabase = createClient();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  return (
    <header
      className="flex items-center justify-between h-14 px-6 border-b"
      style={{
        borderColor: "var(--color-border)",
        background: "var(--color-bg-card)",
      }}
    >
      <div />
      <button
        onClick={handleLogout}
        className="flex items-center gap-2 text-sm cursor-pointer px-3 py-1.5 rounded-md transition-colors"
        style={{ color: "var(--color-text-muted)" }}
        onMouseEnter={(e) =>
          (e.currentTarget.style.color = "var(--color-text)")
        }
        onMouseLeave={(e) =>
          (e.currentTarget.style.color = "var(--color-text-muted)")
        }
      >
        <LogOut size={16} />
        <span>Logout</span>
      </button>
    </header>
  );
}
