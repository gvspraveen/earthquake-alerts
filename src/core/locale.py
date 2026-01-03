"""Locale models and validation - Pure functions (Functional Core).

This module defines locale configuration data models and validation logic.
All functions are pure with no side effects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.core.geo import BoundingBox


@dataclass(frozen=True)
class Locale:
    """Immutable locale configuration.

    Attributes:
        slug: URL-friendly identifier (e.g., "sanramon", "bayarea")
        name: Short name (e.g., "San Ramon")
        display_name: Full display name (e.g., "San Ramon, CA")
        bounds: Geographic bounding box for earthquake queries
        center_lat: Map center latitude
        center_lng: Map center longitude
        min_magnitude: Minimum magnitude threshold for this locale
        is_active: Whether locale is enabled (for soft delete)
        is_featured: Whether to show in main navigation
        sort_order: Display ordering (lower = first)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    slug: str
    name: str
    display_name: str
    bounds: BoundingBox
    center_lat: float
    center_lng: float
    min_magnitude: float = 2.5
    is_active: bool = True
    is_featured: bool = True
    sort_order: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


def validate_locale(locale: Locale) -> list[str]:
    """Validate locale configuration.

    Pure function.

    Args:
        locale: Locale to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Slug validation
    if not locale.slug:
        errors.append("Slug is required")
    elif not locale.slug.replace("-", "").replace("_", "").isalnum():
        errors.append("Slug must be alphanumeric (hyphens and underscores allowed)")
    elif len(locale.slug) > 50:
        errors.append("Slug must be 50 characters or less")

    # Name validation
    if not locale.name:
        errors.append("Name is required")
    elif len(locale.name) > 100:
        errors.append("Name must be 100 characters or less")

    if not locale.display_name:
        errors.append("Display name is required")
    elif len(locale.display_name) > 200:
        errors.append("Display name must be 200 characters or less")

    # Bounds validation
    if not (-90 <= locale.bounds.min_latitude <= 90):
        errors.append("min_latitude must be between -90 and 90")
    if not (-90 <= locale.bounds.max_latitude <= 90):
        errors.append("max_latitude must be between -90 and 90")
    if locale.bounds.min_latitude >= locale.bounds.max_latitude:
        errors.append("min_latitude must be less than max_latitude")

    if not (-180 <= locale.bounds.min_longitude <= 180):
        errors.append("min_longitude must be between -180 and 180")
    if not (-180 <= locale.bounds.max_longitude <= 180):
        errors.append("max_longitude must be between -180 and 180")
    if locale.bounds.min_longitude >= locale.bounds.max_longitude:
        errors.append("min_longitude must be less than max_longitude")

    # Center validation
    if not locale.bounds.contains(locale.center_lat, locale.center_lng):
        errors.append("Center point must be within bounds")

    # Magnitude validation
    if not (0 <= locale.min_magnitude <= 10):
        errors.append("min_magnitude must be between 0 and 10")

    return errors


def locale_to_dict(locale: Locale) -> dict[str, Any]:
    """Convert Locale to API response dict.

    Pure function.

    Args:
        locale: Locale to convert

    Returns:
        Dictionary suitable for JSON serialization
    """
    return {
        "slug": locale.slug,
        "name": locale.name,
        "display_name": locale.display_name,
        "bounds": {
            "min_latitude": locale.bounds.min_latitude,
            "max_latitude": locale.bounds.max_latitude,
            "min_longitude": locale.bounds.min_longitude,
            "max_longitude": locale.bounds.max_longitude,
        },
        "center": {"lat": locale.center_lat, "lng": locale.center_lng},
        "min_magnitude": locale.min_magnitude,
    }


def locale_to_firestore_dict(locale: Locale) -> dict[str, Any]:
    """Convert Locale to Firestore document dict.

    Pure function. Includes all fields for storage.

    Args:
        locale: Locale to convert

    Returns:
        Dictionary for Firestore storage
    """
    return {
        "slug": locale.slug,
        "name": locale.name,
        "display_name": locale.display_name,
        "bounds": {
            "min_latitude": locale.bounds.min_latitude,
            "max_latitude": locale.bounds.max_latitude,
            "min_longitude": locale.bounds.min_longitude,
            "max_longitude": locale.bounds.max_longitude,
        },
        "center": {"lat": locale.center_lat, "lng": locale.center_lng},
        "min_magnitude": locale.min_magnitude,
        "is_active": locale.is_active,
        "is_featured": locale.is_featured,
        "sort_order": locale.sort_order,
        "created_at": locale.created_at,
        "updated_at": locale.updated_at,
    }


def locale_from_dict(data: dict[str, Any]) -> Locale:
    """Create Locale from Firestore document dict.

    Pure function.

    Args:
        data: Dictionary from Firestore document

    Returns:
        Locale instance
    """
    bounds_data = data.get("bounds", {})
    center_data = data.get("center", {})

    return Locale(
        slug=data["slug"],
        name=data["name"],
        display_name=data["display_name"],
        bounds=BoundingBox(
            min_latitude=bounds_data["min_latitude"],
            max_latitude=bounds_data["max_latitude"],
            min_longitude=bounds_data["min_longitude"],
            max_longitude=bounds_data["max_longitude"],
        ),
        center_lat=center_data["lat"],
        center_lng=center_data["lng"],
        min_magnitude=data.get("min_magnitude", 2.5),
        is_active=data.get("is_active", True),
        is_featured=data.get("is_featured", True),
        sort_order=data.get("sort_order", 0),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )
