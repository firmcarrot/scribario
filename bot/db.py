"""Supabase database client — singleton for the bot and worker."""

from __future__ import annotations

from datetime import UTC
from functools import lru_cache

from supabase.client import Client

from bot.config import get_settings
from supabase import create_client


@lru_cache
def get_supabase_client() -> Client:
    """Get the Supabase client using service role key (bypasses RLS)."""
    s = get_settings()
    if not s.supabase_url or not s.supabase_service_role_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set. "
            "Check your .env file."
        )
    return create_client(s.supabase_url, s.supabase_service_role_key)


async def get_tenant_by_telegram_user(telegram_user_id: int) -> dict | None:
    """Look up tenant for a Telegram user. Returns tenant dict or None."""
    client = get_supabase_client()
    result = (
        client.table("tenant_members")
        .select("tenant_id, role, tenants(id, name, slug)")
        .eq("telegram_user_id", telegram_user_id)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    return None


async def create_content_request(
    tenant_id: str,
    intent: str,
    platform_targets: list[str] | None = None,
    due_at: "datetime | None" = None,
    style_override: str | None = None,
) -> dict:
    """Create a new content request in the database."""
    from datetime import datetime  # noqa: F401 — used in type annotation above

    client = get_supabase_client()
    data: dict = {
        "tenant_id": tenant_id,
        "intent": intent,
        "platform_targets": platform_targets,
        "status": "pending",
    }
    if due_at is not None:
        data["due_at"] = due_at.isoformat()
    if style_override is not None:
        data["style_override"] = style_override
    result = (
        client.table("content_requests")
        .insert(data)
        .execute()
    )
    return result.data[0]


async def update_content_request_status(request_id: str, status: str) -> None:
    """Update the status of a content request."""
    client = get_supabase_client()
    client.table("content_requests").update({"status": status}).eq("id", request_id).execute()


async def create_content_draft(
    request_id: str,
    tenant_id: str,
    caption_variants: list[dict],
    image_urls: list[str],
) -> dict:
    """Create a content draft with generated captions and images."""
    client = get_supabase_client()
    result = (
        client.table("content_drafts")
        .insert({
            "request_id": request_id,
            "tenant_id": tenant_id,
            "caption_variants": caption_variants,
            "image_urls": image_urls,
            "status": "generated",
        })
        .execute()
    )
    return result.data[0]


async def update_draft_status(draft_id: str, status: str) -> None:
    """Update the status of a content draft."""
    client = get_supabase_client()
    client.table("content_drafts").update({"status": status}).eq("id", draft_id).execute()


async def get_draft(draft_id: str) -> dict | None:
    """Get a content draft by ID."""
    client = get_supabase_client()
    result = client.table("content_drafts").select("*").eq("id", draft_id).limit(1).execute()
    if result.data:
        return result.data[0]
    return None


async def create_approval_request(
    draft_id: str,
    tenant_id: str,
    telegram_message_id: int,
    telegram_chat_id: int,
) -> dict:
    """Create an approval request linked to a Telegram message."""
    client = get_supabase_client()
    result = (
        client.table("approval_requests")
        .insert({
            "draft_id": draft_id,
            "tenant_id": tenant_id,
            "telegram_message_id": telegram_message_id,
            "telegram_chat_id": telegram_chat_id,
            "status": "pending",
        })
        .execute()
    )
    return result.data[0]


async def create_posting_job(
    draft_id: str,
    tenant_id: str,
    platform: str,
    caption: str,
    asset_urls: list[str],
    idempotency_key: str,
) -> dict:
    """Create a posting job for a specific platform."""
    client = get_supabase_client()
    result = (
        client.table("posting_jobs")
        .insert({
            "draft_id": draft_id,
            "tenant_id": tenant_id,
            "platform": platform,
            "caption": caption,
            "asset_urls": asset_urls,
            "idempotency_key": idempotency_key,
            "status": "queued",
        })
        .execute()
    )
    return result.data[0]


async def create_feedback_event(
    draft_id: str,
    tenant_id: str,
    action: str,
    reason_tags: list[str] | None = None,
    edited_caption: str | None = None,
) -> dict:
    """Record a feedback event (approve, reject, edit, regenerate)."""
    client = get_supabase_client()
    data: dict = {
        "draft_id": draft_id,
        "tenant_id": tenant_id,
        "action": action,
    }
    if reason_tags:
        data["reason_tags"] = reason_tags
    if edited_caption:
        data["edited_caption"] = edited_caption

    result = client.table("feedback_events").insert(data).execute()
    return result.data[0]


async def log_usage_event(
    tenant_id: str,
    event_type: str,
    provider: str,
    cost_usd: float,
    metadata: dict | None = None,
) -> None:
    """Log a usage event for cost tracking."""
    client = get_supabase_client()
    client.table("usage_events").insert({
        "tenant_id": tenant_id,
        "event_type": event_type,
        "provider": provider,
        "cost_usd": cost_usd,
        "metadata": metadata or {},
    }).execute()


async def enqueue_job(
    queue_name: str,
    job_type: str,
    payload: dict,
    idempotency_key: str | None = None,
    scheduled_for: "datetime | None" = None,
) -> dict:
    """Enqueue a job to the fallback job_queue table.

    Uses the job_queue table (not pgmq directly) for portability.
    The worker polls this table with FOR UPDATE SKIP LOCKED.
    """
    from datetime import datetime  # noqa: F401 — used in type annotation above

    client = get_supabase_client()
    data: dict = {
        "queue_name": queue_name,
        "job_type": job_type,
        "payload": payload,
        "status": "queued",
    }
    if idempotency_key:
        data["idempotency_key"] = idempotency_key
    if scheduled_for is not None:
        data["scheduled_for"] = scheduled_for.isoformat()

    result = client.table("job_queue").insert(data).execute()
    return result.data[0]


# --- Onboarding functions ---


async def create_tenant(
    name: str,
    slug: str,
    website_url: str | None = None,
) -> dict:
    """Create a new tenant. Returns the created tenant row."""
    client = get_supabase_client()
    data: dict = {"name": name, "slug": slug}
    if website_url:
        data["website_url"] = website_url
    result = client.table("tenants").insert(data).execute()
    return result.data[0]


async def create_tenant_member(
    tenant_id: str,
    telegram_user_id: int,
    role: str = "owner",
) -> dict:
    """Create a tenant membership for a Telegram user."""
    client = get_supabase_client()
    result = (
        client.table("tenant_members")
        .insert({
            "tenant_id": tenant_id,
            "telegram_user_id": telegram_user_id,
            "role": role,
            "onboarding_status": "pending",
        })
        .execute()
    )
    return result.data[0]


async def upsert_brand_profile(tenant_id: str, profile_data: dict) -> dict:
    """Insert or update a brand profile for a tenant.

    profile_data should contain keys like tone_words, audience_description,
    do_list, dont_list, product_catalog, compliance_notes, scraped_data.
    """
    client = get_supabase_client()
    data = {"tenant_id": tenant_id, **profile_data}
    result = (
        client.table("brand_profiles")
        .upsert(data, on_conflict="tenant_id")
        .execute()
    )
    return result.data[0]


async def update_onboarding_status(
    tenant_id: str,
    telegram_user_id: int,
    status: str,
) -> None:
    """Update the onboarding status for a tenant member."""
    client = get_supabase_client()
    (
        client.table("tenant_members")
        .update({"onboarding_status": status})
        .eq("tenant_id", tenant_id)
        .eq("telegram_user_id", telegram_user_id)
        .execute()
    )


async def update_tenant_website_url(tenant_id: str, website_url: str) -> None:
    """Update the website URL for a tenant."""
    client = get_supabase_client()
    client.table("tenants").update({"website_url": website_url}).eq("id", tenant_id).execute()


async def update_draft_caption(draft_id: str, option_idx: int, new_caption: str) -> None:
    """Update a single caption variant in a content draft.

    Read-modify-write: fetches caption_variants, replaces element at option_idx,
    then writes the full array back.
    """
    client = get_supabase_client()
    result = (
        client.table("content_drafts")
        .select("caption_variants")
        .eq("id", draft_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise ValueError(f"Draft {draft_id} not found")

    variants: list[dict] = result.data[0].get("caption_variants") or []

    if option_idx < 0 or option_idx >= len(variants):
        raise IndexError(
            f"option_idx {option_idx} out of range for draft with {len(variants)} variants"
        )

    updated = list(variants)
    updated[option_idx] = {**updated[option_idx], "text": new_caption}

    client.table("content_drafts").update({"caption_variants": updated}).eq(
        "id", draft_id
    ).execute()


async def get_recent_posts(tenant_id: str, limit: int = 10) -> list[dict]:
    """Get recent posted content for a tenant.

    Returns list of dicts with: draft_id, caption_preview, posted_at, platforms.
    Uses two queries (supabase-py doesn't support JOIN directly) joined in Python.
    """
    client = get_supabase_client()

    # 1. Get posted posting_jobs for this tenant
    jobs_result = (
        client.table("posting_jobs")
        .select("draft_id, platform, updated_at")
        .eq("tenant_id", tenant_id)
        .eq("status", "posted")
        .order("updated_at", desc=True)
        .execute()
    )
    jobs = jobs_result.data or []
    if not jobs:
        return []

    # Collect unique draft_ids in order, track platforms per draft
    draft_ids_seen: list[str] = []
    platforms_by_draft: dict[str, list[str]] = {}
    posted_at_by_draft: dict[str, str] = {}

    for job in jobs:
        did = job["draft_id"]
        if did not in platforms_by_draft:
            draft_ids_seen.append(did)
            platforms_by_draft[did] = []
            posted_at_by_draft[did] = job.get("updated_at", "")
        platforms_by_draft[did].append(job["platform"])

    # Apply limit on unique drafts
    draft_ids_limited = draft_ids_seen[:limit]

    # 2. Fetch corresponding content_drafts
    drafts_result = (
        client.table("content_drafts")
        .select("id, caption_variants, created_at")
        .in_("id", draft_ids_limited)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    drafts_by_id: dict[str, dict] = {d["id"]: d for d in (drafts_result.data or [])}

    # 3. Join in Python, preserving order from jobs
    output: list[dict] = []
    for draft_id in draft_ids_limited:
        draft = drafts_by_id.get(draft_id)
        if not draft:
            continue
        variants = draft.get("caption_variants") or []
        first_text = variants[0].get("text", "") if variants else ""
        caption_preview = first_text[:80] + ("..." if len(first_text) > 80 else "")
        output.append(
            {
                "draft_id": draft_id,
                "caption_preview": caption_preview,
                "posted_at": posted_at_by_draft.get(draft_id, draft.get("created_at", "")),
                "platforms": platforms_by_draft.get(draft_id, []),
            }
        )
    return output


async def create_few_shot_examples_batch(
    tenant_id: str,
    examples: list[dict],
) -> list[dict]:
    """Insert multiple few-shot examples for a tenant.

    Each example dict should have: platform, content_type, caption,
    and optionally image_url, engagement_score.
    """
    client = get_supabase_client()
    rows = [{"tenant_id": tenant_id, **ex} for ex in examples]
    result = client.table("few_shot_examples").insert(rows).execute()
    return result.data


# --- Reference photo functions ---

VALID_LABELS = {"owner", "partner", "product", "other"}
MAX_PHOTOS_PER_TENANT = 50
MAX_IMAGE_INPUTS = 14


async def create_reference_photo(
    tenant_id: str,
    uploaded_by: int,
    label: str,
    storage_path: str,
    file_unique_id: str,
    file_size_bytes: int | None = None,
    mime_type: str | None = None,
    is_default: bool = True,
) -> dict:
    """Store a reference photo for a tenant.

    Raises ValueError if label is not one of: owner, partner, product, other.
    """
    if label not in VALID_LABELS:
        raise ValueError(f"Invalid label '{label}'. Must be one of: {VALID_LABELS}")

    client = get_supabase_client()
    data: dict = {
        "tenant_id": tenant_id,
        "uploaded_by": uploaded_by,
        "label": label,
        "storage_path": storage_path,
        "file_unique_id": file_unique_id,
        "is_default": is_default,
    }
    if file_size_bytes is not None:
        data["file_size_bytes"] = file_size_bytes
    if mime_type is not None:
        data["mime_type"] = mime_type

    result = client.table("reference_photos").insert(data).execute()
    return result.data[0]


async def get_reference_photos(tenant_id: str) -> list[dict]:
    """Get all active (non-deleted) reference photos for a tenant, newest first."""
    client = get_supabase_client()
    result = (
        client.table("reference_photos")
        .select("*")
        .eq("tenant_id", tenant_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


async def get_default_reference_photos(tenant_id: str) -> list[dict]:
    """Get active default reference photos for a tenant, newest first."""
    client = get_supabase_client()
    result = (
        client.table("reference_photos")
        .select("*")
        .eq("tenant_id", tenant_id)
        .eq("is_default", True)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


async def get_reference_photo_by_id(photo_id: str, tenant_id: str) -> dict | None:
    """Get a single reference photo by ID, scoped to tenant."""
    client = get_supabase_client()
    result = (
        client.table("reference_photos")
        .select("*")
        .eq("id", photo_id)
        .eq("tenant_id", tenant_id)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    return None


async def soft_delete_reference_photo(photo_id: str, tenant_id: str) -> None:
    """Soft-delete a reference photo. Always requires tenant_id for safety."""
    from datetime import datetime

    client = get_supabase_client()
    (
        client.table("reference_photos")
        .update({"deleted_at": datetime.now(UTC).isoformat()})
        .eq("id", photo_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )


async def toggle_reference_photo_default(
    photo_id: str, tenant_id: str, is_default: bool
) -> None:
    """Set is_default on a reference photo. Scoped to tenant."""
    client = get_supabase_client()
    (
        client.table("reference_photos")
        .update({"is_default": is_default})
        .eq("id", photo_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )


async def count_reference_photos(tenant_id: str) -> int:
    """Count active (non-deleted) reference photos for a tenant."""
    client = get_supabase_client()
    result = (
        client.table("reference_photos")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .is_("deleted_at", "null")
        .execute()
    )
    return result.count or 0


# --- Posting functions ---


async def get_telegram_chat_id_for_draft(draft_id: str) -> int | None:
    """Get telegram_chat_id from approval_requests for a draft. Single-hop query."""
    client = get_supabase_client()
    result = (
        client.table("approval_requests")
        .select("telegram_chat_id")
        .eq("draft_id", draft_id)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["telegram_chat_id"]
    return None


async def update_posting_job_status(job_id: str, status: str) -> None:
    """Update the status of a posting job."""
    client = get_supabase_client()
    client.table("posting_jobs").update({"status": status}).eq("id", job_id).execute()


async def create_posting_result(
    posting_job_id: str,
    tenant_id: str,
    platform: str,
    success: bool,
    platform_post_id: str | None = None,
    platform_url: str | None = None,
    error_message: str | None = None,
) -> dict:
    """Insert a posting_results row after attempting to post to a platform."""
    client = get_supabase_client()
    data: dict = {
        "posting_job_id": posting_job_id,
        "tenant_id": tenant_id,
        "platform": platform,
        "success": success,
    }
    if platform_post_id is not None:
        data["platform_post_id"] = platform_post_id
    if platform_url is not None:
        data["platform_url"] = platform_url
    if error_message is not None:
        data["error_message"] = error_message

    result = client.table("posting_results").insert(data).execute()
    return result.data[0]
