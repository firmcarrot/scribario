# Veo 3 JSON Prompting Guide

**Source:** "This Is How To Use Google Veo 3 Like A PRO: JSON Prompt (The Only Guide You Need)"
**URL:** https://youtube.com/watch?v=6LhkvHfpjAY
**Creator:** Unknown (references work by Tim Simmons and Mentor on Twitter)

---

## What Is JSON Prompting for Veo 3?

JSON prompting is a method of structuring your Veo 3 prompts using JSON format instead of freeform text. It defines roles and instructions as structured key-value pairs, making it easier for the AI model to parse exactly what you want.

The key insight: JSON uses readable tokens that eliminate ambiguity. Instead of natural language with filler words ("and also add the environment to this, um, and do this but don't do this"), JSON separates each instruction into discrete, labeled fields.

---

## JSON vs. Freeform Text: Head-to-Head Comparison

The video shows a direct A/B comparison using the same scene concept (a revenge monologue: "She left me. But I'll have my revenge. I'm going to find that man in a blue business suit and make him pay."):

| Aspect | Freeform Text Prompt | JSON Prompt |
|--------|---------------------|-------------|
| Visual quality | "Looks really good" but generic | "Way more cinematic" -- looks like a real ad |
| Style control | Limited, model interprets loosely | Precise cinematic direction embedded in structure |
| Consistency | Hit or miss on tone | Reliable cinematic output |
| Production value | Decent AI video | Comparable to $100K CGI/VFX productions |

**Bottom line:** Same content, same model, dramatically different output quality. JSON prompting is what separates amateur AI video from professional-looking ads.

---

## How JSON Prompts Work

JSON prompting structures your creative direction into labeled fields rather than prose. The format:

- Eliminates ambiguity by separating concerns (visuals, audio, camera, characters)
- Uses "readable tokens" that the model can parse more reliably than natural language
- Defines roles and instructions explicitly
- Removes filler/fluff words that dilute the signal

The video shows JSON prompts that look "complicated" at first glance but are described as straightforward once you understand the structure. The prompts control:

1. **Visual scene description** -- what appears on screen
2. **Camera behavior** -- movement, angles, transitions
3. **Character details** -- appearance, clothing, actions
4. **Audio/dialogue direction** -- voiceover, sound design, music
5. **Lighting/mood** -- cinematic atmosphere, color grading
6. **Product placement** -- how branded items appear and interact

---

## Practical Workflow

### Step 1: Generate the JSON Prompt

Use ChatGPT (Projects feature) or Gemini (Gems) with:
- **System instructions** that define the JSON prompt format
- **Reference file** containing example JSON prompts as few-shot examples

Then simply tell it what you want: "Create a JSON prompt for a Tesla ad" or "Create a JSON prompt for [product description] -- I want it to start hovering in a bathroom..." The LLM generates a correctly structured JSON prompt in seconds.

**Pro tip:** You can attach a product image and describe it ("this is my product, it does XYZ, create a JSON prompt for it") for custom brand ads.

### Step 2: Generate the Video

1. Go to **flow.google** (Google Flow -- requires Gemini AI Pro subscription)
2. Click "Create with Flow" then "New Project"
3. Paste the JSON prompt directly into the prompt field
4. Configure settings before generating:
   - **Model:** Use **Veo 3 Fast** (not V2 -- V2 has no audio support)
   - **Quality:** Fast mode = 720p at 20 credits; Quality mode = higher res at more credits
   - **Outputs:** Set to 1 to conserve credits (or 2 if you have plenty)
5. Hit Generate

### Step 3: Post-Processing

- **720p fast mode** output can be upscaled to 1080p using Flow's built-in download/upscale
- **4K** achievable with third-party video upscalers
- Multiple generations recommended to pick the best take

---

## Access and Pricing

- **Gemini AI Pro** offers a free 1-month trial that includes Flow access
- Free trial includes 1,000 credits
- Veo 3 Fast mode: 20 credits per generation (720p, includes audio)
- Quality mode: higher credit cost, higher resolution, also includes audio
- V2 is available but does NOT generate audio -- always use V3

---

## Example Use Cases Shown

1. **Tesla ad** -- showroom-style CGI product reveal
2. **Apple Watch ad** -- uses logo and realistic product rendering (no reference images needed, purely from JSON text description)
3. **Pepsi ad** -- Super Bowl-caliber commercial aesthetic
4. **Dior perfume ad** -- flower scents visualized with cinematic flair
5. **Uber Eats ad** -- comedic voiceover with food delivery visuals (by creator "Mentor")

All created with text-only JSON prompts (no image inputs required), though image inputs are supported for custom products.

---

## Key Takeaways for Scribario

1. **JSON prompting is the standard** for high-quality Veo 3 output. Freeform text produces noticeably inferior results.
2. **LLM-generated JSON prompts** are the workflow -- you don't hand-write them. Feed examples + instructions to ChatGPT/Claude, describe what you want, get a perfect JSON prompt.
3. **Audio is built-in** with Veo 3 (not V2). JSON prompts can include dialogue, voiceover, and sound design direction.
4. **Brand-specific ads** are achievable by describing products in the prompt -- the model can render recognizable products (Tesla, Apple Watch, Pepsi) from text alone.
5. **The 720p/fast mode + upscale workflow** is the cost-efficient path for high volume generation.
6. **No reference images required** for known brands/products, but custom products benefit from image attachment in the prompt generation step.

---

## What This Video Does NOT Cover

- Exact JSON schema/field names (the video shows JSON on screen but doesn't walk through individual fields)
- Character consistency across multiple clips
- Multi-shot/multi-scene sequencing
- Specific camera movement field syntax
- Audio-specific JSON fields in detail
- Negative prompting or constraint fields

These gaps would need to be filled from the actual JSON prompt examples (the video creator offers 10 prompts via Google Docs link) or from other sources.
