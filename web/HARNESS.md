# SCRIBARIO BUILD HARNESS — ABSOLUTE LAW

**This file overrides all defaults, including CLAUDE.md brand tokens. Every rule is mandatory. No exceptions. No shortcuts. No "I'll do it later." Violating any rule means: stop, revert, start over.**

---

## THE BUILD LOOP (EVERY COMPONENT, EVERY TIME)

```
0.  BASELINE SCREENSHOT — Before changing anything, screenshot current state
    (desktop + mobile), read both images, describe what exists. This is your baseline.
1.  VERIFY DEV SERVER IS RUNNING (npm run dev — confirm localhost:3000 responds)
2.  INVOKE brainstorming SKILL — engage fully (see SKILL ENGAGEMENT below)
3.  INVOKE frontend-design SKILL — engage fully (see SKILL ENGAGEMENT below)
4.  WRITE ONE COMPONENT (not 7 files at once — ONE)
5.  BUILD CHECK (npm run build — must pass with zero errors)
6.  SCREENSHOT (node scripts/screenshot.mjs — desktop + mobile)
7.  READ THE SCREENSHOT (use Read tool on the PNG files in tmp_screenshots/)
8.  EVALUATE (list specific issues: spacing, colors, typography, alignment)
9.  FIX ISSUES (if any found in step 8)
10. SCREENSHOT AGAIN (verify fixes)
11. READ AND CONFIRM (screenshot looks good)
12. PRESENT TO RON — show desktop + mobile screenshots, ask:
    "Phase/component X complete. Any issues before I move on?"
    WAIT for Ron's response. Silence ≠ approval.
13. ONLY THEN move to next component
```

**You may NOT skip to step 5 without completing steps 0-4.**
**You may NOT move to the next component without completing steps 5-12.**
**"It's just a utility file" is NOT an excuse to skip screenshots (see UTILITY EXCEPTION below).**

---

## ANTI-LAZINESS RULES

### 1. ONE FILE AT A TIME
- Write ONE file → build → screenshot → verify → next file
- NEVER write 3+ files before checking if anything works

**UTILITY EXCEPTION (narrow):** Files that produce ZERO visual output — `scroll-engine.ts`, `useScrollProgress.ts`, and `globals.css` — need only a build check (no screenshot). But:
- `GradientText.tsx`, `ClipCard.tsx`, and ANY .tsx component ARE visual — full screenshot loop required
- If you create more than 2 non-visual files in sequence without screenshotting something visual, STOP. You are batch-writing. This exception exists for 3 specific files, not for splitting components into pieces to dodge screenshots.

### 2. SKILLS ARE NOT CHECKBOXES
- If you invoke a skill and immediately say "skill invoked, moving on" — that's a violation
- See SKILL ENGAGEMENT section below for minimum requirements

### 3. SCREENSHOTS ARE MANDATORY
- After writing ANY .tsx or .css file: screenshot
- After fixing ANY visual issue: screenshot
- Before declaring ANY section done: full-page screenshot (desktop + mobile)
- Use `node scripts/screenshot.mjs` for full page
- Use `node scripts/screenshot.mjs --section [id]` for specific sections
- Use `node scripts/screenshot.mjs --viewport` for above-the-fold
- READ the screenshot file with the Read tool — don't just take it and ignore it
- If the screenshot shows a blank/error page, the dev server is down — fix it FIRST

### 4. DEV SERVER MUST BE RUNNING
- Before ANY visual work: confirm dev server is live
- If it's not running: `npm run dev &` and wait for it
- If it crashes: fix the error FIRST, then continue

### 5. BUILD BEFORE SCREENSHOT
- `npm run build` must pass BEFORE you screenshot
- If build fails: fix it immediately, don't move on
- TypeScript errors, import errors, missing deps — fix them NOW

### 6. NO BATCH WRITING
- Do NOT use the Agent tool to parallelize visual component writing
- Do NOT write Hero + HowItWorks + FAQ + Footer in one go
- Each section is a full loop: design → write → build → screenshot → verify → fix → screenshot

### 7. ITERATION CAP
- If you have iterated on a component **3 times** and it still has issues, STOP
- Present the current screenshot to Ron with a specific numbered list of remaining issues
- Do not iterate endlessly — ask for direction

### 8. GIT COMMIT BETWEEN PHASES
- At the end of each completed phase, `git commit` with a descriptive message
  - Example: `feat: phase 1 — light theme globals and scroll engine foundation`
  - Example: `feat: phase 2 — floating transparent navbar`
- This creates rollback points so a bad phase doesn't destroy good work
- Do NOT push — just commit locally

---

## SKILL ENGAGEMENT — MINIMUM REQUIREMENTS

### brainstorming — MUST produce ALL of these before writing code:
1. **Specific layout description** — not "a hero section" but "centered hero with clip-path card opening from `inset(0 64px round 45px)`, sticky phone inside, massive bg text below at 19.4vw"
2. **ForHims pattern being cloned** — which specific ForHims section (hero, program, care, shop, etc.) and what's different
3. **A question to Ron** asking for confirmation or redirect
4. **Wait for Ron's response** — do NOT proceed without explicit "go ahead" or similar

### frontend-design — MUST specify ALL of these for the component:
1. **Font sizes** in vw units (consult `reference_forhims_extraction.md` for exact values)
2. **Colors/gradients** — exact hex/rgba values being used, which Scribario brand colors replace ForHims colors
3. **Spacing** — margins and padding in vw units
4. **Animation/interaction** — what scroll-triggers, what transforms, using RAF engine or Framer Motion?
5. **Layout difference from previous section** — how this section differs visually from the one above it

---

## ANIMATION BOUNDARY: FRAMER MOTION vs RAF ENGINE

- **Framer Motion:** Entrance animations only — staggered fades on mount, mount/unmount transitions, `whileInView` reveals
- **Custom RAF scroll engine:** ALL scroll-driven animations — clip-path reveals, parallax, sticky elements, opacity-on-scroll, nav color swap
- Do NOT use Framer Motion's `useScroll` or `useTransform` for scroll effects. Use the custom engine.

---

## COMPONENT BUILD ORDER

**Build for 1440px desktop first** (the ForHims extraction is at desktop scale). After each component passes desktop screenshots, immediately check 375px mobile. Fix mobile before moving on.

```
Phase 1: Foundation (non-visual — build check only, NO screenshots)
  □ globals.css — light theme tokens (OVERRIDES dark tokens in CLAUDE.md)
  □ scroll-engine.ts — RAF utilities (lerp, clamp, remap, iLerp, ease)
  □ useScrollProgress.ts — per-section scroll progress hook
  → npm run build after each, confirm zero errors
  → git commit

Phase 2: Visual Utilities + Nav (visual — full screenshot loop)
  □ GradientText.tsx — add to homepage temporarily, screenshot, verify gradient renders
  □ ClipCard.tsx — add to homepage temporarily, screenshot, verify clip-path works
  □ Navbar.tsx — floating transparent nav with logo swap
  → screenshot each, read, verify
  → Remove temporary test renders from homepage before moving on
  → Present to Ron: "Phase 2 complete. Screenshots attached. Any issues?"
  → git commit

Phase 3: Hero (visual — full screenshot loop)
  □ Hero.tsx — clip-path card + sticky phone + massive bg text
  → screenshot, read, verify, iterate (max 3 iterations then ask Ron)
  → Present to Ron
  → git commit

Phase 4: Content sections (visual — full screenshot loop EACH)
  □ HowItWorks.tsx — Programs-style clip-path card
  → screenshot, read, verify
  □ Demo.tsx — dark accent zone with conversation
  → screenshot, read, verify
  □ Platforms.tsx — Shop-style clip-path card
  → screenshot, read, verify
  → Present all 3 to Ron
  → git commit

Phase 5: Supporting sections (visual — full screenshot loop EACH)
  □ FAQ.tsx — restyle with ForHims typography/spacing
  → screenshot, read, verify
  □ Footer.tsx — dark zone footer
  → screenshot, read, verify
  □ CTA section — centered logo + pill button
  → screenshot, read, verify
  → Present all 3 to Ron
  → git commit

Phase 6: Full QA — Homepage
  □ Remove any temporary test renders or dev routes created during Phase 2
  □ Full-page desktop screenshot (1440px) → read → list every issue
  □ Full-page mobile screenshot (375px) → read → list every issue
  □ Fix all issues
  □ Final screenshots → confirm both pass
  → Present to Ron
  → git commit

Phase 7: Getting Started Page
  □ Restyle /getting-started to match new light theme
  □ Screenshot at both viewports
  → Present to Ron
  → git commit

Phase 8: Final
  □ npm run build — zero errors
  □ DA review agent — spawn, address all issues
  □ Final full-page screenshots both pages, both viewports
  □ Present to Ron for final sign-off
```

---

## QUALITY GATES

Before moving from Phase N to Phase N+1:
1. All components in Phase N build without errors
2. All components in Phase N have been screenshotted and visually verified
3. **Ron has explicitly approved Phase N output** (silence ≠ approval)

Before declaring the site "done":
1. Full-page screenshots at 1440px and 375px for BOTH pages (/ and /getting-started)
2. Every section visually verified
3. `npm run build` passes
4. DA review agent spawned and issues addressed
5. Ron's explicit sign-off

---

## REFERENCE DOCUMENT

For exact CSS values, spacing, typography, gradients, and animation details, always consult:

**`reference_forhims_extraction.md`** in the project root.

Key values to reference:
- Clip-path: `inset(0px 64px round 45px)` → opens to `inset(0px 0px round 0px)`
- Side margins: 64px on cards/sections
- Section spacing: `clamp(6rem, 12vw, 12rem)` vertical (Apple-level generous)
- Hero heading: `clamp(3.5rem, 7vw, 7rem)`, letter-spacing -0.04em
- Section headings: `clamp(2.5rem, 5vw, 5rem)`, letter-spacing -0.03em
- Feature heading: `clamp(1.75rem, 3vw, 3rem)`, letter-spacing -0.02em
- Body copy: `clamp(1.25rem, 2vw, 2rem)`, letter-spacing -0.01em
- Nav: fixed, height 0, transparent, z-index 4
- CTA pill: border-radius 52px, padding 16px 22px, box-shadow rgba(0,0,0,0.06) 0px 8px 30px
- Dark zone bg: #0A0A0F (near-black, NOT old navy #1A1A2E)

---

## THE SITE RON WANTS

- **Light theme** (#FFFFFF base — NOT dark. CLAUDE.md dark tokens are OVERRIDDEN.)
- ForHims structural clone (clip-path reveals, massive typography, sticky phone)
- Premium — belongs on godly.website
- Scribario brand colors (coral-orange #FF6B4A accent, Telegram blue #0088CC)
- Custom RAF scroll engine (NO GSAP, NO AOS, NO Framer Motion useScroll)
- Existing Telegram components (`src/components/telegram/*`) are KEPT as-is
- vw-based fluid typography (-0.0475em to -0.0575em letter-spacing)
- White base with ONE dark accent zone (the Demo/Telegram section)
- Floating zero-height transparent nav with logo color swap on dark sections
