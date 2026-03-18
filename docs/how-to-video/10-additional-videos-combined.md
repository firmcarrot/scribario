# Combined Lessons: AI Video Generation (9 Videos)

Sources:
1. **afzbZYC6fCM** — "How To Use Google VEO 3 JSON Prompting To Create $100k AI Ads"
2. **rBPy7C7W03E** — "Master The Ultimate Google Veo 3.1 Prompt Formula (Full Tutorial)"
3. **PL_izvWJVLU** — "STOP Wasting Credits & Become a VEO 3 Master in 8 Minutes"
4. **KWH46O99oLE** — "Timeline Prompting in Sora 2 is CRAZY for Cinematic AI Videos"
5. **LgoJoMAdNC8** — "Google Veo 3.1 is INSANE - Full Tutorial"
6. **IjF5Uun2jrM** — "Google Veo 3 Tutorial: Make Cinematic AI Videos with Just a Prompt"
7. **4N_TfYVNM7k** — "Claude Code is Taking Video Editor Jobs Now (Remotion Skills)"
8. **0rMMWOWVBo0** — "This is How I Automated Viral AI Videos for FREE (n8n + Veo 3)"
9. **YpuSE9hcal8** — "Build your own AI MOVIES shot by shot - FREE & LOCAL!"

---

## 1. Prompt Structure and Formulas

### The 5-Part Prompt Formula (Google-Recommended)
Every prompt should contain these five ingredients in order:
1. **Shot composition / cinematography** — camera angle, position, movement (e.g., "slow continuous handheld tracking shot at shoulder level with shallow depth of field")
2. **Subject** — detailed description of the main character or focal point (age, clothing, expression, physical details)
3. **Action** — what the subject is doing, how they're moving
4. **Context / setting** — environment, background, time of day, weather
5. **Style / ambiance** — overall aesthetic, mood, lighting, color grade

*Source: rBPy7C7W03E*

### The 10-Component Deep Prompt (Credit-Saving Version)
For maximum control, include all 10:
1. Scene description (what's happening)
2. Subject (who, what they look like)
3. Background (what's behind them)
4. Action (what the subject does)
5. Style (horror cinematic, comedy, documentary, etc.)
6. Camera settings (lens, angle, movement)
7. Composition (framing, depth of field)
8. Lighting and mood (golden hour, cold blue, heavy shadows)
9. Audio (dialogue in quotes, ambient sounds, music)
10. Color palette (teal and orange, warm amber, etc.)

**Bonus: Negative instructions** — tell the model what NOT to generate. This prevents random/unwanted elements from appearing. Most people overlook this.

*Source: PL_izvWJVLU*

### JSON Prompting
JSON-formatted prompts are not magic — they're just a structured way to organize the same information. They work well for:
- Product unboxing / room transformation videos
- Brand advertisements
- Multi-element scenes with specific timing

Use a ChatGPT custom bot to generate JSON prompts from simple ideas (e.g., "Give me a JSON VO3 prompt of a box opening room transformation in Tom and Jerry style"). The bot fills in camera, lighting, room, elements, and sequence details.

*Source: afzbZYC6fCM*

### Timeline Prompting (Sora 2)
Assign specific actions to specific time codes within the video:
- **0-3s (Hook):** tight profile close-up, slow dolly, wind hissing, metal shimmer
- **3-6s (Context):** focus shifts to parchment map, camera tilts down, fingers trace route
- **6-9s (Climax):** over-the-shoulder medium shot, action sequence
- **9-12s (Resolution):** wide shot, character marches into scene

Start with **style** (e.g., "gritty medieval cinematic realism"), then **camera** (e.g., "50mm to 85mm prime lens, slow dolly"), then each timed segment.

Image-to-video gives more control than text-to-video because the AI extracts style, character, and objects from the reference image.

*Source: KWH46O99oLE*

---

## 2. Camera Control Tips

### Specific Camera Language That Works
- "Slow continuous handheld tracking shot at shoulder level" — rBPy7C7W03E
- "Fast, shaky, close quarters dolly in on the subject's face" — rBPy7C7W03E
- "Cinematic close-up with slow dolly-in on his weathered face" — LgoJoMAdNC8
- "Wide shot and slowly zooms in toward the headphone" — LgoJoMAdNC8
- "Fast 180-degree orbit around the headphones, motion blur subtle" — LgoJoMAdNC8
- "Drone captured from directly above" — LgoJoMAdNC8
- "Medium shot with a fast, shaky, close quarters dolly in" — rBPy7C7W03E
- "Static VHS recorder with handheld shakiness, zoom glitches, interlaced flicker" — KWH46O99oLE

### Timed Camera Instructions in Prompts
You can embed time-based camera directions directly in the prompt:
- "At 2 seconds, the camera begins with a wide shot and slowly zooms in..."
- "At 3 seconds, the camera transitions into a fast, fluid 180-degree orbit..."
- "Finally, the camera pulls back, zooms out gracefully..."

This is not perfect yet but VEO 3.1 understands these transitions reasonably well.

*Source: LgoJoMAdNC8*

### Describing Position Instead of Movement (for ComfyUI/Local)
When using Gwen Image Edit for shot-by-shot generation, **describe where things are in space** rather than camera movements:
- "Half the photo is obstructed by the man's back. The large window is to the right. Behind the woman to the left is a bar."
- This works better than "rotate the camera to show an over-the-shoulder shot"

*Source: YpuSE9hcal8*

---

## 3. Audio and SFX Direction

### Audio Prompts Are Essential
Adding audio descriptions dramatically improves video impact. Without them, your video loses half its immersion.

**Ambient SFX examples:**
- "Audio: the creak of the boat, rhythmic thud of waves, wet slap of the net" — rBPy7C7W03E
- "Audio: ocean waves crashing, wind. No background music." — LgoJoMAdNC8
- "Subtle ambient hum, plus light whoosh sounds" — LgoJoMAdNC8

**ASMR / Product sounds:**
- "Clear, crisp ASMR light click of the headset immediately followed by an energetic bass-heavy electronic beat drop" — rBPy7C7W03E

**Dialogue / Narration:**
- Include spoken text in quotes within the prompt: `He says, "The ocean teaches you respect one wave at a time."` — LgoJoMAdNC8, IjF5Uun2jrM
- VEO 3 automatically matches voice to character appearance (older characters get deeper/gravelly voices) — LgoJoMAdNC8
- VEO 3.1 has noticeably richer, more detailed audio than 3.0 — LgoJoMAdNC8

**Narration trick:** Put narration text in quotes at the end of the prompt, preceded by "Narration:" — IjF5Uun2jrM

*Sources: rBPy7C7W03E, LgoJoMAdNC8, IjF5Uun2jrM*

---

## 4. Character Consistency Methods

### Reference Image Approach (Gwen Image Edit + ComfyUI)
The most robust method for multi-shot character consistency:
1. Upload reference images of your characters (up to 3)
2. Upload a reference image of your environment/location
3. The Gwen Image Edit model composites characters into the scene
4. The "Next Scene LoRA" by Lovis93 takes the previous output and generates the next shot while preserving character likeness

**Key details:**
- No LoRA training needed for character consistency — just reference images
- Works with any style: realistic, anime, claymation
- Name your characters in the workflow (e.g., "Tina") to keep organized
- Re-connect the original character reference image periodically to "remind" the model what the character looks like (prevents drift)

*Source: YpuSE9hcal8*

### Reference Sheet Technique
Create a combined reference sheet containing:
- 360-degree environment image
- Both character reference images
- Connect this sheet to every generation step

This helps the model understand spatial relationships (e.g., "bar is to the left, window is to the right") and keeps characters more consistent because you're constantly reminding the model.

*Source: YpuSE9hcal8*

### VEO 3.1 Elements Feature
Upload up to 3 different images (character, object, scene) and VEO 3.1 builds a video incorporating all of them. Generate your reference images first using an image model (e.g., OpenArt Photorealistic, Cadream 4), then upload them as "elements."

*Source: LgoJoMAdNC8*

### Start/End Frame for Product Consistency
Upload a product image as start frame and a modified version (different angle/background) as end frame. VEO 3.1 interpolates between them, keeping the product perfectly consistent throughout.

*Source: LgoJoMAdNC8*

---

## 5. Multi-Clip Workflow Patterns

### Chain-of-Frames Method (VEO 3.1)
1. Generate clip 1 with start frame
2. Swap end frame to become the new start frame
3. Import a new end frame for clip 2
4. Generate clip 2 — transition is seamless because clip 2 starts where clip 1 ended
5. Repeat for unlimited-length videos with perfect continuity

*Source: LgoJoMAdNC8*

### Shot-by-Shot ComfyUI Workflow (Free + Local)
1. **Setup:** Load character references + environment reference into ComfyUI workflow
2. **Scene 1:** Generate establishing shot with all references
3. **Scene 2+:** Use "Next Scene LoRA" — feed previous output as input, write prompt describing the new camera angle/action
4. **Background consistency:** Generate a 360-degree panoramic environment image, then crop relevant sections as background references for each new angle
5. **Pose control:** Optionally upload pose reference images for specific character positions
6. **Video generation:** Feed completed still frames into an image-to-video model (Kling v3, or locally with Mochi 2.2) with start frame + end frame

**Copy groups to create new scenes** — duplicate the generation group, change input references and prompt, run again.

*Source: YpuSE9hcal8*

### Automated Pipeline (n8n + Vertex AI)
Full automation from idea to finished video:
1. **Trigger:** Schedule (daily) or manual
2. **Ideas Agent:** Gemini generates video ideas in structured JSON
3. **Store ideas:** Append to Google Sheet
4. **Prompts Agent:** Second AI agent converts ideas into detailed VEO 3 prompts
5. **Generate video:** HTTP request to Google Vertex AI (VEO 3 model)
6. **Wait node:** ~60 seconds for VEO to render
7. **Fetch video:** Second HTTP request to retrieve base64-encoded video
8. **Decode:** Convert base64 to MP4
9. **Upload:** Save to Google Drive
10. **Log:** Update Google Sheet with shareable Drive link

Access VEO 3 for free via Google Cloud Platform ($300 free credits for 90 days). Use Vertex AI > Media Studio > Generate Video.

*Source: 0rMMWOWVBo0*

### Remotion + Claude Code (Programmatic Video)
Claude Code generates React components that render individual frames, assembled into video:
1. Install Remotion skills globally in Claude Code
2. Create a blank Remotion project (`npx create-video@latest`)
3. Run `npm i && npm run dev` to spawn local video editor in browser
4. Prompt Claude Code: "Create a 20-second video about X"
5. Claude generates code for each scene/slide with transitions, text effects, and assets
6. Edit by referencing specific scenes: "In scene 3, the text boxes are overlapping. Fix that."
7. Ask Claude to self-critique: "If you were an expert motion graphics designer, what improvements would you make?"
8. Render and download MP4

**Best practice:** Use plan mode first — let Claude think through the video structure before coding. Then let it execute. Verify it used all Remotion skills.

*Source: 4N_TfYVNM7k*

---

## 6. Failure Modes and Fixes

### Vague Prompts = Wasted Credits
"Hey, box unboxing explosion" produces garbage. You need structured, detailed prompts with specific camera, lighting, action, and style descriptions. Short prompts that work for ChatGPT do NOT work for video models.

*Source: afzbZYC6fCM, PL_izvWJVLU*

### Fast Mode Is a Trap
VEO 3 "fast mode" (cheaper credits) produces noticeably worse results:
- Movements become slower, more blunt, less natural
- Not significantly faster generation time
- Better to use a different model entirely (e.g., Kling) than VEO 3 fast mode

*Source: PL_izvWJVLU*

### Low-Quality Input Images Degrade Output
Image-to-video quality depends heavily on input image quality. Low-res or blurry starting images produce proportionally worse video. Always use the highest quality image possible as your starting frame.

*Source: PL_izvWJVLU*

### Resolution Limitation (1080p) — Upscale After
VEO 3 outputs at 1080p max, which can look soft for higher-production work. Fix: use OpenArt's video upscale feature to go to 4K after generation. Also increase FPS during upscale for smoother motion.

*Source: PL_izvWJVLU*

### Character Drift in Multi-Shot Sequences
When generating multiple shots, characters gradually change appearance. Fix: periodically re-connect the original character reference image to remind the model.

*Source: YpuSE9hcal8*

### Camera Rotation Failures (ComfyUI)
Prompting "rotate the camera" often fails with Gwen Image Edit. Instead, describe the final composition spatially: "Half the frame is the man's back. Window is to the right. Bar is to the left."

*Source: YpuSE9hcal8*

### Background Inconsistency Across Angles
Changing camera angles often produces inconsistent backgrounds. Fix: generate a 360-degree panoramic image of the environment, then crop relevant sections as background references for each new angle. A custom LoRA trained on 20 real 360-degree images helps the model understand panoramic geometry.

*Source: YpuSE9hcal8*

### Sora 2 Censorship
Sora 2 has aggressive content filters that can block fantasy/action scenes (e.g., a dragon getting hit by a fireball). VEO 3 is less restrictive for creative content.

*Source: KWH46O99oLE*

### Results Are Non-Deterministic
Re-generating the same prompt produces completely different results every time. You cannot exactly replicate a specific output. Expect 3-5 generations to get something you like, especially for complex scenes.

*Sources: afzbZYC6fCM, KWH46O99oLE*

### Remotion First Pass Is Never Perfect
The first Claude Code / Remotion output is a rough draft. The real value is in iterative editing — reference specific scenes and frames for targeted fixes rather than regenerating everything.

*Source: 4N_TfYVNM7k*

---

## 7. Example Prompts (Copy-Paste Ready)

### Cinematic Portrait (VEO 3.1)
```
A weathered sea captain with a thick gray beard and blue knitted hat stands at a ship's railing gesturing towards stormy ocean waves. Cinematic close-up with slow dolly-in on his weathered face. Golden hour lighting with dramatic shadows. He says, "The ocean teaches you respect one wave at a time." Audio: ocean waves crashing, wind. No background music. Color palette: deep blues, warm amber, weathered browns. No subtitles.
```
*Source: LgoJoMAdNC8*

### Tech Ad (VEO 3.1)
```
A young woman in her 20s with expressive wide eyes and a slight confident grin pulls a sleek futuristic augmented reality headset down over her eyes with a purposeful practiced motion. Medium shot with a fast, shaky, close quarters dolly in on the subject's face. A busy colorful cafe filled with diffused natural light and the soft chatter of other patrons. Style: modern social media/tech ad. Shallow depth of field. Clean, vibrant color grading. Audio: clear, crisp ASMR light click of the headset immediately followed by an energetic bass-heavy electronic beat drop.
```
*Source: rBPy7C7W03E*

### Product Ad with Start/End Frame (VEO 3.1)
```
A premium silver-white over-ear headphone set with mesh cushion ear cups and polished aluminum finish perched on a minimalist white stand in a bright white studio. At 2 seconds, the camera begins with a wide shot and slowly zooms in toward the headphone, emphasizing the texture of the ear cushions and metal sheen under soft studio lighting. At around 3 seconds, the camera transitions into a fast, fluid 180-degree orbit around the headphone. Motion blur subtle, capturing reflections as the stand and background begin to fade. Finally, the camera pulls back, zooms out gracefully, revealing the full silhouette of the floating headphone in the center of the black background. Style: ultra minimalist, Apple commercial aesthetic, shallow depth of field, high-end product cinematography, clean reflections. No subtitles. Subtle ambient hum plus light whoosh sounds.
```
*Source: LgoJoMAdNC8*

### Horror VHS Style (Sora 2 Timeline Prompt)
```
Style: Horror VHS realism, eerie analog aesthetic.
Camera: Static VHS recorder with handheld shakiness, zoom glitches, interlaced flicker, tracking errors.
Scene: Dark suburban street at night, deserted, single streetlight buzzing.
0-3s: Close-up of VHS recorder screen, static and distortion.
3-6s: Handheld view from behind man walking down empty street.
6-9s: Medium shot, man stops, tape begins glitching heavily.
9-12s: Video heavily distorts, alien figure appears directly in front of camera.
```
*Source: KWH46O99oLE*

### Simple Cookie Video (VEO 3 via Gemini)
```
A cinematic slow motion shot of freshly baked chocolate chip cookies being pulled out of the oven in a cozy sunlit kitchen. Warm lighting, shallow focus on the cookies, steam rising gently. Soft instrumental background music.
```
*Source: IjF5Uun2jrM*

---

## 8. Unique Insights

### Use Gemini to Write Your VEO Prompts
Since VEO 3 lives inside Gemini, you can ask Gemini itself to help craft prompts: "Can you help me write a cinematic video prompt about X?" It will include camera angles, lighting, pacing, and music suggestions.

*Source: IjF5Uun2jrM*

### Use ChatGPT Templates for Prompt Expansion
Paste a prompt template into ChatGPT with a bracket for your simple idea. ChatGPT expands "a street interview with a chimp" into a full 10-component prompt with scene, subject, background, action, style, camera, composition, lighting, audio, and color palette.

*Source: PL_izvWJVLU*

### Nano Banana for End Frame Manipulation
Use Nano Banana (image editing model in OpenArt) to modify your start frame into an end frame: "Change the product environment to a solid black background and turn the headphones around." This gives you a matching pair of frames for seamless start-to-end transitions.

*Source: LgoJoMAdNC8*

### Claude Code + Remotion: The "Expert Critique" Loop
After first-pass video generation, ask Claude: "If you were an expert motion graphics artist or designer, what improvements would you make?" It generates ~10 suggestions. Cherry-pick the ones that make sense and have Claude implement them. This produces significantly better output than iterating blindly.

*Source: 4N_TfYVNM7k*

### Free VEO 3 Access via Vertex AI
Google Cloud Platform gives $300 in free credits for 90 days. Access VEO 3 through Vertex AI > Media Studio > Generate Video. This is cheaper than OpenArt or other third-party wrappers.

*Source: 0rMMWOWVBo0*

### 360-Degree Environment Images for Spatial Consistency
Generate a panoramic 360-degree image of your scene environment. When changing camera angles in multi-shot sequences, crop the relevant section of the panorama as a background reference. This teaches the image model the full spatial geometry, producing consistent backgrounds from any angle.

Custom LoRA needed: train on ~20 real 360-degree images to teach the model proper panoramic format.

*Source: YpuSE9hcal8*

### GGUF Compression for Local Models
If running locally on limited VRAM (16GB), use GGUF-compressed versions of Gwen Image Edit. Q5 version fits comfortably on 16GB VRAM. Q8 for 24GB+.

*Source: YpuSE9hcal8*

### Image Lightning LoRA for Speed
The "Image Lightning 4-Step LoRA" reduces Gwen Image Edit inference from ~20 steps to 4 steps (set CFG to 1.0). Dramatically speeds up shot-by-shot generation without significant quality loss.

*Source: YpuSE9hcal8*

### Modular Story Structure
Build stories as swappable modules: same shot sequence, different characters or locations. Change one reference image at the start and the entire workflow regenerates with the new character/location. This allows rapid iteration on concepts.

*Source: YpuSE9hcal8*

---

## 9. Tool Comparison Summary

| Tool | Best For | Cost | Key Limitation |
|------|----------|------|----------------|
| **VEO 3 / 3.1** (via Gemini/Flow) | Single-clip cinematic video, dialogue, audio | Paid Google plan ($20/mo) | 8s max per clip, 1080p |
| **VEO 3** (via Vertex AI) | API access, automation | Free $300 credits | No GUI, HTTP requests only |
| **VEO 3** (via OpenArt) | Multi-model access, upscaling, image gen | Credits-based | More expensive per generation |
| **Sora 2 / Pro** (via ArtList) | Timeline prompting, longer clips (12s) | ArtList subscription | Heavy censorship, expensive Pro tier |
| **Remotion + Claude Code** | Motion graphics, slides, data-driven video | Claude subscription | Not photorealistic, code-based only |
| **ComfyUI + Gwen Image Edit** | Shot-by-shot character-consistent stills | Free (local GPU) | Requires 16GB+ VRAM, manual workflow |
| **Mochi 2.2 / Kling v3** | Local image-to-video from generated stills | Free (local) / API | Quality below VEO 3 |
| **n8n + Vertex AI** | Automated batch video generation | Free (self-hosted n8n) | Requires GCP setup, no real-time editing |
