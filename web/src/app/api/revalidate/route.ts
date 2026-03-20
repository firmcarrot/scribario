import { revalidatePath } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const secret = request.headers.get("x-revalidate-secret");

  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
  }

  try {
    const body = await request.json();
    const slug = body?.slug;

    // Always revalidate the blog list page
    revalidatePath("/blog");
    // Also revalidate sitemap
    revalidatePath("/sitemap.xml");

    // If a specific slug is provided, revalidate that post too
    if (slug) {
      revalidatePath(`/blog/${slug}`);
    }

    return NextResponse.json({
      revalidated: true,
      slug: slug || null,
      timestamp: new Date().toISOString(),
    });
  } catch {
    return NextResponse.json({ error: "Failed to revalidate" }, { status: 500 });
  }
}
