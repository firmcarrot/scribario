# Veo 3 Prompting Guide — Replicate Blog

**Source:** https://replicate.com/blog/using-and-prompting-veo-3

## Core Prompt Structure (7 Elements)

1. **Subject** — who/what appears
2. **Context** — location
3. **Action** — movement/behavior
4. **Style** — aesthetic approach
5. **Camera motion** — how the shot moves
6. **Composition** — framing technique
7. **Ambiance** — mood and lighting

## Character Consistency (CRITICAL)

- Keep character descriptions **identical verbatim** across all prompts
- Same prompt = same character (Veo is deterministic with similar seeds)
- More unique/specific descriptions = better visual continuity
- Example: "John, a man in his 40s with short brown hair, wearing a blue jacket and glasses, looking thoughtful"
- If you want VARIATION, change multiple attributes simultaneously

## Dialogue Rules

- **8 seconds max** of speech per clip
- Too much dialogue = unnatural fast-talking
- Too little = "awkward silences or AI gibberish"
- Explicit format: `A guy says: My name is Ben` (colon syntax)
- Implicit format: `A guy tells us his name`
- Phonetic spelling for hard names: "foh-fur" not "Opher"
- Attribute speakers by visible traits: "The woman wearing pink says:..."

## Subtitle Suppression

- Use colon syntax (not quotation marks)
- Add `(no subtitles)` in prompt
- Repeat: "No subtitles. No subtitles!" multiple times if needed
- Model trained on videos with baked-in subtitles — it WANTS to add them

## Audio Control

Four elements to specify:
1. **Dialogue** — what people say
2. **Ambient noise** — street sounds, café sounds
3. **Sound effects** — phones, doors, external noises
4. **Music** — cinematic scores, specific genres

**Common hallucination:** "live studio audience" laughter appears randomly. Fix by explicitly specifying ambient: "sounds of distant bands, noisy crowd, ambient background of a busy festival field"

## Style Transformations

Supported: LEGO, Claymation, South Park, Pixar, 8-bit retro, Graphic novel, Origami, Simpsons, Blueprint, Anime, Marble

Format: `In the style of [style name]: [detailed scene description]`

## Selfie Video Technique

- Start prompt with "A selfie video of..."
- Make arm holding camera visible: "holds the camera at arm's length. His long, powerful arm is clearly visible"
- Natural eye movement: "occasionally looking into the camera before turning to point at interesting stalls"
- Add grain: "slightly grainy, looks very film-like" (reduces AI look)

## Camera Movements

eye level, high angle, worms eye, dolly shot, zoom shot, pan shot, tracking shot

## Key Insight

"Even with a fairly simple prompt, Veo 3 will output very similar results with identical seeds." This means **same prompt = consistent character** but also means you must change prompts significantly to explore variations.
