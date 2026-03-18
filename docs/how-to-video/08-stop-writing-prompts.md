# The Secret to Better AI Videos: Stop Writing Prompts

**Source:** [AI Video School — Mike](https://youtube.com/watch?v=cGTBzed4S4w)
**Length:** ~8 minutes
**Core thesis:** Don't write video prompts yourself. Train an LLM on the model's official docs and let it generate optimized prompts from your plain-English ideas.

---

## 1. The Approach: LLM-as-Prompt-Translator

Instead of manually crafting video generation prompts, use this workflow:

1. **Download the official prompt documentation** for the video model you're using (Runway, Kling, Luma Dream Machine, Veo, Hailuo, etc.)
2. **Save the docs as PDF** (use browser's "Print > Save as PDF")
3. **Upload into a custom GPT or Gemini Gem** with instructions like: "Provide optimized prompts for the user's ideas based on the documentation"
4. **Describe your idea in plain English** — focus on what you want to see and how you want the viewer to feel
5. **Let the LLM format a model-optimized prompt** that follows the specific model's syntax and best practices

**Free tier alternative:** Upload the docs directly into a chat window (ChatGPT, Gemini, DeepSeek). Caveat: the longer you chat, the more it forgets the uploaded document. Start a new chat for every project.

---

## 2. Mental Model: You Are the Director, Not the Translator

- **"The art is not your prompt. The art is your idea."**
- Prompting is translation work — converting human intent into structured LLM language
- Writing prompts manually burns creative energy on translation instead of ideation
- The real skill is **articulating your creative vision** — what the shot looks like AND how the viewer should feel
- **"If a computer is going to read it, I trust a computer to write it. If a human is going to read it, I need a human to write it."**

---

## 3. Iteration Strategy: Generate and Iterate via Conversation

This is the key workflow advantage — iteration becomes a conversation, not prompt rewriting:

- **Bad result?** Tell the GPT what went wrong in plain English: "It feels too over-the-top dramatic. I want something more cinematic and emotionally subdued."
- **Attach screenshots** of bad results and describe what you want changed
- **The GPT rewrites the prompt** using proper model syntax — you never touch the technical prompt format
- Each iteration keeps you focused on creative direction, not prompt engineering
- The conversation itself forces you to clarify your thinking about what you actually want

### Anti-pattern: Manual prompt rewriting
Manually editing structured prompts after bad results wastes time on format/syntax when your actual feedback is about creative direction.

---

## 4. Camera and Visual Control

Control camera work by describing shots the way you'd picture them in your mind:

- **"I want a closeup of her face and then reveal what she's looking at"** — the LLM translates this into proper camera direction syntax
- **"Start on her face, pull back and orbit around her to see her view"** — iterate on camera direction conversationally
- You describe cinematic intent; the LLM handles the technical camera terminology the model expects

---

## 5. Multi-Model Comparison Workflow

Use one idea to generate optimized prompts for multiple models simultaneously:

1. Give your GPT an idea (e.g., a movie concept)
2. Ask for model-optimized prompts for Runway, Hailuo, Veo, Kling, etc. all at once
3. Run the same idea through each model with its optimized prompt
4. Compare results to see which model gets closest to your vision

This works because each model has different prompt syntax and best practices — the GPT handles the per-model formatting.

---

## 6. Failure Modes of Traditional Prompting

- **Wasting creative energy on translation** instead of ideation
- **Not following model-specific syntax** — each model has its own documentation and preferred prompt structure
- **"Prompt engineer" mindset** — the hype around prompt engineering convinced people that manually writing prompts was the valuable skill, when the real skill is creative expression
- **Context drift** — long chat sessions cause the LLM to forget uploaded documentation (solution: new chat per project)

---

## 7. Setup Details

### Custom GPT (ChatGPT paid)
- Go to GPTs > Create
- Upload model documentation PDF(s) in the Knowledge section
- Can have a general "prompt sidekick" with multiple model docs, OR model-specific GPTs
- Add placeholder prompts like "outline best practices" to quickly reference the docs

### Gemini Gem (Gemini paid)
- Open side menu > Explore Gems > New Gem
- Upload documentation as knowledge
- Instructions: "Provide optimized prompts for the user's ideas based on the documentation"

### Where to find model documentation
| Model | Location |
|-------|----------|
| Hailuo | In-app documentation |
| Kling | In-app documentation |
| Luma Dream Machine | In-app documentation |
| Runway | Multiple documentation pages (check several sections) |
| Veo | DeepMind site > Build with Gemini > Documentation > Veo > Prompt writing basics |

---

## Key Takeaway for Scribario

This maps directly to our content pipeline. When generating video prompts for users, we should:
- Embed model-specific documentation into our prompt generation system
- Let users describe intent in plain language
- Have Claude translate to model-optimized prompts using the docs as context
- Support iterative refinement through conversation, not prompt editing
