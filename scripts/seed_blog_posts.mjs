#!/usr/bin/env node
/**
 * Seed blog post bodies from scribario-web static posts into Supabase.
 * Run: node scripts/seed_blog_posts.mjs
 *
 * Reads the posts from scribario-web/src/content/blog/posts.ts (via dynamic import),
 * and updates the body column for each matching slug in blog_posts.
 */

import { createClient } from "@supabase/supabase-js";
import { readFileSync } from "fs";
import { resolve } from "path";

const SUPABASE_URL = "https://iptivnzimbpoepwdlwri.supabase.co";
const SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwdGl2bnppbWJwb2Vwd2Rsd3JpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzE4MzMyOCwiZXhwIjoyMDg4NzU5MzI4fQ.vvGQbLzAkYTurU4KJ9F0--NZ84MVt99T4R7znqEcwX0";

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Parse the posts.ts file manually (it's TypeScript with template literals)
const postsPath = resolve(import.meta.dirname, "../../scribario-web/src/content/blog/posts.ts");
const content = readFileSync(postsPath, "utf-8");

// Extract each post object by finding slug patterns and their body content
const slugBodyPairs = [];
const slugRegex = /slug:\s*"([^"]+)"/g;
let match;
const slugs = [];
while ((match = slugRegex.exec(content)) !== null) {
  slugs.push({ slug: match[1], index: match.index });
}

for (const { slug, index } of slugs) {
  // Find the body: ` block after this slug
  const afterSlug = content.slice(index);
  const bodyStart = afterSlug.indexOf("body: `");
  if (bodyStart === -1) continue;

  const bodyContentStart = index + bodyStart + 7; // "body: `" is 7 chars
  // Find the closing backtick + comma/newline
  let depth = 0;
  let bodyEnd = bodyContentStart;
  for (let i = bodyContentStart; i < content.length; i++) {
    if (content[i] === '`' && content[i - 1] !== '\\') {
      bodyEnd = i;
      break;
    }
  }

  const body = content.slice(bodyContentStart, bodyEnd);
  slugBodyPairs.push({ slug, body });
}

console.log(`Found ${slugBodyPairs.length} posts to update`);

for (const { slug, body } of slugBodyPairs) {
  const { error } = await supabase
    .from("blog_posts")
    .update({ body })
    .eq("slug", slug);

  if (error) {
    console.error(`Failed to update ${slug}:`, error.message);
  } else {
    console.log(`Updated body for: ${slug} (${body.length} chars)`);
  }
}

console.log("Done!");
