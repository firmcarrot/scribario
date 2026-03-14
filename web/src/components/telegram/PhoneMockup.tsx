"use client";

interface Props {
  children: React.ReactNode;
}

export function PhoneMockup({ children }: Props) {
  return (
    <>
      {/* Desktop: full phone frame */}
      <div className="hidden md:block relative">
        <div
          className="relative w-[320px] h-[640px] rounded-[40px] border-[3px] border-[#2a2a2a] bg-[#1B1B1B] overflow-hidden shadow-2xl shadow-black/50"
        >
          {/* Notch */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[120px] h-[28px] bg-[#050505] rounded-b-2xl z-10" />
          {/* Screen content */}
          <div className="absolute inset-0 pt-7">
            {children}
          </div>
        </div>
      </div>

      {/* Mobile: edge-to-edge, no frame */}
      <div className="md:hidden w-full rounded-xl border border-white/10 overflow-hidden h-[480px]">
        {children}
      </div>
    </>
  );
}
