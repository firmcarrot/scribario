# Long-Form Video Creation with VEO 3.1

**Source:** [How to Finally Make Long Videos with VEO 3.1 (Create Consistent Videos of Any Length)](https://youtube.com/watch?v=c772SYf6k-4)
**Platform demonstrated:** Flow (uses VEO 3.1 under the hood)
**Max output:** Up to 3 minutes per project

---

## The Core Workflow (6 Steps)

1. **Write a full script first** -- not random prompts. Have a complete narrative/dialogue before touching any video tool.
2. **Generate a detailed character description** -- facial features, hair color, clothing style, accessories. This description gets reused in EVERY scene prompt.
3. **Break the script into separate scenes** (5 in the demo). Each scene prompt must include BOTH the dialogue portion AND the full character + environment description.
4. **Convert prompts to JSON format** -- VEO 3.1 responds more effectively to structured JSON inputs than plain text. Each JSON object should contain dialogue, character description, and scene setting as distinct fields.
5. **Generate scenes sequentially** using the "extend" feature, not as independent clips.
6. **Export the final video** -- preview may show small pauses between scenes, but the exported file removes them.

---

## Character/Subject Consistency

- **Repeat the full character description in every single scene prompt.** Do not assume the model remembers from the previous generation. Every prompt must specify: appearance, facial structure, hair color, clothing pattern, accessories.
- **Use ChatGPT (or any LLM) to generate one canonical vivid character description**, then embed that same description into all scene prompts.
- **Same dress, same face, same overall look** -- the creator explicitly calls this out as the key constraint when extending scenes.

---

## Scene Extension Technique

- Use the **"Add to Scene"** button to open the Scene Builder. This is NOT the same as generating a new independent clip.
- **Drag the playback pointer** to the exact frame where you want the next scene to continue from.
- Click the **plus icon** to access the "Extend" option. This opens a transition interface that ensures the new scene begins exactly where the previous one ended.
- Paste the next scene's prompt (with full character + environment description) into the extend prompt field, then generate.
- The extend feature handles visual continuity -- it uses the last frame of the previous clip as the anchor for the next generation.

---

## Prompting Patterns

### Script Prompt to ChatGPT
> Write a short text around 30 seconds for a 25-year-old female American influencer who looks directly into the camera while ranting about the cost of living in California as she walks through a busy street filled with people and cars.

### Character Description Prompt to ChatGPT
> Generate a vivid description of this influencer, including her facial features, hair color, clothing style, accessories, and more.

### Scene Breakdown Prompt to ChatGPT
> Break the dialogue script into five separate scenes. Each scene should carry a portion of the dialogue AND include a detailed description of the influencer and the environment around her -- her appearance, facial structure, hair color, clothing pattern, accessories, and a vivid picture of the busy California street with people moving around and cars passing by.

### JSON Conversion Prompt to ChatGPT
> Convert the prompt into JSON format (with dialogue, character description, and scene setting as structured fields).

---

## Common Failures and Fixes

| Problem | Solution |
|---------|----------|
| Character appearance drifts between clips | Embed the FULL character description in every scene prompt, not just the first one |
| Scenes don't connect smoothly | Use the "Extend" feature (not independent text-to-video generations). Extend anchors to the last frame. |
| ChatGPT doesn't follow your scene breakdown prompt | Regenerate / re-prompt. The creator hit this in the demo and just asked again. |
| Preview shows pauses between scenes | This is normal in preview. The final export removes the pauses. |
| A generated scene looks wrong | Delete the scene and regenerate. Iterate until satisfied. Don't try to fix bad generations. |
| Plain text prompts produce inconsistent results | Use JSON-structured prompts. VEO 3.1 handles structured input better. |

---

## Pipeline Summary

```
Script (full dialogue)
  --> Character description (one canonical version)
  --> Scene breakdown (N scenes, each with dialogue + character + environment)
  --> JSON conversion (structured format for each scene)
  --> Generate Scene 1 (text-to-video)
  --> Extend Scene 2 from Scene 1's last frame (paste JSON prompt)
  --> Extend Scene 3 from Scene 2's last frame
  --> ... repeat ...
  --> Preview --> Export --> Download
  --> (Optional) Post-edit in CapCut to trim problem sections
```

---

## Key Takeaways for Automation

1. **The entire pre-production step (script, character description, scene breakdown, JSON conversion) is LLM work.** This can be fully automated in a pipeline.
2. **Scene-by-scene sequential generation with the extend feature is the only way to maintain continuity.** Parallel independent generation will NOT produce consistent characters.
3. **JSON-structured prompts outperform plain text** for VEO 3.1 consistency.
4. **Regeneration is expected.** Budget for multiple attempts per scene -- results are not always perfect on the first try.
5. **Post-production cleanup** (trimming bad sections) is expected. CapCut or similar editor is part of the workflow.
6. **VEO 3.1 "fast" mode** saves credits while still producing usable results.
