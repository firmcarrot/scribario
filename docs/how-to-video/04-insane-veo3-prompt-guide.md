# INSANE Google Veo 3 Prompt Guide for AI Cinematic Video

**Source:** [Full Google Veo 3 Tutorial (2025)](https://youtube.com/watch?v=jnye_QbkZxM)
**Creator:** Zapiwala
**Duration:** ~23 minutes
**Platform:** Google Flow (Veo 3 access point)

---

## The 7 Tips (Summary)

1. Start strong with a cinematic hook
2. Define core visuals (who, what, where)
3. Layer atmosphere and sensory details
4. Choreograph motion + camera movement
5. Use compositional language (frame with intention)
6. Be concise and precise (every word counts)
7. Treat every prompt as standalone (Veo has no memory)

---

## 1. Camera Control

### What Works
- **Name the camera type explicitly:** "wide-angle," "handheld camera," "tracking shot"
- **Name the movement:** "tracks," "slow push-in," "follows"
- **Pair camera with subject action:** "A handheld camera tracks a panicked man sprinting down a dim hospital corridor"
- **Specify lens behavior:** "The lens catches soft flares"

### What Fails
- "The camera shows it" -- too vague, Veo doesn't know what to do
- No camera mention at all -- you get flat, default framing
- "Shows" as a camera verb -- tells Veo nothing about angle, movement, or style

### Exact Wording That Works
- `"A wide-angle golden hour shot captures..."` -- sets lens + lighting in one phrase
- `"A handheld camera tracks..."` -- defines style (shaky/urgent) + movement
- `"A tracking shot follows..."` -- smooth follow movement
- `"Framed in the lower third..."` -- explicit composition placement

### Camera Terms Veo Understands
- Wide-angle, handheld, tracking shot
- Rule of thirds, lower third framing
- Blurred foreground (for depth)
- Off-center placement
- Depth, focus, symmetry, negative space

---

## 2. Character Consistency Across Clips

### The Core Problem
**Veo has ZERO memory between prompts.** Each prompt is processed in complete isolation. If you say "the same guy continues running," Veo will generate a totally different person.

### What Fails
- "Then the same guy continues running through the forest" -- Veo doesn't know who "the same guy" is
- Using "next," "then," or "as before" -- these reference nothing
- Assuming continuity from a previous generation

### The Fix: Full Re-Description Every Time
Every prompt in a multi-clip sequence must:
1. **Re-describe the character fully** -- appearance, clothing, distinguishing features
2. **Re-describe the setting** -- don't just name it, rebuild it visually
3. **Re-describe the mood/action** -- treat it as a fresh scene

### Example of the Fix
BAD: `"Then the same guy continues running through the forest."`

GOOD: `"A tracking shot follows the same bearded man in a soaked flannel shirt as he pushes through thick fog among tall pine trees. He coughs and yells, 'If anyone's still alive, I'm here.'"`

Key details repeated: "bearded man," "soaked flannel shirt" -- these are the visual anchors that keep the character recognizable across clips.

---

## 3. Audio/SFX/Dialogue Prompting

### Dialogue is Non-Negotiable
Every single example prompt in this tutorial includes dialogue. The creator treats dialogue as a core component, not optional. Silent characters produce "flat and passive" results.

### How to Write Dialogue for Veo 3
- Use the phrase **"says clearly"** or **"shouts"** or **"mutters clearly"** or **"yells"**
- Put the dialogue in quotes
- Keep it to 1-2 sentences max
- The dialogue should carry emotional weight / narrative meaning

### Exact Dialogue Patterns That Work
- `...and says clearly, "I think I'm ready to start over."`
- `...and says clearly, "I've been here before, but something's different."`
- `...and says clearly, "The forest remembers everything, even the lies."`
- `...and shouts, "Is anyone in there? Please answer me."`
- `...he mutters clearly, "She always loved mornings like this."`
- `...and yells, "If anyone's still alive, I'm here."`
- `...says calmly, "I never thought I'd make it this far."`

### Pattern
The word **"clearly"** appears repeatedly with dialogue verbs. This likely helps Veo produce intelligible speech rather than mumbled audio.

### Ambient Sound
Sensory descriptions double as sound design cues:
- "Leaves rustle softly" -- triggers rustling audio
- "Steam rises from the grates" -- triggers ambient hissing
- "Waves lapping at the posts" -- triggers water sounds
- "Fluorescent lights flicker overhead" -- triggers buzzing/flickering audio

---

## 4. Lighting Techniques

### What Works
- **Golden hour:** `"A wide-angle golden hour shot"` -- warm, cinematic, soft shadows
- **Moonlight:** `"Pale moonlight filters through twisted trees, casting long shadows"` -- eerie, dramatic
- **Neon:** `"neon-lit Tokyo alley at night"` -- cyberpunk/noir mood
- **Sunrise:** `"His eyes squint into the sunrise"` -- warm, nostalgic
- **Flickering artificial light:** `"Fluorescent lights flicker overhead"` -- tension, horror
- **Firelight:** `"flames dance in the blurred foreground"` -- intimate, warm

### What Fails
- "It's kind of dark" -- Veo doesn't know HOW to light the scene
- No lighting mention -- you get flat, default lighting
- Abstract mood words without visual specifics ("peaceful," "mysterious")

### Key Insight
**Lighting defines tone.** Always specify whether it's harsh daylight, moody shadows, golden hour, moonlit, neon-lit, etc. The lighting choice IS the emotional direction.

### Lighting + Shadow Pairing
Explicitly describe both what's lit AND the shadows:
- "Pale moonlight... casting long shadows on the mossy ground"
- "Flames dance in the blurred foreground... snow-covered trees fade into darkness"

---

## 5. Common Failure Modes and Fixes

### Failure: Vague/Generic Output
**Cause:** Prompt is too short or uses generic words
**Fix:** Replace every generic word with a specific one

| Generic (fails) | Specific (works) |
|---|---|
| "a man" | "a disheveled man in a wrinkled brown coat" |
| "a city" | "a neon-lit Tokyo alley at night" |
| "it's dark" | "pale moonlight filters through twisted trees, casting long shadows" |
| "it's windy" | "leaves rustle softly" + "low fog drifts between roots" |
| "a nice place" | "the edge of a wooden dock, waves lapping at the posts" |
| "walking" | "walks briskly" / "sprinting" / "pushes through" |
| "peaceful" | (show it visually: golden light, slow motion, soft focus) |

### Failure: Flat Composition
**Cause:** No framing instructions
**Fix:** Tell Veo WHERE to place the subject and what's in foreground/background

### Failure: No Emotional Impact
**Cause:** No dialogue, no character emotion, no sensory details
**Fix:** Add all three -- facial expression + dialogue + environment that reinforces the mood

### Failure: Inconsistent Characters Across Clips
**Cause:** Relying on Veo's (nonexistent) memory
**Fix:** Full character re-description in every prompt

### Failure: "Maybe" / "Kind of" / Hedging Language
**Cause:** Uncertainty in the prompt transfers to uncertainty in the output
**Fix:** Be declarative. Never use "maybe," "kind of," "somehow," "sort of"

---

## 6. Prompt Structure and Length

### The Anatomy of a Strong Veo 3 Prompt

Every prompt should contain these layers (in roughly this order):

1. **Cinematic Hook** -- Camera type + lighting/time of day + visual style
2. **Core Visuals** -- Subject (detailed appearance), action (specific verb), setting (textured)
3. **Atmosphere** -- Sensory details: light quality, shadows, fog, texture, ambient elements
4. **Motion** -- What the subject is doing AND what the camera is doing
5. **Composition** -- Where the subject is framed, foreground/background relationship
6. **Dialogue** -- Character speaks with emotional weight (use "says clearly")

### Prompt Length
The good prompts shown are 2-4 sentences. Not paragraphs. Concise but dense with visual information.

### Template (Merged from All 7 Tips)
```
[Camera type + movement] [lighting/time] shot [captures/follows/tracks]
[detailed subject description + clothing + appearance] [specific action verb]
[in/through/at] [detailed setting with texture + atmosphere].
[Sensory detail: light, shadow, fog, sound, weather].
[Subject does secondary action] and [says/shouts/mutters] clearly,
"[1-2 sentences of emotionally weighted dialogue]."
```

### Anti-Patterns (What NOT to Write)
- Don't write like a novelist -- no flowery prose
- Don't use filler words: "maybe," "kind of," "somehow," "sort of"
- Don't use abstract emotions without visual grounding ("it feels mysterious")
- Don't reference previous prompts ("then," "next," "as before," "the same guy")
- Don't use vague verbs: "doing something," "looking," "walking" (without adverb)

---

## 7. Multi-Clip Storytelling

### Rules for Sequences
1. **Each prompt is standalone** -- complete scene in itself
2. **Re-describe everything** -- character, setting, mood, lighting
3. **Never reference previous prompts** -- no "then," "next," "continues"
4. **Use consistent visual anchors** -- same clothing description, same distinguishing features (beard, coat color, shirt type) across all prompts in a sequence
5. **Each clip should have its own dialogue** -- advances the story

### Workflow for Multi-Clip Projects
1. Plan your scenes as a storyboard
2. Write each prompt independently
3. Use identical character descriptions (copy-paste the subject description)
4. Vary camera angles and settings between clips for visual interest
5. Each prompt gets its own dialogue line that advances the narrative

---

## 8. Full Example Prompts from the Video

### Example 1: Wheat Field (Good Prompt)
> A wide-angle golden hour shot captures a young woman standing alone in a sun-drenched wheat field. The lens catches soft flares as she looks into the sky and says clearly, "I think I'm ready to start over."

### Example 2: Tokyo Alley (Good Prompt)
> A disheveled man in a wrinkled brown coat walks briskly through a neon-lit Tokyo alley at night. Steam rises from the grates. He pauses, looks at a flickering sign, and says clearly, "I've been here before, but something's different."

### Example 3: Forest/Moonlight (Good Prompt)
> Pale moonlight filters through twisted trees, casting long shadows on the mossy ground. A low fog drifts between roots as leaves rustle softly. A girl stands barefoot, holding a lantern, and says clearly, "The forest remembers everything, even the lies."

### Example 4: Hospital Corridor (Good Prompt -- Motion Focus)
> A handheld camera tracks a panicked man sprinting down a dim hospital corridor. Fluorescent lights flicker overhead. He skids to a stop at a closed door and shouts, "Is anyone in there? Please answer me."

### Example 5: Campfire (Good Prompt -- Composition Focus)
> Framed in the lower third, a man kneels beside a campfire as flames dance in the blurred foreground. Behind him, snow-covered trees fade into darkness. He looks at the flames and says calmly, "I never thought I'd make it this far."

### Example 6: Fisherman/Dock (Good Prompt -- Precision Focus)
> A weathered fisherman stands alone at the edge of a wooden dock, waves lapping at the posts. His eyes squint into the sunrise as he mutters clearly, "She always loved mornings like this."

### Example 7: Forest Survival (Good Prompt -- Standalone/Consistency Focus)
> A tracking shot follows the same bearded man in a soaked flannel shirt as he pushes through thick fog among tall pine trees. He coughs and yells, "If anyone's still alive, I'm here."

---

## Bonus: ChatGPT Prompt Expansion Workflow

The creator's "magical prompt template" workflow:
1. Take a meta-prompt template that encodes all 7 tips
2. Paste it into ChatGPT
3. Replace the "Enter your idea here" line with a plain-English video concept
4. ChatGPT expands it into a full Veo 3 prompt incorporating all 7 principles
5. Copy the output and paste into Veo 3

This is useful for batch content generation -- describe scenes in plain English, let an LLM expand them into properly structured Veo 3 prompts.

---

## Key Takeaways for Scribario

1. **Every video prompt needs:** camera type, lighting, detailed subject, specific action, setting texture, and dialogue
2. **"Says clearly" is the magic phrase** for getting intelligible dialogue from Veo 3
3. **No memory between generations** -- for multi-clip content, copy-paste character descriptions
4. **Show, don't tell emotions** -- describe the visual that creates the feeling, not the feeling itself
5. **2-4 sentences is the sweet spot** -- dense with visual info, no filler
6. **The LLM expansion workflow** is directly applicable to Scribario's pipeline -- user provides concept, Claude expands into Veo-optimized prompt
