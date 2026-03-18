# Veo 3.1 Feature Test & Practical Lessons

**Source:** "I Tried Every New Veo 3.1 Trick - Wow" by Matt Wolfe (Future Tools)
**URL:** https://youtube.com/watch?v=kYtCVXaB9Jw
**Platform tested:** Google Flow (labs.google/fx/tools/flow) + Gemini + Leonardo

---

## 1. Camera Control

No explicit camera control techniques were tested in this video. The creator focused on feature-level tests (ingredients, frames, editing) rather than camera direction prompting.

---

## 2. Character Consistency Across Clips

- **Ingredients to Video** is the primary method for character consistency. Upload a face image as one of the three ingredient slots, and Veo will incorporate that face into the generated video.
- **Gotcha: Clothing/details drift.** When using ingredients-to-video with a face photo + moose hat + candy world, the model changed pants color for no reason and the moose hat morphed/changed a few seconds into the clip.
- **Face likeness works reasonably well** but the surrounding details (clothing, accessories) are not locked down -- expect drift on non-face elements.

---

## 3. Audio/SFX Prompting

- **Audio is auto-generated** -- you do not prompt for it separately. Veo generates both video and audio from the text prompt.
- **Audio is unpredictable and often nonsensical.** Examples from testing:
  - A man sitting down got audio of someone giving a business presentation ("I want to show you the best way to do your job")
  - A morphing sequence got dramatic dialogue ("Oh, what's happening to me?", "Oh wow, I'm a wolf")
  - Some clips got random music, weird sound effects, or gibberish singing
- **You cannot control audio independently** -- it comes along with the video generation. No separate audio prompt field.
- **Sora 2 comparison:** Sora generated more contextually appropriate audio (lightsaber sounds, fitting dialogue for a Jedi scene).

---

## 4. Lighting Techniques

No specific lighting prompting was tested. This video focused on feature demos rather than cinematography control.

---

## 5. Common Failure Modes and Fixes

### Physics failures
- **Backflips fail consistently.** Prompted "the man does a backflip" -- across 4 variations, none completed a proper backflip. The physics broke every time (partial rotations, impossible body positions, "interesting" flips). Sora 2 handled the same motion noticeably better.

### Morph/transition failures
- **Frame-to-frame morphs skip steps.** When using first-and-last-frame to morph human-to-wolf, the model does amazing mid-transition work but then **jump-cuts** to the final frame instead of completing the smooth morph. Pattern: great buildup -> abrupt skip to end state.
- **Frustrating near-misses:** The morphing looks incredible through the middle portion (shirt coming off, body changing) then just fades/jumps to the target image.

### Ingredient cropping issues
- **Forced square crop on ingredients.** All three ingredient images get forced into the same crop aspect ratio, which can cut off important details (ear flaps on a hat got cropped out).

### Editing limitations
- **Cannot replace/change existing objects.** Tried to change a lightsaber into a hockey stick using the edit feature -- it did absolutely nothing. The object stayed unchanged.
- **Cannot remove objects yet.** This feature was announced but is not available. Two suns appeared in a scene with no way to remove one.
- **Added objects may be static.** When adding a spaceship to a scene using region selection, the spaceship appeared as a static image with no animation/hover movement. However, adding a person walking into a scene DID animate properly.

### Model version limitations
- **Ingredients-to-video only works on "3.1 Fast" mode.** Attempting to use it with "3.1 Quality" mode throws an error: "this feature isn't supported."
- **Frames-to-video DOES work on Quality mode.**

### Aspect ratio gotcha
- **Output aspect ratio is a separate setting from image crop.** Cropping images to landscape does NOT automatically set the output to landscape. You must manually change the aspect ratio dropdown. Forgetting this produces portrait output with landscape images squished to the top.

---

## 6. Prompt Structure/Length

- **Prompts tested were SHORT and direct.** No elaborate multi-paragraph prompts. Examples:
  - "A man with a moose hat dances through a colorful Candy Land world"
  - "The man sits down"
  - "The man morphs into a wolf"
  - "A Jedi swinging a lightsaber"
  - "Mickey Mouse high-fives Super Mario"
  - "Anime cartoon featuring Batman and Spongebob"
  - "The man does a backflip and then gives a double thumbs up to the camera"
- **Extension prompts are action-focused.** When extending a clip, you answer "what should happen next" with a short action description.
- **Edit prompts describe what to ADD.** Example: "an alien spaceship hovers in the background" or "a man in a black cape wearing a black mask walks through the door behind her."

---

## 7. Multi-Clip Storytelling / Scene Extension

- **Extension works by taking the last frame of the current clip as the first frame of the next clip**, then stitching them together automatically.
- **Available in Flow via the "+" button -> Extend** after adding a clip to the scene.
- **You describe what happens next** in a text prompt. The extension maintains visual continuity from the previous clip's last frame.
- **Result:** 15-second combined video (original + extension). Can keep extending for 1 minute or more.
- **Quality varies per extension.** Multiple variations are generated -- pick the best one.
- **Extension was already available in Flow** before 3.1, but now reportedly available outside Flow as well.

---

## 8. First-and-Last-Frame Techniques

- **Feature name in Flow: "Frames to Video"**
- **Upload a start image and an end image**, then write a prompt describing the transition.
- **Works with Quality mode** (unlike ingredients-to-video which is Fast-only).
- **Simple transitions work well.** Standing-to-sitting with matching real photos produced a near-perfect animation.
- **Complex transformations (morphs) partially work.** Human-to-wolf morph produced stunning mid-transition frames but consistently jump-cut to the end frame instead of smooth completion.
- **Tip: Match the background/environment between start and end frames.** For the wolf morph, the creator used a white background on the wolf image to minimize environment changes, making the transition smoother.
- **Tip: Choose start poses that ease the transition.** Used a crouched/low position as the start frame since it's closer to an animal pose.
- **Gotcha: Portrait vs. landscape mismatch.** If you crop images as landscape but leave the generation setting on portrait, the start frame gets placed at the top of a portrait video and the end frame becomes another landscape image awkwardly placed -- wasting the generation.

---

## 9. Reference Image Techniques

### Ingredients to Video (new in 3.1)
- **Upload up to 3 reference images** that get combined into a single video.
- **Slots are conceptual:** face/character + object/clothing + environment/style. Like Google Whisk but for video.
- **Examples tested:**
  - Face photo + moose hat image + candy world image -> man in moose hat dancing in candy world
  - Motorcyclist on dunes + gemstone image -> combined scene (Google demo)
  - Environment + clothing + woman's face -> video with all elements (Google demo)
- **Only works on 3.1 Fast mode** (not Quality).
- **All ingredient images get forced to the same crop**, which can lose important details. No way to set different crops per image.

### First/Last Frame as Reference
- **Using your own photos as first/last frames** gives strong likeness control for that specific frame, with animation between them.

---

## 10. Specific Example Prompts (Tested in Video)

| Prompt | Mode | Result Quality |
|--------|------|----------------|
| "A man with a moose hat dances through a colorful Candy Land world" | Ingredients + Fast | Good -- fun results, some clothing drift |
| "The man does a backflip and then gives a double thumbs up to the camera" | Extend | Poor physics, got thumbs up right |
| "The man sits down" | Frames-to-video + Quality | Excellent -- near perfect |
| "The man morphs into a wolf" | Frames-to-video + Quality | Mid-transition amazing, ending jump-cuts |
| "A Jedi swinging a lightsaber" | Text-to-video | Underwhelming -- liquid on lightsaber, two suns, generic look |
| "An alien spaceship hovers in the background" | Edit (region select) | Spaceship appeared but static/unanimated |
| "A man in a black cape wearing a black mask walks through the door behind her" | Edit (no region) | Worked -- person was animated, found the door |
| "Make the lightsaber a hockey stick" | Edit (region select) | FAILED -- no change at all |
| "Mickey Mouse high-fives Super Mario" | Text-to-video | Generated successfully (surprising -- no guardrail block) |
| "Anime cartoon featuring Batman and Spongebob" | Text-to-video | Generated successfully, looked more like Western cartoon than anime |

---

## 11. Platform & Pricing Notes

- **Flow URL:** labs.google/fx/tools/flow
- **Gemini:** gemini.google.com -> "Create Video"
- **Requires paid plan:** Google AI Premium ($20/mo) or Google AI Ultra ($250/mo). 30-day free trial available.
- **Leonardo** is reportedly the cheapest third-party option for Veo generation (creator is a Leonardo advisor with equity -- bias disclosed).
- **Two quality tiers:** 3.1 Fast (quicker, lower quality, supports all features) and 3.1 Quality (slower, higher quality, does NOT support ingredients-to-video).
- **Output options:** 1-4 videos per prompt, landscape or portrait.

---

## 12. Veo 3.1 vs Sora 2 Summary

| Category | Veo 3.1 | Sora 2 |
|----------|---------|--------|
| Realistic people | Weaker | Better |
| Physics (backflips etc.) | Fails often | Noticeably better |
| Audio quality/relevance | Random/unpredictable | More contextually appropriate |
| Trademark IP (Mickey, Batman) | Currently generates freely | Now blocks most IP |
| Cartoon/anime style | Good aesthetics | Blocked by guardrails |
| Multi-image ingredients | Supported (3 images) | Not available |
| First-and-last frame | Supported | Not tested in video |
| In-video editing (add objects) | New in 3.1 | Not available |
| Video extension | Supported | Not tested in video |
| Overall initial prompt quality | Needs iteration/editing | Better one-shot results |

---

## Key Takeaways for Content Creators

1. **Use "3.1 Fast" for ingredients-to-video** -- Quality mode does not support it.
2. **Always double-check the aspect ratio dropdown** matches your intended output -- it does not auto-detect from your uploaded images.
3. **Simple transitions (sit, stand, walk) work great with frames-to-video.** Complex morphs look amazing in the middle but choke on the final transition.
4. **The edit feature can ADD animated characters** but cannot replace or remove existing objects. Don't try to swap elements -- it silently does nothing.
5. **When adding objects via edit, skip the region selector for animated additions.** Adding a person without region selection produced animated results; adding a spaceship with region selection produced a static overlay.
6. **Trademark IP currently generates freely on Veo 3.1** (Mickey Mouse, Batman, Spongebob, etc.) -- but this will likely get locked down soon. Use it while you can.
7. **Generate 4 variations per prompt** and pick the best -- quality varies significantly between generations.
8. **For human likeness, use ingredients-to-video with a face photo** as one of the three ingredient images.
9. **Match environments between first/last frames** to help the model focus on the subject transition rather than fighting a scene change.
