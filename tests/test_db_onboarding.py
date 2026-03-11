"""Tests for onboarding-related DB functions in bot.db module."""

from __future__ import annotations

import asyncio

from bot.db import (
    create_few_shot_examples_batch,
    create_tenant,
    create_tenant_member,
    update_onboarding_status,
    update_tenant_website_url,
    upsert_brand_profile,
)


class TestOnboardingFunctionSignatures:
    """Verify new onboarding db functions exist and are async."""

    def test_create_tenant_is_async(self):
        assert asyncio.iscoroutinefunction(create_tenant)

    def test_create_tenant_member_is_async(self):
        assert asyncio.iscoroutinefunction(create_tenant_member)

    def test_upsert_brand_profile_is_async(self):
        assert asyncio.iscoroutinefunction(upsert_brand_profile)

    def test_create_few_shot_examples_batch_is_async(self):
        assert asyncio.iscoroutinefunction(create_few_shot_examples_batch)

    def test_update_onboarding_status_is_async(self):
        assert asyncio.iscoroutinefunction(update_onboarding_status)

    def test_update_tenant_website_url_is_async(self):
        assert asyncio.iscoroutinefunction(update_tenant_website_url)


class TestCreateTenantSignature:
    """Verify create_tenant accepts the right parameters."""

    def test_accepts_name_and_slug(self):
        import inspect
        sig = inspect.signature(create_tenant)
        params = list(sig.parameters.keys())
        assert "name" in params
        assert "slug" in params

    def test_accepts_optional_website_url(self):
        import inspect
        sig = inspect.signature(create_tenant)
        param = sig.parameters.get("website_url")
        assert param is not None
        assert param.default is None


class TestCreateTenantMemberSignature:
    def test_accepts_required_params(self):
        import inspect
        sig = inspect.signature(create_tenant_member)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params
        assert "telegram_user_id" in params
        assert "role" in params


class TestUpsertBrandProfileSignature:
    def test_accepts_tenant_id_and_profile_data(self):
        import inspect
        sig = inspect.signature(upsert_brand_profile)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params
        assert "profile_data" in params


class TestUpdateOnboardingStatusSignature:
    def test_accepts_tenant_id_and_status(self):
        import inspect
        sig = inspect.signature(update_onboarding_status)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params
        assert "telegram_user_id" in params
        assert "status" in params


class TestCreateFewShotExamplesBatchSignature:
    def test_accepts_tenant_id_and_examples(self):
        import inspect
        sig = inspect.signature(create_few_shot_examples_batch)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params
        assert "examples" in params
