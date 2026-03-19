# MASTER LESSONS: AI Video Generation with Veo 3 / 3.1

Consolidated from 21 YouTube videos + 8 web sources. Deduplicated, organized by topic.
Compiled: 2026-03-15

---

## 1. PROMPT STRUCTURE

### The Formula (use every time)

```
[STYLE/FORMAT] + [CAMERA] + [SUBJECT] + [ACTION] + [SETTING] + [LIGHTING] + [AUDIO] + [NEGATIVES]
```

**Style goes FIRST.** Veo weighs the beginning of the prompt more heavily. Start with "cinematic film," "2D anime," "horror movie," etc.

### Optimal Length
- **100-150 words** for Veo (our skill says this, confirmed by multiple sources)
- Short prompts (<50 words) produce generic results
- Over-long prompts (>175 words) confuse the model
- **One subject, one action, max 2 camera movements per clip**

### JSON vs Prose
- JSON prompts work well for structured scenes (products, ads, room transformations)
- For cinematic/emotional content, narrative prose works better
- **Best practice:** Use an LLM (Claude) to translate plain-English creative direction into model-optimized prompts. "The art is your idea, not your prompt."

### Negative Instructions
- Describe unwanted elements as **nouns**, not instructions
- WRONG: "no walls" or "don't show walls"
- RIGHT: Add negative nouns: "wall, frame" or "Avoid: deformed hands, morphing objects, text overlays"
- Put negatives at the END of the prompt

---

## 2. CAMERA CONTROL

### What RELIABLY Works
| Movement | Exact Wording | Reliability |
|----------|---------------|-------------|
| Pan | "camera slowly pans left/right" | High |
| Tilt | "camera tilts up/down to reveal X" | High |
| Zoom in | "camera zooms in on her face" | High |
| Pull back | "camera pulls back to reveal X" | High |
| Static | "locked-off shot" or just don't mention camera | High |
| Handheld | "handheld, natural breathing and micro-sway" | High |
| Tracking | "slow continuous handheld tracking shot at shoulder level" | Medium |
| Dolly in | "camera moves physically closer to subject" | Medium |
| Crane | "camera rises from ground to above the rooftops" | Low-Medium |
| 180° orbit | "fast fluid 180-degree orbit around the subject" | Medium |

### What FAILS
- **"Dolly zoom" / Vertigo effect** — 22% success rate. Skip entirely.
- **3+ camera movements** in one prompt — causes jump cuts instead of smooth motion
- **Rig names** like "crane shot," "dolly" — Veo may render the actual equipment. Describe what the camera SEES physically.
- **"Camera on tripod"** — may literally render a tripod in frame (we learned this the hard way)

### Camera Lens Types That Work
- "shot on a Sony camera" → cinematic photorealistic boost
- "fisheye lens" → ultra-wide distorted look
- "macro lens" → extreme close-up detail
- "85mm lens, f/1.8" → portrait with bokeh (from our Nano Banana skill)
- "35mm, f/2.8" → street/candid feel
- "anamorphic lens" → widescreen cinematic with horizontal bokeh flares

### First-Person / Selfie
- "first-person POV shot" → immersive viewer perspective
- "selfie video" or "self camera angle shot from an extended arm" → vlog style
- Make arm holding camera visible for authenticity

### Time-Based Camera Instructions
You CAN embed timing in prompts:
- "At 2 seconds, the camera begins with a wide shot and slowly zooms in..."
- "At 3 seconds, the camera transitions into a fast orbit..."
- Not 100% reliable but Veo understands these reasonably well

---

## 3. CHARACTER CONSISTENCY

### The Core Problem
Veo has NO memory between generations. Every clip drifts. There is no perfect solution.

### Method 1: Verbatim Text Description (Best for dialogue)
- Write ONE canonical detailed description (face, hair, clothing, accessories)
- Paste it **IDENTICALLY** into every prompt — never paraphrase
- Change only the scene/action portion
- **Pro:** Character can talk (Veo generates dialogue)
- **Con:** Clothing, hair, face structure will still vary between clips

### Method 2: Reference Image → Image-to-Video (Best for visual consistency)
- Generate a high-quality reference image of your character
- Use Flux Context / Nano Banana to create new images of the same character in different scenes
- Upload each image to Veo as first frame → animate with short prompt
- **Pro:** Best visual consistency (face, clothing, accessories match)
- **Con:** NO dialogue generation when using reference images

### Method 3: Green Screen Hack
- Generate character on GREEN SCREEN background
- Upload to frames-to-video
- Start prompt with: "Instantly jump/cut to on frame one"
- Then describe new scene
- **Pro:** Very consistent appearance
- **Con:** Slightly lower quality, no dialogue

### Method 4: Ingredients-to-Video (Veo 3.1)
- Upload up to 3 images (face + object + environment)
- **Only works on 3.1 Fast mode** (not Quality)
- Face likeness works, but clothing/accessories drift
- All images get forced to same crop (can lose details)

### Method 5: Scene Extension (Best for continuity)
- Use "Extend" feature — takes last frame as first frame of next clip
- Paste full character description + new scene into extend prompt
- This is how people make "long" consistent videos
- **Pipeline:** Scene 1 → Extend Scene 2 from last frame → Extend Scene 3...

### Universal Rule
**Re-embed the FULL character description in EVERY scene prompt.** Never assume the model remembers anything.

---

## 4. AUDIO / SFX / DIALOGUE

### Audio Prompting Basics
Veo generates audio from the text prompt. Specify:
1. **Foreground sound** — footsteps, door creaks, engine hum
2. **Ambient bed** — ocean waves, café chatter, wind
3. **Music** — "suspenseful music" or "no background music"
4. **Dialogue** — character speech

### Dialogue Rules
- **Colon syntax REQUIRED:** `He says: "The ocean teaches you respect."`
- NOT quotation marks alone (triggers subtitle hallucination)
- **Max 8 seconds / ~25 words** per clip
- **Always add:** "No subtitles. No on-screen text."
- Repeat "no subtitles" multiple times if needed — model trained on captioned videos
- **Nothing works 100%** for subtitle suppression. Plan to crop or use AI remover tool.

### Tone of Voice
- Describe GENERAL IDEA rather than exact script for better emotional delivery
- "old man whispering about what it was like to fight" > exact word-for-word script
- Tone keywords: "aggressively shouts," "nervous, stuttering, unsure," "quietly whispers"

### Audio Limitations
- Reference image mode (frames-to-video, ingredients) → falls back to Veo2 → **NO AI audio**
- Fast mode → no dialogue
- Video extension → falls back to Veo2, no sound
- **Audio is unpredictable** — can produce random business presentations, gibberish singing, cartoon sounds

### Ambient Sound Examples That Work
- "sound of waves at the beach"
- "sound of a creek running by"
- "sounds of wind rustling and cars honking in the background"
- "the creak of the boat, rhythmic thud of waves, wet slap of the net"
- "café ambiance — distant conversation, espresso machine, soft jazz"

### Accent Control
Accents only work when the ENVIRONMENT makes it plausible from movie training data:
- Brazilian man on beach in Rio → Portuguese accent ✓
- Medieval monastery → British accent ✓
- Star Wars character + "Hispanic accent" → doesn't work ✗

---

## 5. LIGHTING

### Physical Sources (Name them explicitly)
- "soft sunlight beaming through the trees"
- "harsher moonlight casting down"
- "light shining on him from a fire"
- "golden hour backlighting; warm amber rim from sun low on horizon"
- "single motivated source — desk lamp frame right; 4:1 key-to-fill"

### Color Grading Keywords
- **Warm golden** — approachable, nostalgic
- **Cool blue** — cold, dreary, melancholic
- **Desaturated** — gritty, war-film (Saving Private Ryan)
- **Monochromatic** — uneasy, unnatural
- **Light pastel** — soft, gentle
- **Teal and orange** — cinematic blockbuster

### Photorealism Fix
Fantasy/historical prompts often produce video-game style instead of photorealistic.
**Fix:** Add `muted colors, cinematic film` to prompt. If still video-game, change prompt entirely.

### Temperature References
- "Warm 3200K" — intimate, indoor
- "Cool 5600K" — professional, daylight

---

## 6. MULTI-CLIP WORKFLOWS

### The Professional Pipeline
```
Image Generation (validate composition cheaply)
  → Image-to-Video (animate validated frames)
  → Review each clip individually
  → Stitch in editor (CapCut, FFmpeg, Remotion)
  → Post-process (upscale, add text overlays, music)
```

### Key Principles
1. **Image-first, video-second.** Validate composition as a still image before spending on video generation.
2. **5-8 second clips MAX.** Beyond 10 seconds, motion degrades.
3. **Generate 3-5 variations** per prompt — pick the best. Results are non-deterministic.
4. **Use Fast mode for drafting, Quality for finals.** Don't waste premium credits on exploration.
5. **Extend, don't regenerate.** Use scene extension (last frame → first frame) for continuity.

### Chain-of-Frames Method
1. Generate clip 1 with start frame
2. End frame of clip 1 becomes start frame of clip 2
3. Import new end frame for clip 2
4. Generate clip 2 — seamless transition because it starts where clip 1 ended
5. Repeat for unlimited length

### Looping Videos
No native loop. Workaround: duplicate clip in editor, reverse the copy, place side-by-side → seamless loop.

---

## 7. COMMON FAILURE MODES

### Things That ALWAYS Fail
| Problem | Why | Fix |
|---------|-----|-----|
| Readable text on screen | AI can't render text | Generate text with PIL/Remotion, composite in post |
| 3+ camera movements | Causes jump cuts | Max 2 movements per clip |
| Backflips/complex physics | Model can't simulate | Use simpler actions or Sora 2 |
| Morphing end state | Jump-cuts to final frame | Accept mid-transition is the good part |
| Subtitle suppression | Model trained on captioned video | Crop bottom, use AI remover, add "no subtitles" |

### Things That SOMETIMES Fail
| Problem | Why | Fix |
|---------|-----|-----|
| Character drift | No memory between clips | Full description + reference images every time |
| Camera follows instead of static | Prompt ambiguity | Don't mention camera equipment. Describe what's in frame. |
| Cartoon audio on cinematic video | Audio generation is unpredictable | Specify exact ambient sounds. Add SFX in post. |
| Subject mutation (horse+buggy) | Multi-element scenes overwhelm model | Simplify to fewer elements per scene |
| Video-game style instead of photo | Fantasy/historical bias | Add "muted colors, cinematic film" |
| Wrong accent | Training data mismatch | Match accent to plausible environment |

### Our Specific Failures (Hero Video V3)
1. **"Camera static on roadside"** → rendered a literal camera on tripod. **Fix:** Never say "camera" or "tripod." Describe what's IN FRAME.
2. **Buggy in front of horses** → multi-element confusion. **Fix:** Simplify — fewer moving parts per scene.
3. **Cartoon horse sounds** → audio hallucination. **Fix:** Explicitly specify "realistic horse hooves on dirt road, leather creaking" — don't leave audio to chance.
4. **Car from wrong direction** → Veo invented its own spatial logic. **Fix:** Use first/last frame to lock start and end compositions.
5. **Wrong logo** → used wrong asset file. **Fix:** Double-check asset paths before generation.

---

## 8. ITERATION STRATEGY

### The Right Workflow
1. **Plain-English creative brief** → describe what you want and how viewer should FEEL
2. **LLM translates to optimized prompt** → Claude formats it with proper camera, lighting, audio syntax
3. **Generate 3-5 variations** → pick best
4. **Bad result? Describe what's wrong in plain English** → LLM rewrites prompt. Never manually edit prompt syntax.
5. **Use image preview first** → generate still frame to validate composition before spending on video
6. **Fast mode for drafts, Quality for finals**

### One Clip at a Time
**DO NOT** generate all clips blind and hope they work. Generate one, review, iterate until good, then move to next. This is what professionals do.

### The "Expert Critique" Loop (Claude Code + Remotion)
After first pass, ask: "If you were an expert motion graphics designer, what improvements would you make?" Cherry-pick suggestions. This produces significantly better output than iterating blindly.

---

## 9. TOOLS & COST

### Model Selection
| Use Case | Best Model | Cost |
|----------|-----------|------|
| Cinematic environments | Veo 3.1 | $0.40/clip (Fast via Kie.ai) |
| Character narratives | Sora 2 Pro | Higher |
| Social dynamics | Kling 3.0 | Varies |
| Stylized/artistic | Sora 2, Veo 3 | Varies |
| Fast drafts | Kling 2.6, Veo Fast | Cheapest |

### Cost Optimization
- Prototype with Fast mode ($0.40) not Quality ($2.00)
- Validate compositions as images ($0.04) before video ($0.40+)
- Generate 5-second clips (half cost of 10-second)
- Set aspect ratio BEFORE generating (wrong ratio = re-render)

### Post-Processing
- Upscale 1080p → 4K with dedicated upscaler
- Remove subtitles with AI remover (V-Make, etc.)
- Add text overlays with PIL/Remotion (not AI)
- Add music/SFX in post if Veo audio is bad

---

## 10. KEY INSIGHTS FOR SCRIBARIO HERO VIDEO

Based on ALL research, here's what we should do differently:

### Scene-by-Scene Approach
1. Generate each clip individually
2. Ron reviews each one before proceeding
3. Iterate on bad clips before moving to next
4. Stitch only after all clips are approved

### Use First/Last Frame
For scenes where camera position matters (buggy passing camera), generate start and end frame images with Nano Banana, then use FIRST_AND_LAST_FRAMES_2_VIDEO to control the exact motion.

### Simplify Multi-Element Scenes
Horse + buggy + rider + car = too many elements. Break into:
- Wide shot of buggy alone (simple)
- Wide shot of blur streaking past (simple)
- Car alone in reveal shot (simple)
- Mirror close-up (simple)

### Never Mention Camera Equipment
Instead of "camera is static on a tripod at roadside," say:
"A dusty desert road fills the frame. A horse-drawn buggy enters from the left, passes through the center, and exits to the right. The viewpoint does not move."

### Specify Audio Explicitly
Don't leave audio to chance. For every scene:
- Name exact sounds: "horse hooves on packed dirt, leather creaking, wooden wheels crunching gravel"
- Name exact music: "no background music" or "low ambient desert wind"
- Never say just "cinematic audio" — that's a slot machine

### Use Image-First Validation
Before spending $0.40 on a video clip:
1. Generate the scene as a still image ($0.04)
2. Verify composition, subject, lighting
3. Only THEN animate the validated image

### Accept Veo's Limits
- Audio will sometimes be wrong — plan to replace in post
- Characters will drift between clips — use reference images
- Camera won't always follow instructions — use first/last frame for control
- Generate 3-5 variations and pick the best one
