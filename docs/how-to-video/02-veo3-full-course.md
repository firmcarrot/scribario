# VEO 3 Full Course — Practical Reference

**Source:** "Create Cinematic Ai Videos with Google VEO 3 (FULL COURSE)"
**URL:** https://youtube.com/watch?v=1lktT4dVAT4
**Duration:** ~31 minutes
**Creator:** AI filmmaking practitioner (unnamed in transcript)

---

## 1. Camera Control

### What Works

- **Crane shots:** "slow crane shot behind a cloaked figure walking up the steps" — camera flies above and tilts down to reveal. Works well.
- **Tilt up reveal:** "close-up shot on a gloved finger hovering over a blaster, then the camera quickly tilts up to reveal a bounty hunter with a helmet." One of the creator's favorite generations. The fast tilt from detail to full subject is very effective.
- **Pan up from feet:** "start from the feet of stormtroopers marching through a town and then pan up to reveal the body and helmets." Works.
- **Camera pull back:** "camera pulls back while the Jedi walks forward and waves her white lightsaber." Works with text-to-video prompts.
- **Orbit/circle:** "camera circles around the subject." Decent control when described in the text prompt.
- **Tilt down:** "camera tilts down while this hunter jumps down from the ledge." Works.
- **Pan + tilt combo:** "camera pans left and tilts up to reveal a giant AT-AT vehicle." Works in text-to-video (not in image-to-video).

### What Fails

- **Too much action + camera movement in one prompt:** Asking for a droid making beeping noises AND THEN panning to a Jedi character — "too much going on inside this prompt for it to animate properly." Voice gets mixed up, dialogue garbled.
- **Subject descriptions override camera angles:** If you prompt for "over-the-shoulder shot of a rebel pilot," VEO 3 wants to SHOW the rebel pilot (face/body) first, then switches to over-the-shoulder. The subject description fights the camera instruction.
- **Fix for subject vs. camera conflict:** Remove the named subject. Instead of "over-the-shoulder shot of a rebel pilot in a cockpit," use "over-the-shoulder shot inside a cockpit of a spaceship." Removing "rebel pilot" lets VEO 3 prioritize the camera angle. This gives a perfect over-the-shoulder for the entire clip.

### Key Principle

VEO 3 prioritizes showing named subjects over following camera instructions. If camera angle matters more than showing a specific character, describe the SCENE and ANGLE without naming a character subject.

---

## 2. Character Consistency Across Clips

### How to Achieve It

- Write a **detailed, specific character description** covering: skin color/texture, facial features (tattoos, patterns, scars), hairstyle, clothing materials and colors, accessories.
- **Reuse the exact same description** across every prompt for that character.
- The more specific you are, the more consistent the results.

### Example — Sith Lord Description

> "He's tall, lean, pale white ashy skin with dark veins on his gaunt face. Gray hair tied in a bun. Wears a raggedy black cloak with sharp edge plating on the shoulders."

This produced highly consistent results across multiple generations. The main variance was the shoulder pad details (plates vs. needles) — removing "sharp edge plating" from the prompt would have eliminated that inconsistency.

### Example — Female Jedi Description

> Green skin, geometric tattoos across her face, yellow lightsaber, lightweight brown and gold robe.

Adding clothing details and specific environment helped consistency. Worked across multiple scene contexts.

### What Varies

- Accessories and small details (shoulder pads, ornamental features) vary the most between generations.
- **Fix:** Remove ambiguous accessory descriptions, or simplify them. Keep the core appearance details (skin, face, hair, main clothing).

### Multi-Character Scenes

- Copy BOTH full character descriptions into a single prompt.
- Assign each character specific dialogue.
- Example: Full Jedi description + full Sith description + "The Sith says: [line]. The Jedi says: [line]."
- Works for dialogue scenes. Lightsaber battles start slow but ramp up with sparks and effects.

---

## 3. Audio / SFX / Voice Prompting

### What VEO 3 Does Automatically

- Generates sound effects matched to the scene: lightsaber hums, footsteps, environmental sounds.
- Generates character voices matched to character appearance (older weathered man = deeper grittier voice; young woman = different tone).
- Lip sync quality is high — hand motions, facial expressions, and speech coordinate well.

### What You CAN Control

- **Specific dialogue:** Put exact words in quotes in the prompt. The character will say those words.
  - Example: `She says, "The force doesn't scream, it hums. Listen and you'll know which path is open."`
- **General emotional direction in voice:** Can ask for screaming, yelling — partially works. Got a scream at the end, but timing was off (word said at beginning, scream at end).

### What You CANNOT Control

- **Voice timbre/character:** Prompting for "high-pitched and nasal voice" or "stuffy nose" does NOT work. VEO 3 determines voice purely from the character's visual appearance. You cannot override this via prompt.
- **Specific sound effects:** "You don't actually have that much control over what specific sound effects are generated."
- **Expressive delivery timing:** Asking for a character to "yell NO with exaggerated facial expression" — the yell and the word "no" happened at different times, mouth didn't match.

### Workaround for Voice Control

Use an external voice generator (e.g., ElevenLabs) + lip sync tool (e.g., Pix) to:
1. Generate video in VEO 3 without dialogue
2. Generate voice separately in ElevenLabs
3. Apply lip sync in a third tool
Not ideal, but it's the current workaround.

---

## 4. Lighting & Visual Techniques

### Describing the Visual Aesthetic Is Critical

A prompt that just describes character + action produces bland, flat-looking video. You MUST describe the visual look of the shot.

### Before/After Example

**Bad prompt (bland result):**
> "An Asian female Jedi from Star Wars. She has two small ram horns on her head and is wearing a white sleeveless dress with gold ornaments. She sits on a circular jade throne in an Asian Palace. She stands up, pulls out a green lightsaber. She says 'May the force be with you.'"

**Good prompt (cinematic result):**
> "An Asian female Jedi from Star Wars. She's wearing a white sleeveless dress with gold ornaments. She sits on a glowing dark jade throne inside a dark Asian palace. She stands up and pulls out a green lightsaber. Muted dark colors, high contrast between the dark green jade throne and the darker palace with intricate Asian designs and dragon statues behind the Jedi."

The difference is "enormous."

### Key Lighting/Color Phrases That Work

- "Muted dark colors"
- "High contrast between [light element] and [dark element]"
- "Glowing dark jade" (self-illuminating materials)
- "Bioluminescent plants" (for alien/swamp scenes)
- "Red lightning inside a thunderstorm"
- "Bright sunlit rocky environment"
- "Dark orange dust"
- "Cinematic film" (append this as a style tag)

### Material/Texture Descriptions

- Default VEO 3 tends toward clean, chrome, shiny surfaces.
- Explicitly describe textures: "rusty, made out of old metal scraps, with plants growing on the side" turned a chrome speeder into something that fit a Star Wars world.
- Think about what textures and materials belong in the world you're creating.

---

## 5. Common Failure Modes and Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| Video looks like PowerPoint slides | Using older Veo 2 model (Fast/Quality settings) | Select "Highest quality with experimental audio" in settings — that's the actual VEO 3 model |
| Character walks wrong direction (down stairs instead of up) | Inherent randomness in generation | Re-run the same prompt. Second try may nail it |
| Camera shows character's face/body before switching to requested angle | Named subject in prompt overrides camera instruction | Remove the named subject; describe scene/angle without naming a character |
| Complex action scene is incoherent (Sith does 360 flip, bounty hunter appears from nowhere) | Too many actions + characters + camera moves in one prompt | Break into smaller clips. Generate each action beat separately |
| Dialogue garbled or words out of order | Too much happening in prompt alongside dialogue | Simplify the scene. Fewer simultaneous actions = better dialogue |
| Bland/flat video with no cinematic feel | Prompt describes character and action but not visual aesthetic | Add color palette, lighting, contrast, environment details to prompt |
| Voice doesn't match character | VEO 3 determines voice from appearance, ignores voice descriptions | Can't fix in VEO 3. Use external voice + lip sync tools |
| Sound effects don't match or are missing | Limited SFX control in prompts | Add SFX in post-production |
| Upscaler gets stuck | Known platform bug | Download original size, upscale externally if needed |
| Image-to-video generates unwanted subtitles on screen | Bug when prompting talking characters from reference images | Known issue. No fix currently in VEO 3 |
| Image-to-video uses Veo 2 instead of Veo 3 | Camera motion presets and image-to-video features only work with older model | Use text-to-video for VEO 3 quality; describe the scene in text instead |

---

## 6. Prompt Structure & Length

### Recommended Prompt Structure

1. **Camera angle/movement** (put first or prominently if camera control matters)
2. **Character description** (appearance, clothing, features — be very specific for consistency)
3. **Action/movement** (what happens in the scene)
4. **Dialogue** (in quotes, with attribution: `She says, "..."`)
5. **Environment/setting** (location, time of day, weather)
6. **Visual style** (colors, contrast, lighting, textures)
7. **Style tag** (end with "cinematic film" or similar)

### Length Guidelines

- Short prompts (1-2 sentences) work for simple scenes but produce generic results.
- Detailed prompts (5-8 sentences) with specific visual descriptions produce much better cinematic output.
- **Too long/complex** prompts with multiple characters + actions + camera moves + dialogue = quality degrades. The model can't handle everything at once.
- Sweet spot: One character, one action, one camera move, specific visual details.

### Magic Words/Phrases

- "Cinematic film" — improves overall visual quality when appended
- "Muted colors" — prevents oversaturated/cartoony output
- Specific material descriptions > generic ones ("rusty old metal scraps" > "metal")

---

## 7. Multi-Clip Storytelling

### Core Principle

Dynamic scenes with multiple beats do NOT work well in a single 8-second clip. Break your story into separate clips, each with one clear action.

### Example — Force Push Scene

**Single clip (failed):** Sith reaches out with palm, says words, sends bounty hunter flying. Result: Sith does a 360 flip, bounty hunter appears from nowhere. Incoherent.

**Multi-clip approach (worked):**
- Clip 1: Sith reaches out with palm and says "This will be the last time you fail me"
- Clip 2: Bounty hunter getting thrown (separate generation)

### Extend Feature (Google Flow)

- "Add to scene" lets you extend a video with a new prompt continuing the action.
- Limited to Veo 2 quality (lower than VEO 3).
- Quality drops in the extension compared to the original clip.
- Works okay for continuation but not great for complex narrative.

### Jump To Feature

- Supposed to generate a different camera angle of the same scene.
- "Hit or miss" — sometimes it just extends the video instead of changing angle.
- Sometimes works: bounty hunter blaster-to-helmet shot successfully jumped to him walking away from spaceship.

### Realistic Expectations

- A 1.5-hour AI film requires a full team: sound design, voice actors, cinematographers, editors.
- VEO 3 alone cannot produce feature-length content.
- It's a tool for generating individual cinematic clips, not a complete filmmaking solution.

---

## 8. Specific Example Prompts From the Video

### Female Jedi — Talking Scene
> A female Jedi from Star Wars with green skin, geometric tattoos across her face, yellow lightsaber, wearing a lightweight brown and gold robe. She is meditating inside a quiet swamp illuminated by bioluminescent plants on an alien world. She says, "The force doesn't scream, it hums. Listen and you'll know which path is open."

### Sith Lord — Consistent Character
> [Tall, lean Sith with] pale white ashy skin and dark veins on his gaunt face. Gray hair tied in a bun. Wears a raggedy black cloak with sharp edge plating on the shoulders.

### Crane Shot — Sith Temple
> Slow crane shot behind a cloaked figure walking up the steps to an ancient Sith temple in Star Wars. The camera flies above and slowly tilts down to reveal the Sith temple. Red lightning inside a thunderstorm.

### Tilt Up Reveal — Bounty Hunter
> Close-up shot on a gloved finger hovering over a blaster. The camera quickly tilts up to reveal a bounty hunter with a helmet.

### Over-the-Shoulder (Fixed Version)
> Over-the-shoulder shot inside a cockpit of a spaceship. [Looking out the window at fighter jets flying by.]

(Note: "rebel pilot" was intentionally removed to preserve camera angle.)

### Dynamic Jump — Text-to-Video (Better Than Image-to-Video)
> Front view of a bounty hunter from Star Wars. He's wearing a rusty helmet and rusty armor. The camera tilts down as he jumps down from a tall ledge into a rock pit and lands on the ground. Bright sunlit rocky environment with brown rocks and some sand.

### Cinematic Throne Scene (Improved Version)
> An Asian female Jedi from Star Wars. She's wearing a white sleeveless dress with gold ornaments. She sits on a glowing dark jade throne inside a dark Asian palace. She stands up and pulls out a green lightsaber. Muted dark colors, high contrast between the dark green jade throne and the darker palace with intricate Asian designs and dragon statues behind the Jedi.

### AT-AT Reveal — Pan + Tilt
> A close-up shot on a female Jedi from Star Wars with a white lightsaber on a dusty battlefield. The camera pans left and tilts up to reveal a giant AT-AT vehicle from Star Wars. Dark orange dust and color tones.

### Ingredients-to-Video — Multi-Character
> The woman with blue skin and the man with red skin walk together on a rocky landscape. Muted colors. Cinematic film.

---

## 9. Platform-Specific Notes (Google Flow)

- VEO 3 is accessed through **Google Flow** (Google's filmmaking platform).
- Three modes: **Text-to-video**, **Frames-to-video** (image reference), **Ingredients-to-video** (multiple reference images).
- In settings: select **"Highest quality with experimental audio"** — this is the actual VEO 3 model. "Fast" and "Quality" options use older Veo 2.
- Set outputs to 1 per prompt to iterate faster.
- Videos are **8 seconds** long.
- Download options: GIF, original size, or upscaled HD (upscaler is buggy).
- **Image-to-video features (camera motion presets, ingredients) force you to Veo 2** — you lose VEO 3 quality and sound effects.
- Image-to-video cannot generate talking characters with actual speech (only mouth movement, no voice).
- Pricing: $125/month, going up to $250/month after 3 months.

---

## 10. Text-to-Video vs. Image-to-Video — Decision Matrix

| Factor | Text-to-Video | Image-to-Video |
|--------|--------------|----------------|
| Model quality | VEO 3 (best) | Veo 2 (older) |
| Sound effects | Yes, auto-generated | No |
| Talking characters | Yes, with lip sync | Mouth moves but no actual speech |
| Camera control | Via prompt (good) | Via presets (smooth but limited to Veo 2) |
| Character accuracy | Depends on description skill | Matches reference image |
| Motion dynamism | More dynamic, better action | More subtle, less dynamic |
| Creative flexibility | Higher | Lower (constrained by starting image) |
| Best for | Most scenes, action, dialogue | Specific character look that's hard to describe in text |

**Creator's recommendation:** Use text-to-video whenever possible. Only use image-to-video when you need a character look you absolutely cannot describe in text (e.g., Jar Jar Binks).
