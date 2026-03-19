import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

interface GenerateBlogRequest {
  keyword: string;
  brief?: string;
  tone?: string;
}

interface AnthropicMessage {
  id: string;
  content: Array<{ type: string; text: string }>;
  model: string;
  stop_reason: string;
  usage: { input_tokens: number; output_tokens: number };
}

function estimateReadingTime(text: string): number {
  const wordsPerMinute = 230;
  const wordCount = text.split(/\s+/).length;
  return Math.max(1, Math.ceil(wordCount / wordsPerMinute));
}

function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function parseResponse(raw: string): {
  title: string;
  description: string;
  body: string;
  slug: string;
  readingTime: number;
} {
  // Extract title: first H1 line or first line
  const titleMatch = raw.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : raw.split("\n")[0].trim();

  // Extract meta description: look for a line after "Meta Description:" or similar
  const descMatch = raw.match(
    /(?:meta\s*description|description)\s*:\s*(.+)/i
  );
  let description = "";
  if (descMatch) {
    description = descMatch[1].trim().replace(/^["']|["']$/g, "");
  }

  // Build body: remove the title line and meta description line from the markdown
  let body = raw;
  if (titleMatch) {
    body = body.replace(/^#\s+.+$/m, "").trim();
  }
  if (descMatch) {
    body = body
      .replace(/(?:meta\s*description|description)\s*:\s*.+/i, "")
      .trim();
  }

  // If no explicit description was found, use the first paragraph as description
  if (!description) {
    const firstParagraph = body
      .split("\n\n")
      .find((p) => p.trim() && !p.trim().startsWith("#"));
    description = firstParagraph
      ? firstParagraph.replace(/\n/g, " ").trim().slice(0, 160)
      : "";
  }

  return {
    title,
    description,
    body,
    slug: generateSlug(title),
    readingTime: estimateReadingTime(body),
  };
}

export async function POST(request: NextRequest) {
  // Auth check — verify session exists
  const cookieStore = await cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll(); },
        setAll() {},
      },
    }
  );
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "ANTHROPIC_API_KEY is not configured" },
      { status: 500 }
    );
  }

  let payload: GenerateBlogRequest;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const { keyword, brief, tone } = payload;

  if (!keyword || typeof keyword !== "string" || keyword.trim().length === 0) {
    return NextResponse.json(
      { error: "keyword is required and must be a non-empty string" },
      { status: 400 }
    );
  }

  const effectiveTone = tone?.trim() || "professional, conversational";

  const systemPrompt = `You are an expert SEO blog writer for Scribario, an AI-powered social media automation platform. Your task is to write high-quality, SEO-optimized blog posts.

Follow these rules strictly:
- Write in markdown format
- Start with a single H1 title line (# Title)
- On the very next line, write: Meta Description: <a compelling 150-160 character meta description>
- Then write the blog post body using H2 (##) and H3 (###) subheadings
- Target the given keyword naturally: include it in the title, the first paragraph, and at least 2 subheadings
- Write between 800 and 1500 words (body only, excluding title and meta description)
- Begin with a compelling introduction paragraph that hooks the reader
- End with a clear conclusion that includes a call to action
- Use short paragraphs (2-4 sentences) for readability
- Include bullet points or numbered lists where appropriate
- Write in a ${effectiveTone} tone
- Do NOT include any preamble, commentary, or explanation outside the blog post itself`;

  const userMessage = brief
    ? `Write an SEO blog post targeting the keyword: "${keyword.trim()}"\n\nAdditional brief: ${brief.trim()}`
    : `Write an SEO blog post targeting the keyword: "${keyword.trim()}"`;

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        system: systemPrompt,
        messages: [{ role: "user", content: userMessage }],
      }),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error("Anthropic API error:", response.status, errorBody);
      return NextResponse.json(
        {
          error: "Failed to generate blog post",
          detail:
            process.env.NODE_ENV === "development" ? errorBody : undefined,
        },
        { status: 502 }
      );
    }

    const data: AnthropicMessage = await response.json();

    const textBlock = data.content.find((block) => block.type === "text");
    if (!textBlock) {
      return NextResponse.json(
        { error: "No text content in API response" },
        { status: 502 }
      );
    }

    const parsed = parseResponse(textBlock.text);

    return NextResponse.json(parsed, { status: 200 });
  } catch (err) {
    console.error("Generate blog error:", err);
    return NextResponse.json(
      { error: "Internal server error while generating blog post" },
      { status: 500 }
    );
  }
}
