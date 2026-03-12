"""Job handler — content posting via Postiz."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.db import (
    create_posting_result,
    get_supabase_client,
    get_telegram_chat_id_for_draft,
    update_posting_job_status,
)
from pipeline.posting import PostizClient

logger = logging.getLogger(__name__)


async def handle_post_content(message: dict) -> None:
    """Post approved content to target platforms via Postiz.

    Message format:
        {
            "id": "job-uuid",
            "type": "post_content",
            "tenant_id": "tenant-uuid",
            "draft_id": "draft-uuid",
            "caption": "final approved caption text",
            "image_urls": ["https://..."],
            "platform_targets": ["instagram", "facebook"] | None,
            "idempotency_key": "hash(draft_id + post_content)"
        }
    """
    job_id = message.get("job_id") or message.get("id")
    draft_id = message["draft_id"]
    tenant_id = message["tenant_id"]
    caption = message["caption"]
    image_urls = message.get("image_urls", [])

    # Read platform_targets from message (None = post to all connected)
    platform_targets: list[str] | None = message.get("platform_targets") or None

    logger.info(
        "Posting content",
        extra={"draft_id": draft_id, "platforms": platform_targets},
    )

    # 1. Idempotency check — skip if already posted
    if job_id:
        client = get_supabase_client()
        existing = (
            client.table("posting_jobs")
            .select("id, status")
            .eq("id", job_id)
            .limit(1)
            .execute()
        )
        if existing.data and existing.data[0].get("status") in ("posted", "failed", "partial"):
            logger.info(
                "Skipping duplicate post_content job — already processed",
                extra={"job_id": job_id, "draft_id": draft_id, "status": existing.data[0].get("status")},
            )
            return

    # 2. Load tenant Postiz credentials from platform_connections
    # The PostizClient already reads postiz_url / postiz_api_key from settings.
    # platform_connections stores per-tenant overrides; for now we pass platform_targets
    # to PostizClient.post() which filters connected integrations accordingly.
    # Future: load tenant-specific integration IDs from platform_connections here.

    # 3. Post via Postiz
    postiz_client = PostizClient()
    results = await postiz_client.post(
        caption=caption,
        image_urls=image_urls,
        platforms=platform_targets,
    )

    # 4. Persist results and determine final job status
    succeeded: list[str] = []
    failed: list[str] = []

    for result in results:
        logger.info(
            "Posting result",
            extra={
                "platform": result.platform,
                "success": result.success,
                "url": result.platform_url,
            },
        )

        if job_id:
            try:
                await create_posting_result(
                    posting_job_id=job_id,
                    tenant_id=tenant_id,
                    platform=result.platform,
                    success=result.success,
                    platform_post_id=result.platform_post_id,
                    platform_url=result.platform_url,
                    error_message=result.error_message,
                )
            except Exception:
                logger.exception("Failed to save posting_result — non-fatal", extra={"job_id": job_id})

        if result.success:
            succeeded.append(result.platform)
        else:
            failed.append(result.platform)

    # Determine final status
    if not results:
        final_status = "failed"
    elif not failed:
        final_status = "posted"
    elif not succeeded:
        final_status = "failed"
    else:
        final_status = "partial"

    if job_id:
        await update_posting_job_status(job_id, final_status)

    # 5. Brand voice learning — insert few_shot_example for successful posts
    if succeeded:
        try:
            _learn_client = get_supabase_client()

            # Check for duplicate caption before inserting
            dup_check = (
                _learn_client.table("few_shot_examples")
                .select("id")
                .eq("tenant_id", tenant_id)
                .eq("caption", caption)
                .limit(1)
                .execute()
            )
            if not dup_check.data:
                _learn_client.table("few_shot_examples").insert(
                    {
                        "tenant_id": tenant_id,
                        "caption": caption,
                        "platform": succeeded[0],
                        "content_type": "organic",
                        "engagement_score": 1.0,
                    }
                ).execute()

                # Trim to most recent 20 per tenant
                # Get IDs of the 20 most recent examples
                keep_result = (
                    _learn_client.table("few_shot_examples")
                    .select("id")
                    .eq("tenant_id", tenant_id)
                    .order("created_at", desc=True)
                    .limit(20)
                    .execute()
                )
                keep_ids = [row["id"] for row in (keep_result.data or [])]
                if keep_ids:
                    _learn_client.table("few_shot_examples").delete().eq(
                        "tenant_id", tenant_id
                    ).not_.in_("id", keep_ids).execute()
        except Exception:
            logger.exception(
                "Brand voice learning failed — non-fatal",
                extra={"draft_id": draft_id, "tenant_id": tenant_id},
            )

    # 6. Send Telegram confirmation
    telegram_chat_id = await get_telegram_chat_id_for_draft(draft_id)
    if telegram_chat_id:
        settings = get_settings()
        bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            if final_status == "posted":
                text = f"✅ Posted to: {', '.join(succeeded)}"
            elif final_status == "partial":
                text = (
                    f"⚠️ Partial post: {', '.join(succeeded)}. "
                    f"Failed: {', '.join(failed)}"
                )
            else:
                text = f"❌ Posting failed for: {', '.join(failed or ['all platforms'])}"

            await bot.send_message(chat_id=telegram_chat_id, text=text)
        finally:
            await bot.session.close()
    else:
        logger.warning(
            "No telegram_chat_id found for draft — skipping confirmation",
            extra={"draft_id": draft_id},
        )
