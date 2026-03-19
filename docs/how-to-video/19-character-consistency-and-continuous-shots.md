# 19 - Character Consistency and Continuous Shots in Veo

Extracted from three YouTube tutorials. This is the most critical reference for Scribario's video pipeline.

**Sources:**
- [6iBc4aoiwf4] "How to Create Single Continuous Shots with Veo in Google Flow" (AI Video School, 16 min)
- [RK-989PgFk4] "How to Make Consistent Characters in Veo 3" (AI Video School, 8 min)
- [i_KlptBTdck] "How to Create Long AI Animation Videos with Consistent Characters | VEO 3.1 + Google Flow" (18 min)

---

## Table of Contents

1. [Character Consistency Techniques](#1-character-consistency-techniques)
2. [Continuous Shot Methods](#2-continuous-shot-methods)
3. [First-Frame / Last-Frame Technique](#3-first-frame--last-frame-technique)
4. [Scene Extension (Extend vs Jump To)](#4-scene-extension-extend-vs-jump-to)
5. [Reference Image Usage](#5-reference-image-usage)
6. [Character Drift and Degradation](#6-character-drift-and-degradation)
7. [Prompt Patterns and Templates](#7-prompt-patterns-and-templates)
8. [Google Flow Specific Techniques](#8-google-flow-specific-techniques)
9. [Multi-Clip Assembly Workflow](#9-multi-clip-assembly-workflow)
10. [What Fails and How to Avoid It](#10-what-fails-and-how-to-avoid-it)
11. [Veo 3.1 Edit/Insert Feature](#11-veo-31-editinsert-feature)
12. [Voice and Audio Consistency](#12-voice-and-audio-consistency)
13. [Caption/Subtitle Removal](#13-captionsubtitle-removal)
14. [Implications for Scribario API Pipeline](#14-implications-for-scribario-api-pipeline)

---

## 1. Character Consistency Techniques

### The Core Method: Detailed Character Description Template

The single most important technique for character consistency across clips is building an extremely detailed, reusable character description and including it verbatim in every prompt.

**Step-by-step process (from [RK-989PgFk4]):**

1. **Generate a reference image** of your character (Whisk, Midjourney, or any image gen tool).
2. **Use Whisk's "Subject" feature** to analyze the image. Drag the image into the Subject slot -- Whisk's AI will generate a detailed description of what it sees. This is how the "Google AI universe" perceives the character.
3. **Take the Whisk description + your original prompt to Gemini.** Attach the reference photo and say: *"Here's a prompt I wrote in Whisk [paste prompt]. Here is the image description I received for this image [paste Whisk description]. I would like a detailed Veo 3 description of just the man/woman that I can use in a template for building prompts where I try to place them in a consistent looking way. Don't worry about wardrobe -- just focus on the face."*
4. **Gemini returns a canonical character description.** This becomes your reusable template.
5. **Also generate a voice description.** Ask Gemini: *"What would his/her name be, and how would you write a voice prompt for them in Veo 3?"* Gemini returns both a name and a voice description (e.g., "slightly raspy and gravelly, tinged with thoughtful curiosity").
6. **Build a three-part prompt template:**
   - **Character physical description** (face only, not wardrobe -- wardrobe changes per scene)
   - **Voice description** (consistent across all clips)
   - **Cinematic style template** (e.g., "shot in 35mm, high-end documentary style")

**Key insight:** You are NOT using the image as a character reference (Veo 3 does not support character reference images as of this tutorial). Instead, you are converting the image into extremely detailed TEXT that Veo can interpret consistently.

### Why This Works

Veo 3 does not have a character reference feature like Runway. The only way to maintain consistency is through the TEXT PROMPT. The more detailed and specific the character description, the more consistent the output.

The description should focus on **immutable facial features**: bone structure, eye shape, nose shape, skin tone, hair texture, jawline. NOT clothing (which changes per scene).

---

## 2. Continuous Shot Methods

There are **two distinct methods** for creating continuous shots, each with different tradeoffs:

### Method A: Extend (in Google Flow Scene Builder)

- Start with a Veo 3 clip, add it to Scene Builder
- Click the **+** button, then **Extend**
- Enter a prompt describing "what should happen next"
- The system takes the last frame of the current clip and generates a continuation
- **Limitation:** As of the tutorial, extending only works with **Veo 2 fast mode**, NOT Veo 3 fast. The extend feature is not supported in V3 fast mode -- you must switch to V2.
- **UPDATE (from [i_KlptBTdck]):** Veo 3.1 now supports extending in Flow with both quality and fast modes.
- V2 extension loses audio (no sound generation in V2)
- Result: seamless visual continuity within Flow, but requires post-production audio work

### Method B: Last Frame / First Frame (Frames-to-Video)

- Generate first clip in Veo 3 quality mode
- In Scene Builder, scrub to near the end of the clip
- Click **"Save frame as asset"** to capture that frame
- Go to **Frames to Video**, use the saved frame as the **Start Frame** only (leave End Frame empty)
- Write your continuation prompt and generate in Veo 3 quality mode
- Repeat: save last frame of new clip, use as start frame for next clip
- **This method works with Veo 3 quality mode** (100 credits per clip)
- Preserves audio generation capability since each clip is native Veo 3

### Which Method to Use

| Factor | Extend (Method A) | Last Frame/First Frame (Method B) |
|--------|-------------------|-----------------------------------|
| Audio | Lost (V2 has no audio) | Preserved (each clip is V3) |
| Visual continuity | Very smooth | Good but degrades over time |
| Character consistency | High (same context) | Degrades each generation |
| Credits per 8s clip | 4 (V2 fast) | 100 (V3 quality) or 20 (V3 fast) |
| Control over dialogue | None after first clip | Full control each clip |
| Best for | Silent/music videos | Dialogue-driven videos |

---

## 3. First-Frame / Last-Frame Technique

### Detailed Procedure

1. **Generate Clip 1** using Frames-to-Video with your Midjourney/reference image as the Start Frame
2. **In Scene Builder**, scrub to the frame you want to use (NOT necessarily the very last frame -- see below)
3. Click **"Save frame as asset"**
4. **Go back to the main text-to-video area**, click **Frames to Video**
5. Upload or select the saved frame as the **Start Frame**
6. **Only use a Start Frame** -- leave End Frame empty for continuous shots (you want the video to flow wherever it goes)
7. Write your continuation prompt
8. Select **V3 quality** mode (100 credits) for best results
9. Generate, review, repeat

### Critical Detail: Don't Always Use the Literal Last Frame

> "Sometimes the last frame is blurry. Like if you'll see around her eyes, they're a little bit blurry. If you go back a few frames, they're not quite as blurry. Because this is a little bit higher quality, we're going to use this as the last frame instead."

**Rule:** Scrub back a few frames from the end to find the **sharpest, clearest frame**. The last frame is often in motion blur. Using a blurry frame compounds quality degradation.

> "I know what you're thinking -- it's not all going to blend together. But I noticed when I did last frame first frame with the actual last frame, I still had to trim up the clips in a video editing program. It wasn't a seamless single clip. I had to download each individual clip and trim them up. And since I have to do that anyway, I may as well try and find the best clip that I can."

**Key takeaway:** Last-frame/first-frame is NEVER truly seamless. You ALWAYS need to trim in post-production. So pick the best quality frame, not the mathematically last one.

### Frame Selection Tips

- **Choose frames where the subject is looking at camera** -- this helps maintain facial consistency
- **Choose frames with clear, sharp facial features** -- avoid motion blur
- **Choose frames where the subject appears to be in motion** -- if the last frame looks "still," the next generation may think the character is standing still and break the walking motion
- Scrub back 0.25-0.5 seconds from the end for best results

---

## 4. Scene Extension (Extend vs Jump To)

### Extend

- **What it does:** Takes the last frame of the selected clip and generates a seamless continuation
- **Use when:** You want the same continuous scene to keep going (same location, same action, same character)
- **Prompt format:** Describe what should happen NEXT -- the system already has the visual context from the last frame
- **Example prompt:** "Camera tracking motion as the conductor walks down the aisle revealing more passengers. The passengers are all anthropomorphic animals. She smiles in amusement."

### Jump To

- **What it does:** Takes a frame from the current clip and generates a SEPARATE clip that "jumps to" a new scene
- **Use when:** You want a scene change while still maintaining some visual connection
- **How it works:** "It's going to take the frame from where you selected and then create another video, jump to that video, instead of extending the clip you selected."

### Scene Changes Within Flow

When you want a completely different scene with a different character:
1. Switch to **Frames to Video** mode
2. Upload a new reference image for the new scene
3. Generate the new scene clip
4. Add it to Flow
5. Extend from there for that scene
6. Repeat for each scene change

> "If you want another scene, you use frames to video, generate a video, and then extend that, extend that until you get to what you want."

---

## 5. Reference Image Usage

### Image-to-Video (Frames to Video)

- **Start Frame:** Sets the opening visual. The generated video starts from this image.
- **End Frame (Last Frame):** Sets where the video should end up. For continuous shots, leave this EMPTY -- you want the video to flow naturally.
- **Both frames:** Creates a video that transitions from start to end. Useful for specific scene transitions but NOT for continuous shots.

### How to Get Good Reference Images

1. **Midjourney** -- generates high-detail reference images
2. **Whisk** (Google tool) -- generates images AND provides detailed AI descriptions of what it sees
3. **Any image generator** -- the key is getting a clear, detailed face shot

### Using Reference Images Across Multiple Clips

The reference image is only used for the FIRST clip. After that, you're using saved frames from previous generations. This is why degradation happens -- each generation is one step further from the original reference.

### Veo 3.1 First Frame + Last Frame for Clip-Level Control

From [i_KlptBTdck], for a second intro video, the creator used first frame and last frame (without Google Flow) in the normal Veo 3.1 interface:
- Generated the first part of a video using first frame + last frame
- For a standing/talking shot, used a first frame from the video
- For a close-up shot, used a close-up frame as the first frame
- This gives per-clip control over framing and camera angle

---

## 6. Character Drift and Degradation

### The VHS Tape Analogy

> "It's like when you used to do VHS tapes -- every time you make a copy, every copy is worse than the version that came before it."

Each generation introduces drift:
- **Generation 1:** Matches the reference image well
- **Generation 2:** Slight changes (different ear shape, slightly different nose)
- **Generation 3-4:** Noticeable changes (different piercings, different eye color)
- **Generation 5+:** "A completely different person"

### What Changes During Drift

From the tutorial, observed drift includes:
- Hair color/style changes
- Facial structure changes (especially around eyes and nose)
- Skin tone shifts
- Added/removed accessories (piercings appearing)
- Age perception changes
- Eye color changes
- Clothing style shifts (even when not described)

### How to Minimize Drift

1. **Use the detailed character description in EVERY prompt** (most important)
2. **Pick the highest quality frame** for next generation (not the blurry last frame)
3. **Use V3 quality mode** instead of fast -- quality mode maintains more detail from the reference frame
4. **Keep clips shorter when possible** -- fewer seconds = less drift within each clip
5. **Trim aggressively** -- cut to the best frames before using as reference for next clip
6. **Accept some drift** as inevitable -- plan your edit around it

### Drift Rate Comparison

| Mode | Drift Rate | Notes |
|------|-----------|-------|
| V2 fast extend | Low within extend, but no audio | Best visual continuity |
| V3 fast (frames-to-video) | High | Noticeably different after 2-3 clips |
| V3 quality (frames-to-video) | Moderate | "Definitely a lot better than fast mode" |
| V3.1 extend in Flow | Low | Best option as of latest update |

---

## 7. Prompt Patterns and Templates

### Character Description Template (from [RK-989PgFk4])

Structure your prompt in three blocks:

```
[PHYSICAL DESCRIPTION]
A man in his mid-50s with deep-set brown eyes, a weathered face with prominent
laugh lines, salt-and-pepper stubble, a strong jawline, olive-toned skin,
thick dark eyebrows, and slightly receding dark hair with gray at the temples.

[VOICE DESCRIPTION]
He speaks with a slightly raspy and gravelly voice, tinged with thoughtful
curiosity. His cadence is measured and deliberate.

[SCENE + DIALOGUE]
High-end documentary style, shot on 35mm film. Interior interview setup,
natural lighting. He looks slightly off-camera and says: "I used to wake up
and worry about all of the things I needed to do that day."
```

### Extension Prompt Template (from [6iBc4aoiwf4])

For extend prompts in Scene Builder, describe:
1. **Camera movement** (tracking, panning, etc.)
2. **Character action** (walks, turns, gestures)
3. **What's revealed** (new elements entering frame)
4. **Character reaction** (smiles, looks surprised)

Example: *"Camera tracking motion as the conductor walks down the aisle revealing more passengers. The passengers are all ballerinas. The conductor waves to one ballerina."*

### Frames-to-Video Continuation Prompt (from [6iBc4aoiwf4])

```
Motion tracking shot of the woman walking. She says [dialogue here].
[Optional: emotional descriptors like "regretfully", "with a smile"]
[Optional: new visual elements appearing in scene]
```

### Animation-Style Prompt Structure (from [i_KlptBTdck])

For animated/stylized content, structure prompts with explicit timing:

```
Aesthetic style: Pixel-style 3D animation
Visual look: Golden hour sunlight
Color palette: Bright blue coat, orange sunlight, metallic silver gadget
Camera direction: [describe camera movement]

0-2 seconds: [character says/does X]
3-4 seconds: [character says/does Y]
5-8 seconds: [character says/does Z]
```

**Important caveat:** Veo 3 / 3.1 will NOT strictly follow timestamp directions. The creator acknowledges: *"I know V3 is not going to stick with this. V3.1 will not stick with this."* But adding them helps structure the overall pacing.

### Extension Prompt for Flow (from [i_KlptBTdck])

When extending in Flow, include:
- What the character SAYS (voice/dialogue)
- What the character DOES (gestures, movements)
- What appears in the scene (objects, backgrounds)

Example: *"Voice: The boy says 'It now supports high quality video with audio in flow.' He gestures to the holographic screen behind him showing waveforms and clips playing together seamlessly."*

---

## 8. Google Flow Specific Techniques

### Scene Builder Overview

- **Access:** From any generated video, click "Add to Scene" to enter Scene Builder (also called Google Flow)
- **Purpose:** Arrange, extend, trim, and assemble multiple clips into a long video
- **All clips generated in Scene Builder** also appear in the main project library

### Flow Operations

| Operation | How | When to Use |
|-----------|-----|-------------|
| **Add to Scene** | Click "Add to Scene" on any generated clip | Starting a new sequence |
| **Extend** | Click + button, select "Extend" | Continue the current scene |
| **Jump To** | Click + button, select "Jump To" | Scene change with visual connection |
| **Save Frame as Asset** | Click + button, select "Save frame as asset" | Capture a frame for frames-to-video |
| **Trim** | Drag clip edges | Remove unwanted start/end frames |
| **Delete** | Click trash icon, select clip | Remove a bad clip from sequence |
| **Download** | Click download button | Export final assembled video |

### Trimming in Flow

Trimming is critical for quality:
- **Trim the end of clips** to remove blurry/degraded final frames
- **Trim the start of clips** to remove the "settling" effect where a new generation adjusts to the reference frame
- **Trim to fix pacing:** If a clip has awkward pauses or the speech was cut off, trim to the usable portion

> "What I can do is to trim it -- I can reduce it from here and then reduce this part of the video. Trim it back a bit so that it will just blend in."

### Model Selection in Flow

- **V2 fast:** Required for the Extend feature (as of earlier tutorial)
- **V3 quality:** Works with Frames-to-Video in Flow (100 credits)
- **V3 fast:** Works for Frames-to-Video but lower quality (20 credits)
- **V3.1 quality:** Now available in Flow for extending (latest update)
- **V3.1 fast:** Also available in Flow

> "In Google Flow, remember before you couldn't use 3.1 in Google Flow, but now you can use 3.1 quality or fast. I'm still using the quality version. I've noticed that quality gives better videos, especially when you're using frames to video."

### Downloading from Flow

- Click download button to get the assembled video
- **The output is NOT perfect** -- you still need to take it to a video editor (CapCut, Premiere Pro) for:
  - Proper trimming of clip boundaries
  - Adding sound effects and background music
  - Fixing any audio/visual glitches at transition points

---

## 9. Multi-Clip Assembly Workflow

### Complete Workflow: Dialogue-Driven Long Video

**Phase 1: Character Setup**
1. Generate reference image (Midjourney/Whisk/any tool)
2. Run through Whisk Subject analysis to get AI description
3. Use Gemini to create canonical character description + voice template
4. Write your script/dialogue broken into 8-second chunks

**Phase 2: First Clip Generation**
1. Go to Frames-to-Video in Veo 3
2. Upload reference image as Start Frame
3. Write prompt with character description + first dialogue + scene setting
4. Generate in quality mode
5. Review and iterate until satisfied
6. Click "Add to Scene"

**Phase 3: Extension Loop**
1. In Scene Builder, click + on last clip
2. Choose Extend (if same scene continues) or prepare a new Frames-to-Video (if scene change)
3. For Extend: describe what happens next + dialogue
4. For new scene: save frame as asset, go to Frames-to-Video, upload frame, write new prompt
5. Generate, review, trim
6. Repeat until video is complete

**Phase 4: Post-Production**
1. Download assembled video from Flow
2. Import into video editor (CapCut recommended)
3. Trim clip boundaries for smooth transitions
4. Remove any unwanted captions/subtitles (see section 13)
5. Add background music, sound effects
6. Color grade for consistency across clips
7. Export final video

### Workflow for Faceless/Narrated Channel Content (from [i_KlptBTdck])

> "If you're trying to create a long video, more like a faceless channel type of video where someone is speaking -- this is the best way to use it. You generate the first part and then you continue, you generate the next. What you just have to change would probably be the speech -- that will be the only thing to change."

This is the simplest workflow:
1. Generate first clip with full scene description + dialogue
2. Extend repeatedly, changing only the dialogue/speech each time
3. The character and scene stay consistent because extend inherits context
4. Download and edit in CapCut

---

## 10. What Fails and How to Avoid It

### FAILURE: Character Stops Moving When Extended

**What happens:** You extend a clip of a walking character, and in the new clip they just stand still.

**Why:** The last frame of the previous clip looked like the character was standing still (captured at a moment where motion wasn't apparent).

**Fix:** Trim the previous clip back to a frame where the character clearly appears to be in motion, then extend from there.

> "The trick there was that the final frame looked too much like she was just standing there and it didn't know that she was in motion."

### FAILURE: Wrong Character Speaks the Dialogue

**What happens:** You write dialogue for Character A, but Character B says it.

**Why:** Veo doesn't always correctly assign dialogue to the intended character, especially in multi-character scenes.

**Fix:** Regenerate. Sometimes it takes multiple attempts to get the right character speaking.

### FAILURE: Unwanted Subtitles/Captions Appear

**What happens:** Veo 3 burns subtitles into the video.

**Why:** This is a known Veo 3 behavior, especially when dialogue is included in the prompt.

**Attempted fixes that DON'T reliably work:**
- Generating via Gemini instead of Flow (inconsistent)
- Adding "no subtitles" to the prompt (doesn't work)
- Removing quotation marks from dialogue (helps slightly but not reliably)

**Fixes that DO work:**
- Runway inpainting (brush over captions, AI removes them -- slight artifacts)
- CapCut AI Remove (better results -- select captions with quick brush, remove)
- See section 13 for details

### FAILURE: Progressive Character Degradation

**What happens:** After 3-5 generations using last-frame/first-frame, the character looks completely different.

**Why:** Each generation introduces small changes that compound. Like photocopying a photocopy.

**Mitigation:**
- Use V3 quality mode (slower degradation than fast)
- Use the Extend method instead of last-frame/first-frame when possible
- Pick the sharpest frame (not the literal last frame) for references
- Include the full character description in every prompt
- Keep the video shorter or plan fewer generations

### FAILURE: Speech Gets Cut Off

**What happens:** The dialogue you wrote is too long for the 8-second clip, so it gets truncated.

**Why:** Each Veo clip is approximately 8 seconds. If your dialogue is longer than what can be spoken in 8 seconds, it gets cut.

> "If you notice, it cut the speech actually because the speech was actually too long. If you're trying to generate a video, just ensure that your speech is not too long or else it's going to cut it down. You just have 8 seconds to use."

**Fix:** Keep dialogue per clip to what can comfortably be spoken in 6-7 seconds (leave buffer). Break longer speeches across multiple clips.

### FAILURE: Camera Does Unexpected Things

**What happens:** Instead of continuing the scene smoothly, the camera suddenly pans up, zooms in, or changes angle unexpectedly.

**Why:** Veo has its own "creative" interpretation of prompts. When you ask for an action that requires a scene change (like exiting a train), it may interpret the camera movement differently than intended.

**Fix:** Sometimes the unexpected result is actually usable -- adapt your creative vision. Otherwise, regenerate with more explicit camera direction. The creator found that an unexpected camera pan upward actually provided a good transition to an exterior shot.

### FAILURE: Accent/Voice Inconsistency

**What happens:** When a character is described with a specific ethnicity (e.g., "Armenian farmer"), Veo generates inconsistent accents across clips.

**Why:** Veo interprets ethnicity as implying an accent, and the accent varies between generations.

**Fix:** Clone the best voice sample using ElevenLabs (only 10 seconds needed), then replace inconsistent audio in post-production. See section 12.

### FAILURE: Extend Feature Not Available in V3

**What happens:** You try to extend a V3 clip and get an error.

**Why:** As of the earlier tutorial, extend only works with V2 in Flow. V3.1 has since added extend support.

**Fix:** Either use V2 fast for extending (lose audio) or use the last-frame/first-frame method with V3 quality.

---

## 11. Veo 3.1 Edit/Insert Feature

From [i_KlptBTdck], Veo 3.1 introduced an in-place edit feature:

1. Generate a video
2. Click the **Edit** button
3. **Draw a bounding box** on the area where you want to insert/change something
4. Write a prompt for what should appear in that box
5. Generate -- the AI inserts the described object/character into that region

**Example:** Adding a Chihuahua dog to a scene by drawing a box on the floor area and prompting "a small Chihuahua dog walking."

**Use cases:**
- Add props or objects to an existing scene
- Insert additional characters
- Modify a specific region without regenerating the whole clip

This is useful for Scribario because it allows post-generation refinement without starting over.

---

## 12. Voice and Audio Consistency

### The Problem

Veo 3 generates audio with each clip, but:
- Accents vary between generations
- Voice timbre can shift
- Background audio changes

### The Solution: ElevenLabs Voice Cloning

1. Find the best voice clips from your Veo 3 generations
2. Combine them to get **10 seconds of audio** (minimum for ElevenLabs cloning)
3. Export just the audio
4. Upload to ElevenLabs to create a cloned voice
5. Two approaches:
   - **Voice changer:** Run all generated audio through the clone to normalize accent/timbre
   - **Text-to-speech:** Type in the dialogue and generate with the cloned voice, then drop into the video in post

> "Having a consistent voice as well as a consistent face really helps sell it."

### Voice Changer Limitations

The voice changer doesn't always remove accents perfectly. For clips where the accent was too strong, the creator switched to text-to-speech with the cloned voice and matched timing manually.

---

## 13. Caption/Subtitle Removal

### The Problem

Veo 3 frequently burns subtitles into the generated video when dialogue is in the prompt.

### Methods to Remove

**Method 1: Runway Inpainting**
- Use brush tool to paint over captions
- AI removes them and fills in the background
- Slight visual artifacts visible if you look closely
- Acceptable for most uses

**Method 2: CapCut AI Remove (RECOMMENDED)**
- Import video into CapCut
- Select the clip, go to Video > AI Remove
- Use the Quick Brush to select caption area
- Click Remove
- Results are very clean, even over complex backgrounds

> "I think the CapCut one worked terrific."

### Prevention Tips

- Avoid quotation marks in dialogue prompts (slight improvement)
- "No subtitles" in the prompt does NOT work reliably
- Generating via Gemini instead of Flow is inconsistent
- Best approach: plan to remove them in post-production

---

## 14. Implications for Scribario API Pipeline

### What We Can Automate

Based on these tutorials, here's what maps to Scribario's programmatic pipeline:

**Character Consistency:**
- **Automate the character description generation** -- use Claude to analyze a reference image and generate a canonical character description template (replaces the Whisk + Gemini manual process)
- **Store the character template** in the brand profile / content request
- **Inject the character template** into every video prompt automatically
- **Store voice description** separately for audio consistency

**Clip Generation:**
- **Use Veo API's frames-to-video** with start frame for continuity
- **Break scripts into 6-7 second dialogue chunks** automatically
- **Generate each clip with full character description + dialogue chunk + scene description**

**Assembly:**
- **Save the last frame (or near-last frame) programmatically** from each generated clip
- **Feed that frame as the start frame** for the next clip
- **Implement quality scoring** -- if a frame is too blurry, scrub back a few frames
- **The extend API** (if available) would be preferable for same-scene continuity

**Post-Production:**
- **Trim clip boundaries** programmatically (remove first/last 0.25-0.5 seconds)
- **Detect and remove burnt-in captions** (could use video inpainting API)
- **Stitch clips** with crossfade transitions to hide seams
- **Add consistent background music** under dialogue

### Key Constraints for Pipeline Design

1. **8-second clip limit** -- all dialogue must fit in ~7 seconds per clip
2. **Character drift is inevitable** -- plan for 4-6 clips max before significant drift
3. **Quality mode is worth the cost** for character consistency
4. **Every clip needs the full character description** -- don't abbreviate
5. **Frame selection for continuity matters** -- pick sharp frames, not blurry last frames
6. **Post-production is NOT optional** -- raw output always needs trimming and cleanup
7. **Extend is better than last-frame/first-frame** for continuity within a scene
8. **Scene changes should use new reference images** fed through frames-to-video

### Credit/Cost Implications

| Operation | Credits | Notes |
|-----------|---------|-------|
| V3 quality clip (8s) | 100 | Best for character consistency |
| V3 fast clip (8s) | 20 | 5x cheaper but more drift |
| V3.1 quality in Flow | 100 | Best overall option |
| V3.1 fast in Flow | 20 | Good for iteration/testing |
| V2 fast extend | 4 | Cheapest but no audio |

For a 1-minute video (7-8 clips): 140-800 credits depending on mode.

### Recommended Pipeline Strategy

1. **First clip:** V3.1 quality with reference image as start frame (100 credits)
2. **Subsequent clips (same scene):** Extend in V3.1 quality (100 credits each)
3. **Scene changes:** New reference image via frames-to-video in V3.1 quality
4. **Iterate/test:** Use V3.1 fast (20 credits) for testing prompts, then regenerate winners in quality
5. **Always include:** Full character description + voice description + scene description + dialogue (under 7 seconds)
6. **Always post-process:** Trim, remove captions, add music, color match
