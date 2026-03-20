"""Tests for the asset resolver module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from pipeline.prompt_engine.asset_resolver import (
    MAX_PEOPLE_PHOTOS,
    MAX_PRODUCT_PHOTOS,
    AssetManifest,
    resolve_assets,
)


TENANT_ID = "test-tenant-id"


class TestAssetManifest:
    def test_instantiation(self) -> None:
        m = AssetManifest(
            product_photos=["https://a.com/1.jpg"],
            people_photos=["https://a.com/2.jpg"],
            other_photos=[],
            logo_url="https://a.com/logo.png",
        )
        assert len(m.product_photos) == 1
        assert m.logo_url is not None

    def test_defaults(self) -> None:
        m = AssetManifest(product_photos=[], people_photos=[], other_photos=[])
        assert m.logo_url is None

    def test_all_urls(self) -> None:
        m = AssetManifest(
            product_photos=["a", "b"],
            people_photos=["c"],
            other_photos=["d"],
        )
        assert m.all_urls == ["a", "b", "c", "d"]

    def test_total_count(self) -> None:
        m = AssetManifest(
            product_photos=["a", "b"],
            people_photos=["c"],
            other_photos=[],
        )
        assert m.total_count == 3

    def test_caps(self) -> None:
        assert MAX_PRODUCT_PHOTOS == 10
        assert MAX_PEOPLE_PHOTOS == 4


class TestResolveAssets:
    @pytest.mark.asyncio
    async def test_groups_by_label(self) -> None:
        """Photos with label=product go to product_photos, label=owner to people_photos."""
        mock_photos = [
            {"storage_path": "photos/product1.jpg", "label": "product"},
            {"storage_path": "photos/product2.jpg", "label": "product"},
            {"storage_path": "photos/owner1.jpg", "label": "owner"},
            {"storage_path": "photos/other1.jpg", "label": "other"},
        ]

        with (
            patch("pipeline.prompt_engine.asset_resolver.get_reference_photos",
                  new_callable=AsyncMock, return_value=mock_photos),
            patch("pipeline.prompt_engine.asset_resolver.get_signed_urls_for_generation",
                  side_effect=lambda paths: [f"https://signed/{p}" for p in paths]),
            patch("pipeline.prompt_engine.asset_resolver._load_logo",
                  new_callable=AsyncMock, return_value=(None, None)),
        ):
            manifest = await resolve_assets(TENANT_ID)

        assert len(manifest.product_photos) == 2
        assert len(manifest.people_photos) == 1
        assert len(manifest.other_photos) == 1

    @pytest.mark.asyncio
    async def test_includes_new_photos(self) -> None:
        """New photo paths are added to the manifest as product photos."""
        with (
            patch("pipeline.prompt_engine.asset_resolver.get_reference_photos",
                  new_callable=AsyncMock, return_value=[]),
            patch("pipeline.prompt_engine.asset_resolver.get_signed_urls_for_generation",
                  side_effect=lambda paths: [f"https://signed/{p}" for p in paths]),
            patch("pipeline.prompt_engine.asset_resolver._load_logo",
                  new_callable=AsyncMock, return_value=(None, None)),
        ):
            manifest = await resolve_assets(
                TENANT_ID,
                new_photo_paths=["photos/new1.jpg", "photos/new2.jpg"],
            )

        assert len(manifest.product_photos) == 2
        assert all("new" in u for u in manifest.product_photos)

    @pytest.mark.asyncio
    async def test_product_photos_capped(self) -> None:
        """Product photos are capped at MAX_PRODUCT_PHOTOS."""
        mock_photos = [
            {"storage_path": f"photos/p{i}.jpg", "label": "product"}
            for i in range(15)
        ]

        with (
            patch("pipeline.prompt_engine.asset_resolver.get_reference_photos",
                  new_callable=AsyncMock, return_value=mock_photos),
            patch("pipeline.prompt_engine.asset_resolver.get_signed_urls_for_generation",
                  side_effect=lambda paths: [f"https://signed/{p}" for p in paths]),
            patch("pipeline.prompt_engine.asset_resolver._load_logo",
                  new_callable=AsyncMock, return_value=(None, None)),
        ):
            manifest = await resolve_assets(TENANT_ID)

        assert len(manifest.product_photos) == MAX_PRODUCT_PHOTOS

    @pytest.mark.asyncio
    async def test_people_photos_capped(self) -> None:
        """People photos are capped at MAX_PEOPLE_PHOTOS."""
        mock_photos = [
            {"storage_path": f"photos/o{i}.jpg", "label": "owner"}
            for i in range(8)
        ]

        with (
            patch("pipeline.prompt_engine.asset_resolver.get_reference_photos",
                  new_callable=AsyncMock, return_value=mock_photos),
            patch("pipeline.prompt_engine.asset_resolver.get_signed_urls_for_generation",
                  side_effect=lambda paths: [f"https://signed/{p}" for p in paths]),
            patch("pipeline.prompt_engine.asset_resolver._load_logo",
                  new_callable=AsyncMock, return_value=(None, None)),
        ):
            manifest = await resolve_assets(TENANT_ID)

        assert len(manifest.people_photos) == MAX_PEOPLE_PHOTOS

    @pytest.mark.asyncio
    async def test_logo_url_loaded(self) -> None:
        with (
            patch("pipeline.prompt_engine.asset_resolver.get_reference_photos",
                  new_callable=AsyncMock, return_value=[]),
            patch("pipeline.prompt_engine.asset_resolver.get_signed_urls_for_generation",
                  side_effect=lambda paths: [f"https://signed/{p}" for p in paths]),
            patch("pipeline.prompt_engine.asset_resolver._load_logo",
                  new_callable=AsyncMock, return_value=("https://signed/logo.png", "square")),
        ):
            manifest = await resolve_assets(TENANT_ID)

        assert manifest.logo_url == "https://signed/logo.png"

    @pytest.mark.asyncio
    async def test_empty_tenant(self) -> None:
        """Tenant with no photos returns empty manifest."""
        with (
            patch("pipeline.prompt_engine.asset_resolver.get_reference_photos",
                  new_callable=AsyncMock, return_value=[]),
            patch("pipeline.prompt_engine.asset_resolver.get_signed_urls_for_generation",
                  side_effect=lambda paths: [f"https://signed/{p}" for p in paths]),
            patch("pipeline.prompt_engine.asset_resolver._load_logo",
                  new_callable=AsyncMock, return_value=(None, None)),
        ):
            manifest = await resolve_assets(TENANT_ID)

        assert manifest.total_count == 0
        assert manifest.logo_url is None
