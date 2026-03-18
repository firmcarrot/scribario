# Claude Code Can Now Make Videos -- Lessons Extracted

**Source:** "Claude Code can now make videos, here's how" by David Andre
**URL:** https://youtube.com/watch?v=fOY0_WCR3eY
**Length:** ~16 minutes
**Date extracted:** 2026-03-15

---

## 1. Core Architecture: How It Works

- **Remotion** is the engine. It is a React-based framework for creating videos programmatically. You write React components, and Remotion records them frame-by-frame into MP4 via **FFmpeg**.
- Think of it as "a website that gets recorded frame by frame into a video file."
- Data can come from APIs, databases, or user input. Each render produces a unique video.
- Why AI agents love it: agents are great at writing code but terrible at using complex GUIs (After Effects, Premiere Pro). Remotion turns video creation into React component authoring -- something Claude Code already excels at.

## 2. The Agent Skill System

- Remotion released an **agent skill** -- an instruction file that teaches Claude Code how to work with Remotion's API patterns, component conventions, and animation best practices.
- Skills use **progressive disclosure**: Claude does NOT load the full skill into context. It only loads the specific parts relevant to the current task (e.g., `animations.md`, `timing.md`, `sequencer.md`). This keeps context lean and tokens efficient.
- Skills are an open standard (like MCPs). They work across Claude Code, OpenCode, Agent Zero, and others.
- The skill bundles reference docs for specific topics like 3D, audio, and captions. Claude loads only what it needs.

## 3. Setup (Step by Step)

1. Run `npx create-video` (from remotion.dev) to scaffold a blank Remotion project.
2. Choose: blank template, add Tailwind (yes), add agent skills (yes).
3. Install the Remotion skill via the skills.sh installer (by Vercel). Select Claude Code as the agent. Choose project-level or global install. Use symlink method.
4. Launch Claude Code in the project folder. Run `/skill` to verify the Remotion skill is loaded.
5. Run `npm run dev` to get the local Remotion Studio (browser-based preview player with timeline scrubbing).

## 4. Project Organization Best Practices

- **Dedicated folder:** Create a clean directory for the Remotion project. Do not mix animation files with other project files.
- **Subdirectories per animation:** Tell Claude to create a separate subfolder for each animation/composition. The root should stay clean with no animation files directly in it.
- **Prompts folder:** Create a `prompts/` directory with numbered markdown files (`prompt01.md`, `prompt02.md`, etc.) containing detailed animation descriptions.
- **Assets in `/public`:** Claude automatically moves image assets (PNGs, etc.) into the `public/` directory where Remotion expects them.

## 5. Prompting Strategies

### Be Extremely Detailed
- The best results came from prompts that were 200-400 lines long. Not one-liners.
- Describe each scene, each visual element, transitions, timing, style references.
- Example: "Visual animation in the style of 3Blue1Brown" with detailed descriptions of geometric elements, colors, sequencing.

### Iterative, Not One-Shot
- Do NOT try to generate the entire video in a single prompt. The best animations required **5 to 10 prompts** minimum.
- Start small, preview the result, adjust, repeat.
- Follow-up prompts can be surgical: "change the background gradient to be Claude orange color instead" -- and watch it update in real time.

### Reference a Known Style
- Naming a well-known visual style (e.g., "3Blue1Brown") gives Claude a strong anchor for design decisions.

### Tell Claude to Use the Skill Explicitly
- In your prompt, say "use the Remotion skill" so Claude loads the right context.
- Paste context about what you are doing so Claude understands the project.

### Keep It Modular
- Instruct Claude to build reusable components: intros, transitions, outros as separate components.
- Do NOT put everything into a single monolithic component.

### Shorter Code = Faster Results
- One prompt included: "The fewer lines of code, the better." This prevented Claude from over-engineering and cut generation time from 10+ minutes to ~2 minutes.

## 6. How Clips Are Generated and Stitched

- Remotion uses **Sequence components** to place elements in time (like a timeline in a video editor).
- Each composition has a defined duration in frames (e.g., 2400 frames = 40 seconds at 60fps).
- The Remotion Studio shows a timeline with multiple sequences that can be individually toggled on/off.
- To render the final video: each frame gets screenshotted and stitched into MP4 via FFmpeg.
- Multiple compositions can exist in the same project (e.g., "Pythagorean Proofs" and "Claude Ad" side by side in the browser).

## 7. What Claude Code Actually Generates

- Multiple React component files: one per visual element (e.g., `AnimatedLine`, `Triangle`, `Square`).
- A main orchestrator file that sequences the components.
- A `root.tsx` that registers all compositions.
- The code is typically 70-100+ lines per component file, hundreds of lines total.
- Claude handles imports, variable cleanup, linting fixes automatically.

## 8. Providing Assets

- **High-quality assets dramatically improve output.** If building a product video, provide high-quality product photos. If a game, provide sprites.
- Assets are referenced in prompts and Claude moves them to the right directory.
- Example: a screenshot of the Claude Code UI was provided as `claude-startup.png`, and Claude built an animated ad around it.

## 9. Error Handling and Iteration

- First renders often have issues: misalignment, wrong ordering of sequences, elements slightly off.
- These are fixable with follow-up prompts -- "nothing you can't fix in future prompts."
- Since everything is code, everything is deterministic and adjustable.
- Claude may hit linter errors (unused variables, etc.) and will auto-fix them.
- Long animations (400-line prompts) can take 10+ minutes of Claude Code compute time. Simpler prompts (~200 lines) finish in ~2 minutes.

## 10. Gotchas and Failure Modes

| Gotcha | Detail |
|--------|--------|
| **One-shot complex animations fail** | Always iterate. 5-10 prompts minimum for quality results. |
| **Sequence ordering bugs** | First render may have sequences in wrong order. Fix with follow-up prompt. |
| **Alignment issues** | Elements may be slightly misaligned. Fixable iteratively. |
| **Long generation times** | Complex prompts = 10+ minutes of Claude Code runtime. Manage expectations. |
| **Vague prompts = mediocre results** | Must be extremely detailed. 200-400 line prompts are normal for good output. |
| **Monolithic components** | If you don't tell Claude to be modular, it may dump everything in one file. Explicitly request reusable components. |
| **Context bloat** | The skill system handles this via progressive disclosure, but be aware of token usage on long sessions. |
| **Missing assets** | If you reference images Claude doesn't have, results will be poor. Provide all assets upfront. |

## 11. Tools and Libraries Referenced

| Tool | Purpose |
|------|---------|
| **Remotion** | React framework for programmatic video creation |
| **FFmpeg** | Frame-to-MP4 stitching (used internally by Remotion) |
| **Claude Code** | AI coding agent that writes the Remotion React code |
| **Tailwind CSS** | Styling within Remotion components |
| **skills.sh** | Skill installer (by Vercel) for agent skill management |
| **React** | Component framework Remotion is built on |
| **npm** | Package management and dev server (`npm run dev`) |

## 12. Key Takeaway for Scribario

This pipeline is about **programmatic animation** (motion graphics, product demos, explainers) -- NOT AI-generated video from models like Kie.ai/Runway/Sora. It is complementary:

- **Remotion + Claude Code** = animated motion graphics, UI demos, explainers, product showcases (deterministic, code-based, high control)
- **Kie.ai / image-gen models** = photorealistic or artistic imagery from text prompts (non-deterministic, model-based)

For Scribario's social media content pipeline, Remotion could be used for:
- Animated product showcase reels
- Template-based promo videos (brand colors, logos, text overlays)
- Explainer/how-to animations
- Ad creatives with consistent brand identity

The key advantage: since it is all React code, templates can be parameterized and reused across tenants with different brand assets, colors, and copy.
