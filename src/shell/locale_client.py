"""Locale Client - Imperative Shell.

This module handles persistence of locale configurations to Firestore.
Includes in-memory caching to minimize database reads.

All I/O is contained here; locale models and validation are in the core module.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from google.cloud import firestore

from src.core.geo import BoundingBox
from src.core.locale import Locale, locale_from_dict, locale_to_firestore_dict


logger = logging.getLogger(__name__)


# Default collection name for storing locales
LOCALES_COLLECTION = "locales"

# Default cache TTL in seconds (5 minutes)
DEFAULT_CACHE_TTL_SECONDS = 300


@dataclass
class LocaleClientConfig:
    """Configuration for LocaleClient.

    Attributes:
        project_id: GCP project ID (None for default)
        database: Firestore database name (None for default database)
        cache_ttl_seconds: How long to cache locale data
    """

    project_id: str | None = None
    database: str | None = None
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS


class LocaleClient:
    """Client for managing locale configurations in Firestore.

    This is part of the imperative shell - it handles database I/O.
    Includes in-memory caching to reduce Firestore reads.

    Document structure (locales/{slug}):
    {
        "slug": "sanramon",
        "name": "San Ramon",
        "display_name": "San Ramon, CA",
        "bounds": {
            "min_latitude": 37.3,
            "max_latitude": 38.3,
            "min_longitude": -122.5,
            "max_longitude": -121.5
        },
        "center": {"lat": 37.78, "lng": -121.98},
        "min_magnitude": 2.5,
        "is_active": true,
        "is_featured": true,
        "sort_order": 1,
        "created_at": <timestamp>,
        "updated_at": <timestamp>
    }
    """

    def __init__(self, config: LocaleClientConfig | None = None) -> None:
        """Initialize LocaleClient.

        Args:
            config: Client configuration
        """
        self.config = config or LocaleClientConfig()
        self._client: firestore.Client | None = None
        self._cache: dict[str, Locale] = {}
        self._cache_timestamp: float = 0

    @property
    def client(self) -> firestore.Client:
        """Lazy initialization of Firestore client."""
        if self._client is None:
            kwargs = {}
            if self.config.project_id:
                kwargs["project"] = self.config.project_id
            if self.config.database:
                kwargs["database"] = self.config.database
            self._client = firestore.Client(**kwargs)
        return self._client

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._cache:
            return False
        elapsed = time.time() - self._cache_timestamp
        return elapsed < self.config.cache_ttl_seconds

    def _refresh_cache(self) -> None:
        """Refresh the locale cache from Firestore."""
        logger.info("Refreshing locale cache from Firestore")

        try:
            docs = self.client.collection(LOCALES_COLLECTION).stream()
            self._cache = {}

            for doc in docs:
                data = doc.to_dict()
                if data:
                    try:
                        locale = locale_from_dict(data)
                        self._cache[locale.slug] = locale
                    except (KeyError, TypeError) as e:
                        logger.warning("Skipping invalid locale document %s: %s", doc.id, e)

            self._cache_timestamp = time.time()
            logger.info("Loaded %d locales into cache", len(self._cache))

        except Exception as e:
            logger.error("Failed to refresh locale cache: %s", e)
            # Keep stale cache if available - better than nothing

    def invalidate_cache(self) -> None:
        """Force cache invalidation.

        Call this after create/update/delete operations.
        """
        self._cache_timestamp = 0
        logger.debug("Locale cache invalidated")

    def get_all_locales(
        self,
        active_only: bool = True,
        featured_only: bool = False,
    ) -> list[Locale]:
        """Get all locales, optionally filtered.

        Uses cached data if available and valid.

        Args:
            active_only: Only return active locales (default True)
            featured_only: Only return featured locales (default False)

        Returns:
            List of Locale objects, sorted by sort_order then name
        """
        if not self._is_cache_valid():
            self._refresh_cache()

        locales = list(self._cache.values())

        if active_only:
            locales = [loc for loc in locales if loc.is_active]
        if featured_only:
            locales = [loc for loc in locales if loc.is_featured]

        # Sort by sort_order, then by name
        locales.sort(key=lambda loc: (loc.sort_order, loc.name))

        return locales

    def get_locale(self, slug: str) -> Locale | None:
        """Get a single locale by slug.

        Uses cached data if available and valid.

        Args:
            slug: Locale slug to look up

        Returns:
            Locale if found, None otherwise
        """
        if not self._is_cache_valid():
            self._refresh_cache()

        return self._cache.get(slug)

    # ===== Admin Methods (no caching, always fresh) =====

    def get_all_locales_admin(self) -> list[Locale]:
        """Get all locales for admin view (including inactive).

        Always fetches fresh data from Firestore.

        Returns:
            List of all Locale objects
        """
        logger.info("Admin: Fetching all locales from Firestore")

        try:
            docs = self.client.collection(LOCALES_COLLECTION).stream()
            locales = []

            for doc in docs:
                data = doc.to_dict()
                if data:
                    try:
                        locales.append(locale_from_dict(data))
                    except (KeyError, TypeError) as e:
                        logger.warning("Skipping invalid locale document %s: %s", doc.id, e)

            locales.sort(key=lambda loc: (loc.sort_order, loc.name))
            return locales

        except Exception as e:
            logger.error("Failed to fetch locales for admin: %s", e)
            return []

    def create_locale(self, locale: Locale) -> tuple[bool, str]:
        """Create a new locale.

        Args:
            locale: Locale to create

        Returns:
            Tuple of (success, message)
        """
        logger.info("Creating locale: %s", locale.slug)

        try:
            doc_ref = self.client.collection(LOCALES_COLLECTION).document(locale.slug)

            if doc_ref.get().exists:
                logger.error("Locale %s already exists", locale.slug)
                return False, f"Locale '{locale.slug}' already exists"

            now = datetime.now(timezone.utc)
            data = locale_to_firestore_dict(locale)
            data["created_at"] = now
            data["updated_at"] = now

            doc_ref.set(data)
            self.invalidate_cache()

            logger.info("Created locale: %s", locale.slug)
            return True, f"Locale '{locale.slug}' created successfully"

        except Exception as e:
            logger.error("Failed to create locale %s: %s", locale.slug, e)
            return False, f"Failed to create locale: {str(e)}"

    def update_locale(self, slug: str, updates: dict[str, Any]) -> tuple[bool, str]:
        """Update an existing locale.

        Args:
            slug: Locale slug to update
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success, message)
        """
        logger.info("Updating locale: %s", slug)

        try:
            doc_ref = self.client.collection(LOCALES_COLLECTION).document(slug)

            if not doc_ref.get().exists:
                logger.error("Locale %s not found", slug)
                return False, f"Locale '{slug}' not found"

            updates["updated_at"] = datetime.now(timezone.utc)
            doc_ref.update(updates)
            self.invalidate_cache()

            logger.info("Updated locale: %s", slug)
            return True, f"Locale '{slug}' updated successfully"

        except Exception as e:
            logger.error("Failed to update locale %s: %s", slug, e)
            return False, f"Failed to update locale: {str(e)}"

    def delete_locale(self, slug: str, hard_delete: bool = False) -> tuple[bool, str]:
        """Delete a locale.

        Args:
            slug: Locale slug to delete
            hard_delete: If True, permanently delete. If False, soft delete (set is_active=False)

        Returns:
            Tuple of (success, message)
        """
        logger.info("Deleting locale: %s (hard=%s)", slug, hard_delete)

        try:
            doc_ref = self.client.collection(LOCALES_COLLECTION).document(slug)

            if not doc_ref.get().exists:
                logger.error("Locale %s not found", slug)
                return False, f"Locale '{slug}' not found"

            if hard_delete:
                doc_ref.delete()
                action = "deleted permanently"
            else:
                doc_ref.update({
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc),
                })
                action = "deactivated"

            self.invalidate_cache()

            logger.info("Deleted locale: %s (%s)", slug, action)
            return True, f"Locale '{slug}' {action}"

        except Exception as e:
            logger.error("Failed to delete locale %s: %s", slug, e)
            return False, f"Failed to delete locale: {str(e)}"

    def restore_locale(self, slug: str) -> tuple[bool, str]:
        """Restore a soft-deleted locale.

        Args:
            slug: Locale slug to restore

        Returns:
            Tuple of (success, message)
        """
        logger.info("Restoring locale: %s", slug)

        try:
            doc_ref = self.client.collection(LOCALES_COLLECTION).document(slug)
            doc = doc_ref.get()

            if not doc.exists:
                logger.error("Locale %s not found", slug)
                return False, f"Locale '{slug}' not found"

            doc_ref.update({
                "is_active": True,
                "updated_at": datetime.now(timezone.utc),
            })
            self.invalidate_cache()

            logger.info("Restored locale: %s", slug)
            return True, f"Locale '{slug}' restored successfully"

        except Exception as e:
            logger.error("Failed to restore locale %s: %s", slug, e)
            return False, f"Failed to restore locale: {str(e)}"
