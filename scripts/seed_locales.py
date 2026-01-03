#!/usr/bin/env python3
"""Seed locales collection with initial data.

This script populates the Firestore 'locales' collection with the
initial locale configurations that were previously hardcoded.

Usage:
    python scripts/seed_locales.py

Environment:
    Uses Application Default Credentials (ADC) for authentication.
    Run `gcloud auth application-default login` if needed.
"""

import sys
from datetime import datetime, timezone

from google.cloud import firestore


# Database name (named database to avoid conflicts with Datastore Mode)
DATABASE_NAME = "earthquake-alerts"

# Collection name
COLLECTION_NAME = "locales"

# Initial locale configurations (matches api/main.py)
INITIAL_LOCALES = [
    {
        "slug": "sanramon",
        "name": "San Ramon",
        "display_name": "San Ramon, CA",
        "bounds": {
            "min_latitude": 37.3,
            "max_latitude": 38.3,
            "min_longitude": -122.5,
            "max_longitude": -121.5,
        },
        "center": {"lat": 37.78, "lng": -121.98},
        "min_magnitude": 2.5,
        "is_active": True,
        "is_featured": True,
        "sort_order": 1,
    },
    {
        "slug": "bayarea",
        "name": "Bay Area",
        "display_name": "San Francisco Bay Area",
        "bounds": {
            "min_latitude": 37.0,
            "max_latitude": 38.5,
            "min_longitude": -123.0,
            "max_longitude": -121.5,
        },
        "center": {"lat": 37.77, "lng": -122.42},
        "min_magnitude": 2.5,
        "is_active": True,
        "is_featured": True,
        "sort_order": 2,
    },
    {
        "slug": "la",
        "name": "Los Angeles",
        "display_name": "Los Angeles, CA",
        "bounds": {
            "min_latitude": 33.5,
            "max_latitude": 34.8,
            "min_longitude": -119.0,
            "max_longitude": -117.0,
        },
        "center": {"lat": 34.05, "lng": -118.24},
        "min_magnitude": 2.5,
        "is_active": True,
        "is_featured": True,
        "sort_order": 3,
    },
]


def seed_locales(dry_run: bool = False) -> None:
    """Seed the locales collection with initial data.

    Args:
        dry_run: If True, print what would be done without writing
    """
    print(f"Connecting to Firestore database: {DATABASE_NAME}")

    if dry_run:
        print("[DRY RUN] Would seed the following locales:")
        for locale in INITIAL_LOCALES:
            print(f"  - {locale['slug']}: {locale['display_name']}")
        return

    client = firestore.Client(database=DATABASE_NAME)
    now = datetime.now(timezone.utc)

    print(f"Seeding {len(INITIAL_LOCALES)} locales...")

    for locale in INITIAL_LOCALES:
        slug = locale["slug"]
        doc_ref = client.collection(COLLECTION_NAME).document(slug)

        # Check if document already exists
        if doc_ref.get().exists:
            print(f"  [SKIP] {slug} already exists")
            continue

        # Add timestamps
        doc_data = {
            **locale,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref.set(doc_data)
        print(f"  [OK] Created {slug}")

    print("\nDone! Verifying...")

    # Verify by reading back
    docs = client.collection(COLLECTION_NAME).stream()
    count = 0
    for doc in docs:
        data = doc.to_dict()
        print(f"  - {doc.id}: {data.get('display_name', 'N/A')}")
        count += 1

    print(f"\nTotal locales in collection: {count}")


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed Firestore locales collection with initial data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without writing",
    )

    args = parser.parse_args()

    try:
        seed_locales(dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
