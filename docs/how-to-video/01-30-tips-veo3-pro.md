# 30 Tips To Create Mindblowing Videos With Google VEO 3

**Source:** [YouTube - 30 Tips To Create Mindblowing Videos With Google VEO 3 (Become a Pro)](https://youtube.com/watch?v=fvV95J0LiOE)
**Duration:** ~36 minutes
**Extracted:** 2026-03-15

---

## 1. Camera Control

### Camera Shots (framing)
- **Close-up shot** -- focuses on face/detail. Use: `close-up shot on her face`
- **Full body shot** -- shows entire character body
- **Side profile shot** -- camera perpendicular to subject. Use: `side profile shot`
- **Extreme long shot** -- camera pulled way back, shows full environment + tiny character
- **Bird's eye view / overhead shot** -- looking straight down, gives objective environmental view

### Camera Angles (vertical position)
- **Low angle shot** -- camera below looking up. Makes character look bigger, stronger, more powerful
- **High angle shot** -- camera above looking down. Makes character look smaller, weaker
- **First-person POV shot** -- immersive, viewer is the character. Use: `first-person POV shot`

### Camera Movements
- **Tilt up** -- camera tilts upward to reveal something above. Example: `camera tilts up from female character to reveal an eagle flying in the sky`
- **Pan** -- horizontal camera movement. Example: `camera pans from the female character and shows an abandoned monastery far in the distance`
- **Zoom in** -- moves closer during scene. Example: `camera zooms in on her face during the battle`
- **Pull back / dolly out** -- starts close, reveals wider scene. Example: `close-up shot on character's face, then camera pulls back to reveal her riding on a horse`
- **Crane shot** -- elevated sweeping movement. Example: `slow crane shot behind the female character, walking up the steps of an ancient castle, then camera flies above and slowly tilts down to reveal the entire castle`

### Camera Movement Gotcha
- Too much camera motion in a single prompt causes jump cuts instead of smooth movement. Veo3 may swap abruptly between a wide fight scene and a face close-up instead of smoothly zooming in.

### Camera Lens / Device Types
- **Fisheye lens** -- ultra-wide, distorted spherical look
- **Macro lens** -- extreme close-up of small subjects with fine detail
- **Infrared camera** -- infrared visual style
- **Sony camera** -- adding "shot on a Sony camera" gives cinematic photorealistic look
- **Selfie stick / extended arm** -- vlog-style framing. Use: `self camera angle shot from an extended arm` or `holding up a vlog cam on a selfie stick`
- **Vlog camera** -- wider angle. Use: `shot from a vlog camera` for full wide-angle perspective

### Frame Interpolation (first + last frame)
- Upload a first frame image AND a last frame image to "frames to video"
- Prompt describes the transition (e.g., `the camera pulls back`)
- Veo3 generates a video interpolating between the two frames
- Great for controlling exact camera movement between two compositions
- **Limitation:** Only works with older Veo2 model -- no sound effects generated

---

## 2. Character Consistency Across Clips

### Method 1: Text-only (Tip 11) -- BEST for dialogue
- Write an extremely detailed character description: skin color, hair style/color, clothing, accessories, weapons
- Paste the EXACT SAME description into every new prompt, only changing the scene description below it
- **Example character block:** "A female warrior with pale skin and long white braided hair braided into two thick plaits that hang over her shoulders. She wears a dark red cloak with loose white trousers and strap leather gear around her waist. She carries a short straight sword."
- **Pro:** Character can talk (Veo3 dialogue works with text-to-video)
- **Con:** Inconsistencies between clips -- clothing not exact, facial structure varies slightly, hair may flip shoulders

### Method 2: Green Screen Hack (Tip 12) -- credit: Martin Nebolon
- Generate an image of your character on a GREEN SCREEN background
- Upload to "frames to video"
- Start prompt with: `Instantly jump/cut to on frame one`
- Then describe the scene: `she walks next to a huge white direwolf in an icy landscape, it is snowing`
- First frame shows character + green screen, then cuts to the new scene
- **Pro:** Very consistent character appearance
- **Con:** Quality slightly lower, extra-high contrast issues. NO dialogue generation (reference image mode can't generate speech)

### Method 3: Ingredients to Video (Tip 13) -- WORST option
- Upload multiple images (character, other character, landscape) as "ingredients"
- Forces fallback to older Veo2 model
- Results are mediocre -- characters may swap mid-scene
- No AI-generated sound effects
- **Verdict:** Not recommended

### Method 4: Image-to-Video with Flux Context (Tip 14) -- BEST for visual consistency
- Step 1: Generate a base image of your character
- Step 2: Upload that image to **Flux Context Max** (available on OpenArt.ai, chat-to-edit feature)
- Step 3: Ask the AI to create new images of the same character in different scenes/angles: "Create an image of this female character in a medieval tavern. Her appearance should stay the same. Cinematic film shot on a Sony camera."
- Step 4: Upload each generated image to Veo3 "frames to video" and animate with a simple prompt
- **Pro:** Best visual consistency (face, clothing, accessories all match closely)
- **Con:** No dialogue generation when using reference images

### Adding Dialogue to Image-Based Characters (Tip 15)
- Veo3 CANNOT generate dialogue when using a reference image
- **Workaround:** Use external lip-sync tool (e.g., Ddesign.ai lip sync feature)
- Upload the Veo3 video + a separate audio file
- Result is passable but not ideal -- lip sync quality is imperfect

### Consistent Objects/Products (Tip 16)
- Same Flux Context workflow works for products, objects, and locations
- Upload product image, ask AI to place it in new contexts while maintaining design details
- Then animate in Veo3 via frames-to-video

---

## 3. Audio / SFX Prompting

### Ambient Sounds (Tip 6)
- Explicitly describe ambient sounds in your prompt
- Examples that work:
  - `sound of waves at the beach`
  - `sound of a creek running by`
  - `sounds of wind rustling and cars honking in the background`
- Adds immersion. Veo3 generates these natively with text-to-video.

### Background Music (Tip 7)
- Prompt for specific music moods: `suspenseful and thrilling music`, `relaxed piano playing in the background`
- Be specific about instruments: `a guqin playing in the background` (traditional Chinese instrument) -- Veo3 can handle obscure instruments
- Music generation only works with text-to-video (Veo3 model), NOT with reference images or features that fall back to Veo2

### Sound Limitations
- Reference image mode (frames to video, ingredients to video) falls back to Veo2 -- NO AI-generated sound
- Fast mode -- no dialogue generation
- Video extension feature -- falls back to Veo2, no sound effects; you must add audio manually

---

## 4. Lighting Techniques (Tip 27)

### Light Sources
- **Soft sunlight:** `soft sunlight beaming through the trees`
- **Moonlight:** `harsher moonlight casting down` -- night scenes
- **Firelight:** `light shining on him from a fire`

### Color Grading / Palettes
- **Cool blue tones** -- cold, dreary, melancholic feeling
- **Warm tones** -- softer, more approachable
- **Desaturated colors** -- gritty war-film look (Saving Private Ryan style)
- **Monochromatic** -- single color shade (e.g., all green = uneasy, unnatural feeling)
- **Light pastel tones** -- soft pinks and blues, colorful and gentle

### Photorealism Fix (Tip 20)
- Fantasy/historical characters often render as 3D video-game style instead of photorealistic
- **Fix:** Add `muted colors, cinematic film` to the prompt
- This steers the model toward photorealistic faces and textures
- Does NOT work 100% of the time -- some prompts stubbornly render as video-game style; in those cases, change the prompt entirely

---

## 5. Common Failure Modes and Fixes

### Unwanted Subtitles (Tip 3)
- Veo3 frequently burns subtitles/captions into the bottom of generated videos
- **What does NOT work reliably:**
  - Removing quotation marks from dialogue in the prompt
  - Adding "no subtitles" to the prompt
  - None of the commonly suggested prompt tricks work consistently
- **Actual fixes:**
  - Crop out the subtitle area in a video editor (zoom in, hide bottom)
  - Use an AI subtitle remover tool (e.g., **V-Make** video subtitle remover -- free version previews 5 seconds, paid removes full video)

### Accents Not Working (Tip 4)
- Simply writing "Hispanic accent" or "Brazilian accent" in the prompt does NOT reliably produce accents
- **Key insight:** Accents only work when the LOCATION/ENVIRONMENT makes the accent plausible based on movie training data
  - Star Wars character + "Hispanic accent" = no accent (SW films don't have that)
  - Medieval monastery + "British accent" = works (plausible from movie data)
  - Brazilian man in NYC = sounds American
  - Brazilian man on a beach in Rio = speaks Portuguese (may overshoot to full language change)
- **Rule:** Match the accent to an environment where that accent naturally appears in film/TV

### Video-Game Style Instead of Photorealism
- Fantasy/historical characters often render in 3D video-game style
- Fix: add `muted colors, cinematic film` to prompt
- If still video-game style, change the prompt -- some concepts are stuck

### Prompt Not Followed Exactly
- Veo3 may not follow action descriptions precisely (e.g., "climbing stairs" becomes "coming down a well")
- This is inherent to the model -- regenerate or adjust wording

### Fight Scenes Start Slow
- Fight/action scenes typically begin slowly and become dynamic as the clip progresses
- This is normal behavior -- plan to trim the opening seconds if needed

---

## 6. Prompt Structure and Length

### Prompt Architecture
1. **Style/format keywords FIRST** -- Veo3 weighs the beginning of the prompt more heavily (e.g., `2D anime`, `muted color cinematic film`, `man on the street interview`)
2. **Character description** -- detailed physical appearance (skin, hair, clothing, accessories)
3. **Scene/action description** -- what's happening, where
4. **Dialogue** -- what characters say (attribute clearly to each character)
5. **Audio/ambient** -- ambient sounds, music style, instruments

### Dialogue Prompting
- You CAN give each character specific dialogue lines
- Clearly attribute which character says what: "The stormtrooper reporter says: [line]. The male Sith says: [line]."
- Tone of voice works better when you describe the GENERAL IDEA rather than a specific script: `old man whispering about what it was like to fight back in the day` produces better emotional delivery than a word-for-word script
- Tone keywords that work: `aggressively shout`, `nervous, stuttering, and unsure`, `quietly whispers`

### Style Keywords
- Put animation/visual style at the START of the prompt for maximum effect
- Examples: `2D anime`, `3D Pixar style`, `horror movie`, `comedy movie`, `sci-fi movie`
- Movie genre changes lighting, color palette, and overall vibe automatically

### Photorealism Keywords
- `muted colors` + `cinematic film` = photorealistic look
- `shot on a Sony camera` = cinematic quality boost

---

## 7. Multi-Clip Storytelling

### Vlog-Style Videos (Tip 1)
- Use multiple camera angles for the same character to simulate a real vlog:
  - `self camera angle shot from an extended arm` (selfie angle)
  - `holding up a vlog cam on a selfie stick` (mid-distance selfie)
  - `shot from a vlog camera` (wide angle, full environment)
- Works with any character (yeti, stormtrooper, etc.)

### Man-on-the-Street Interviews (Tip 2)
- Start prompt with: `a man on the street interview`
- Define reporter + interviewee, their emotions/attitudes
- Assign specific dialogue to each character

### Combining Camera Techniques (Tip 22)
- Mix shots + angles + movements in a single prompt for dynamic sequences
- Example: close-up on face, then camera pulls back to reveal horse riding
- Example: slow crane shot behind character walking up stairs, camera flies above, tilts down to reveal castle
- This demonstrates scale (small character vs. massive environment)

### Creating Longer Videos (Tip 30)
- Veo3 has an "add to scene" / "extend video" feature
- **Limitation:** Falls back to older Veo2 model -- lower quality, no sound effects
- Extended clips roughly follow the prompt but quality degrades
- For now, better to generate separate high-quality clips and edit them together

### Infinite Looping Videos (Tip 28)
- No native loop feature in Veo3
- **Workaround:**
  1. Take a generated clip
  2. Duplicate it in a video editor (e.g., CapCut)
  3. Reverse the second copy
  4. Place them side by side: forward + reverse = seamless loop
  5. Stack as many copies as needed for longer loops

---

## 8. Specific Example Prompts

### Vlog-Style Yeti
> Self camera angle shot from an extended arm. A Yeti with white fur holding up a fish. He's in an icy landscape. "Welcome back to Yeti Adventures. Today, we're learning how to go ice fishing."

### Vlog on Selfie Stick
> Holding up a vlog cam on a selfie stick. He is talking to the vlog cam. "I've been out here since sunrise. Just me. No internet trolls asking if I'm related to Bigfoot."

### Man on the Street Interview
> A man on the street interview. Inside Gotham City, a young female reporter asked a young man what he thinks about Batman. The young man is unhappy with how many problems Batman causes. "What are your thoughts on Batman?" "Honestly, he causes more problems than he solves. This city's a mess because of him."

### Multi-Character Dialogue (scripted)
> Stormtrooper reporter interviewing a Sith. The Stormtrooper reporter says: "Are the rumors about the war in the outer rim true?" The male Sith says: "The Outer Rim is ripe for conquest. The Empire always expands."

### Accent via Environment
> A Brazilian man on a beach in Rio de Janeiro... (produces Portuguese-accented or Portuguese-language speech)
> Medieval monastery, British-accented monk... (produces British accent naturally)

### Tone of Voice -- Aggressive
> Viking commander aggressively shouts and commands his troops

### Tone of Voice -- Nervous
> Nervous, stuttering, unsure of himself

### Tone of Voice -- Whispering
> Old man whispering about what it was like to fight back in the day

### Ambient Sound
> [scene description] + the sound of waves at the beach
> [scene description] + the sounds of wind rustling and cars honking in the background

### Background Music
> [scene description] + suspenseful and thrilling music
> [scene description] + a guqin playing in the background

### Green Screen Consistent Character
> Instantly jump/cut to on frame one. She walks next to a huge white direwolf in an icy landscape. It is snowing.

### Photorealism Fix
> [detailed character description]. Muted colors, cinematic film. [scene description]

### Flux Context -- Consistent Character Repose
> Create an image of this female character in a medieval tavern. Her appearance should stay the same. Cinematic film shot on a Sony camera.

### Consistent Product
> Create a side profile photo of a young Canadian man wearing the blue headphones. The gold patterns on the headphones should remain the same. On a street in Montreal, shot on a Sony camera.

### Fight Scene
> Kung fu fight scene. [character description]. [scene description].

### First-Person POV
> First-person POV shot. A character running through a trench in World War I.

### Camera Movement Combo
> Slow crane shot behind the female character, walking up the steps of an ancient castle. Then the camera flies above and slowly tilts down to reveal the entire castle.

### Image Preview Prompt (for frames-to-video image gen)
> Photo of a panther in a jungle. Golden afternoon light and shadows. Green foliage shot on a Sony camera.

---

## 9. Miscellaneous Tips

### Vertical Videos (Tip 10)
- No native vertical video option in Veo3
- **Workaround:** Take a vertical image, rotate it 90 degrees to landscape, upload to "frames to video", generate the video, then rotate the output video back to vertical
- Veo3 CAN animate a 90-degree rotated image and maintain good resolution

### Upscaling (Tip 8)
- Free with subscription: download button > select "upscaled" version
- Upscales from 720p to 1080p
- Quality is okay but not amazing -- some graininess in backgrounds, faces not ultra-detailed
- Takes a couple minutes to process

### Flow TV for Inspiration (Tip 9)
- Inside the Flow interface, "Watch Flow TV" shows curated videos with viewable prompts
- Uses "show prompt" button to reveal exact prompts used
- Most are Veo2 (older model) but still useful for prompt structure ideas
- Grid view lets you browse many examples; flip through channels for different styles

### Fast Mode (Tip 18)
- Text-to-video only, half the cost of regular mode
- Quality is still high compared to other AI video generators
- Anatomy stays consistent even during dynamic motion
- **Limitation:** Cannot generate character dialogue
- Good for action/visual shots where speech isn't needed

### Animation Styles (Tip 26)
- Put animation style keyword at the START of your prompt
- Supported styles: `3D Pixar style`, `2D anime`, normal cinematic, and more
- The beginning of the prompt carries more weight for style than the end

### Movie Genre Affects Everything (Tip 25)
- Adding genre keywords changes lighting, color palette, and mood automatically
- `horror movie` = dark, moody lighting
- `comedy movie` = lighthearted, brighter colors
- `sci-fi movie` = futuristic palette and set design

### Image Generator as Preview (Tip 29)
- In "frames to video," click "add an image" and let Veo3 GENERATE an image from a text prompt
- Gives you preview thumbnails to choose from before spending credits on video generation
- Pick the composition/angle/palette you like, THEN animate it
