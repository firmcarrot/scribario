# Claude Code Video Toolkit — Digital Samba

**Source:** https://github.com/digitalsamba/claude-code-video-toolkit

## What It Is

AI-native video production system for Claude Code. Makes explainer-style videos (product demos, sprint reviews, presentations) using Remotion (React-based video) + AI tools.

## Architecture

### Skills (Domain Knowledge)
- **Remotion** — React-based video framework
- **ElevenLabs** — AI TTS, voice cloning, music synthesis
- **FFmpeg** — media processing
- **Playwright** — browser automation for recording demos
- **Qwen-Edit** — AI image manipulation
- **RunPod** — cloud GPU for heavy processing

### Multi-Session Project Lifecycle
```
planning → assets → review → audio → editing → rendering → complete
```

Each project gets `project.json` tracking scenes, audio, sessions, phase, config.
Auto-generated `CLAUDE.md` for instant session resumption.

## Production Workflow

1. Create project → select template + brand
2. Edit `VOICEOVER-SCRIPT.md` → plan scenes, timing
3. Gather assets (browser captures, imports, reference images)
4. Scene review in Remotion Studio
5. Design refinement (colors, fonts, spacing)
6. Generate audio (ElevenLabs or Qwen3-TTS)
7. Configure asset paths, durations, transitions
8. Preview live in studio
9. Iterate with Claude Code
10. Render final MP4

## Transitions Library

Custom: glitch, rgbSplit, zoomBlur, lightLeak, clockWipe, pixelate, checkerboard
Official Remotion: slide, fade, wipe, flip

## Key Insight for Our Work

This toolkit is **Remotion-based** (React components defining frames). It's a DIFFERENT approach from our Veo clip generation + FFmpeg stitching pipeline. Could be useful for:
- CTA cards and text overlays (React renders pixel-perfect text)
- Transitions between AI-generated clips
- Precise timing control

## Python Tools

- voiceover.py — TTS generation
- music.py — background music
- sfx.py — sound effects
- redub.py — replace audio
- addmusic.py — add music to video
- image_edit.py — AI image editing
- upscale.py — 2x/4x upscaling
- dewatermark.py — watermark removal
- flux2.py — AI image generation

## Cost

RunPod: pay-per-second, ~$0.01-0.15 per job, typical monthly under $10.

## Error Handling

- Project reconciliation validates intent vs filesystem
- Session recovery for incomplete projects
- Fallback patterns (ElevenLabs → Qwen3-TTS, RunPod → local CPU)
