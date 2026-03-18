# VEO 3.1: Storytelling, Character Consistency & Ad Creation

**Source:** "Master Google VEO 3.1 - AI Video Generation, Storytelling & Ad Creation Guide" by GenHQ (Raw Keith)
**URL:** https://youtube.com/watch?v=O8-vsMM8hSI
**Duration:** ~20 minutes

---

## 1. Key VEO 3.1 Features (vs VEO 3)

- **Ingredients feature:** Upload up to 3 reference images and combine them into a single video (character + location + object)
- **First and last frame:** Now integrated into VEO 3.1 — set a start frame and end frame, AI connects the dots between them
- **Audio/sound design on first-last frame:** VEO 3.1's advantage over competitors like Kling 2.1 — you get generated audio even on first/last frame videos
- **Multi-shot mode:** Splits your prompt into scenes and adds camera cuts automatically (available on Higgsfield platform)
- **Voice quality improved:** VEO 3 had "really tiny voice outputs" — VEO 3.1 is significantly better
- **Prompt coherence improved:** Significantly better than VEO 3

---

## 2. Platform Recommendation: Higgsfield

- Recommended for VEO 3.1 access because of unlimited generations during first week of release
- Also offers unlimited image generation
- Has both Frames (first/last frame) and Ingredients features in their UI
- Multi-shot mode is a Higgsfield-specific feature — auto-rewrites your prompt into timed scene structure
- Has built-in prompt enhancer on backend

---

## 3. Image Quality for Video Input (Critical)

**Problem:** Uploading low-quality images to VEO 3.1 produces poor video output. VEO 3 smoothed out skin and adjusted coloring, making output look obviously AI-generated.

**Rules:**
- Always upload crisp, high-resolution images (4K if possible)
- Upscale images before uploading if they are low-res
- More detail in the source image = more detail for the video model to "attach to"
- Low-res images (e.g., 1000x1000 from Nano Banana) will produce poor results
- **Recommended image model for quality:** Cadream (produces 4K crisp imagery)
- **For products with text:** Nano Banana is better at preserving text on products

---

## 4. Character Consistency Technique (360 Spin Method)

This is the "expert level tip" from the video:

1. **Generate a character** using an image model (e.g., Cadream, Higgsfield Soul)
2. **Generate a full-body shot** of that character on a white background (upload the face/bust image and prompt for full body)
3. **Upload that full-body image** to a video model (e.g., Kling 2.5) and prompt: "The character spins on a full 360. So we see all angles of the character. He moves around in a full rotation."
4. **Use a 10-second generation** for the spin
5. **Pause the video at any point** and screenshot — you now have reference images from every angle (side profile, back, three-quarter, etc.)
6. **Use those screenshots as reference images** in future generations for consistent character across scenes

This gives you a "full 360-degree render" of your character that you can use as reference for any scene.

---

## 5. Ingredients Feature Workflow (3-Image Composition)

**Concept:** Combine character + location + object into one video.

**Step-by-step:**
1. Generate or source your **character image** (full body preferred)
2. Generate or source your **location image** (e.g., interior of a car at nighttime)
3. Generate or source your **object image** (e.g., an iPhone, a product)
4. Upload all 3 as "ingredients" in VEO 3.1
5. Write a prompt describing how they combine

**Example prompt used in video:**
> "The character who has the TV as the head is sat inside the car and he is driving the car. He has one hand on the wheel and he's holding an iPhone up to his ear and he is talking. As he is talking, the light on the TV monitor flickers to visually represent each time he's talking. And he's in a heated debate with his girlfriend on the phone. In the background, we can hear his girlfriend talking on the phone and then he's replying to his girlfriend and he's getting frustrated."

**Note:** Aspect ratio of ingredient images does not matter — the model handles it.

---

## 6. Multi-Shot Mode (Automatic Scene Splitting)

When enabled, the platform rewrites your prompt into a timed multi-scene structure.

**Example:** A simple prompt about a mechanic got rewritten into:
> - 0-2 seconds: medium shot of a man leaning over the hood of the Land Rover [details]
> - 2-3 seconds: quick cut to a closeup of his face
> - 3-5 seconds: slow zoom on his face
> - 5-7 seconds: medium shot, pulls back out
> - 7-8 seconds: final shot lingers on the Land Rover badge on the engine cover

**Result:** 5 shots in an 8-second sequence. In practice, it produced 3 distinct shots.

**Alternative without multi-shot:** You can manually write camera cut instructions in your prompt, e.g., "the camera cuts to a side profile of the character talking on the phone" — VEO 3.1 will generate that cut mid-video.

**Warning:** Multi-shot prompt enhancer sometimes adds things you don't want. Turn it off if you need precise control.

---

## 7. First & Last Frame for Product Ads

**Workflow for product transition videos:**

1. **Generate product images** in different compositions/angles using an image model
   - Example: Kellogg's cereal box — one close-up, one with orange particles swirling around it on dark background
2. **Upload Image A as first frame, Image B as last frame** in VEO 3.1's Frames option
3. **Write a transition prompt** describing what happens between the two frames

**Example prompt:**
> "The cereal is floating in the air, and the camera slowly moves around the box. The box slants ever so slightly as it's floating in the air and orange particles start to circle around the box showcasing a cool product transition shot."

**Critical settings for first/last frame:**
- **Turn OFF enhance** (prompt enhancer) — otherwise it will change your prompt
- **Turn OFF multi-shot** — same reason, you want exact control

**LLM-assisted prompting:** Upload both first and last frame images to an LLM (Claude, Gemini, ChatGPT) and ask:
> "Write me a simple first and last frame transition shot between the close-up image of the cereal box to the last frame which has the orange particles swirling around it. In between these two frames, I would like to have the product floating in the air. I would like these orange particles to circle around the box, creating a very cool transition. Can you write me a prompt that's optimized for Google VEO 3.1?"

---

## 8. 1080p Upscaling Warning

- VEO 3.1 offers 1080p output, but it's just upscaling from 720p internally
- **Upscaling can negatively impact quality** — washes out detail, especially skin
- Creates a "plasticky look" on human subjects
- **Recommendation:** Use 720p native if quality matters, especially for human/realistic content; upscale externally with a dedicated tool if needed

---

## 9. Content Safety / Moderation Gotchas

- **Swear words in dialogue prompts get blocked.** Example: "Damn, this is a hard day's work" caused a generation error. Removing "damn" fixed it.
- **Safety-aware actions blocked:** VEO 3.1 refused to generate someone on the phone while driving (safety concern)
- These are hard blocks — not quality issues. You must rework the prompt.

---

## 10. Audio/Sound Direction in Prompts

- You can describe audio/dialogue directly in VEO 3.1 prompts (e.g., "he says 'this is a hard day's work'")
- You can direct background audio (e.g., "in the background, we can hear his girlfriend talking on the phone")
- VEO 3.1 generates both video AND audio from the prompt
- Voice generation is significantly improved over VEO 3

---

## 11. Prompt Architecture Summary

**For storytelling/cinematic content:**
- Describe the scene visually
- Include camera directions (medium shot, closeup, slow zoom, pulls back)
- Include dialogue in quotes
- Include sound/audio descriptions
- Use time stamps for multi-shot sequences (0-2s, 2-3s, etc.)

**For product ads:**
- Use first/last frame with two carefully composed product images
- Describe the transition motion (floating, rotating, particles)
- Turn OFF enhance and multi-shot for precise control
- Use an LLM to optimize your transition prompt

**For character consistency:**
- Generate character on white background
- Do a 360-spin video to get all angles
- Screenshot reference angles from that video
- Use those as ingredients in future scenes

---

## 12. Tool/Model Recommendations from Video

| Task | Recommended Tool |
|------|-----------------|
| Character/scene images (quality) | Cadream (4K output) |
| Product images with text | Nano Banana |
| Quick character concepts | Higgsfield Soul |
| 360 spin video for references | Kling 2.5 |
| Final video generation | Google VEO 3.1 (via Higgsfield) |
| Prompt optimization | Any LLM (Claude, Gemini, ChatGPT) |
