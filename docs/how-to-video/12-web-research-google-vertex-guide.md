# Veo on Vertex AI — Official Google Prompt Guide

**Source:** https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide

## Prompt Anatomy

**Subject:** Include specific descriptors — "a seasoned detective" not "a person"
**Action:** Include subtle actions too — "a gentle breeze ruffling hair"
**Scene/Context:** Sensory details matter — "floating dust motes", weather, time of day

## Camera Angles (with reliability notes)

> "Some advanced angles have variable reliability"

- Eye-level, low-angle, high-angle, bird's-eye view
- Close-up, extreme close-up, medium shot, full shot, wide shot
- Over-the-shoulder, POV

## Camera Movements

- Static, pan (left/right), tilt (up/down), dolly (in/out)
- Truck (sideways), pedestal (vertical), zoom
- Crane shots, aerial/drone, handheld, whip pan, arc shots

## Lens & Optical Effects

- Wide-angle, telephoto, shallow DOF, deep DOF
- Lens flare, rack focus, fisheye, vertigo effect (dolly zoom)

## Lighting Types

Natural, artificial, cinematic (Rembrandt, film noir), volumetric, backlighting, golden hour, side lighting

## Negative Prompts (IMPORTANT)

**Describe unwanted elements as NOUNS, not instructions.**

- WRONG: "no walls" or "don't show walls"
- RIGHT: "wall, frame" (as negative nouns)

Example: Adding negative "urban background, man-made structures, dark, stormy atmosphere" produces noticeably different results.

## Audio Direction

Supported by `veo-3.0-generate-001`:
- Use SEPARATE sentences for audio
- Sound effects: "the sound of a phone ringing"
- Ambient: "waves crashing on the shore"
- Dialogue: `the man in the red hat says: Where is the rabbit?`

## Cinematic Editing Terms

Match cut, jump cut, establishing shot sequence, montage, split diopter effect — these terms influence generation style.

## Key Guidance

- Not all advanced angles/lenses are reliable
- Short clips (5-8s) work better than long ones for subtle evolution
- Specificity prevents generic outputs
- Separate audio from visual descriptions in prompt
