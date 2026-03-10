"""Supabase database client — singleton for the bot and worker."""

from __future__ import annotations

from functools import lru_cache

from supabase import create_client
from supabase.client import Client

from bot.config import get_settings


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
) -> dict:
    """Create a new content request in the database."""
    client = get_supabase_client()
    result = (
        client.table("content_requests")
        .insert({
            "tenant_id": tenant_id,
            "intent": intent,
            "platform_targets": platform_targets or ["instagram"],
            "status": "pending",
        })
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
) -> dict:
    """Enqueue a job to the fallback job_queue table.

    Uses the job_queue table (not pgmq directly) for portability.
    The worker polls this table with FOR UPDATE SKIP LOCKED.
    """
    client = get_supabase_client()
    data: dict = {
        "queue_name": queue_name,
        "job_type": job_type,
        "payload": payload,
        "status": "queued",
    }
    if idempotency_key:
        data["idempotency_key"] = idempotency_key

    result = client.table("job_queue").insert(data).execute()
    return result.data[0]
