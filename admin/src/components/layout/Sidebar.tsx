"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  Search,
  BarChart3,
  Users,
  Server,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/blog", label: "Blog", icon: FileText },
  { href: "/keywords", label: "Keywords", icon: Search },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/tenants", label: "Tenants", icon: Users },
  { href: "/system", label: "System", icon: Server },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`flex flex-col border-r transition-all duration-200 ${
        collapsed ? "w-16" : "w-60"
      }`}
      style={{
        borderColor: "var(--color-border)",
        background: "var(--color-bg-card)",
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center h-14 px-4 border-b"
        style={{ borderColor: "var(--color-border)" }}
      >
        {!collapsed && (
          <span
            className="text-lg font-bold tracking-tight"
            style={{ color: "var(--color-accent)" }}
          >
            Scribario
          </span>
        )}
        {collapsed && (
          <span
            className="text-lg font-bold"
            style={{ color: "var(--color-accent)" }}
          >
            S
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 px-2 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/" ? pathname === "/" : pathname.startsWith(href);

          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                collapsed ? "justify-center" : ""
              }`}
              style={{
                background: isActive
                  ? "var(--color-bg-hover)"
                  : "transparent",
                color: isActive
                  ? "var(--color-text)"
                  : "var(--color-text-muted)",
              }}
              title={collapsed ? label : undefined}
            >
              <Icon size={18} />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 border-t cursor-pointer"
        style={{
          borderColor: "var(--color-border)",
          color: "var(--color-text-muted)",
        }}
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  );
}
