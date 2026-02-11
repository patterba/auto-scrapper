"""Supabase storage layer for scraped signing events."""

from __future__ import annotations

import logging
from datetime import datetime

from supabase import Client, create_client

from scrapper.models import SigningEvent

logger = logging.getLogger(__name__)

TABLE_NAME = "signing_events"


def get_client(url: str, key: str) -> Client:
    """Create and return a Supabase client."""
    return create_client(url, key)


def upsert_events(client: Client, events: list[SigningEvent]) -> int:
    """Insert or update signing events in Supabase.

    Uses (signer_name, date_time, source_site) as a natural dedup key.
    Returns the number of rows upserted.
    """
    if not events:
        return 0

    rows = []
    for event in events:
        rows.append(
            {
                "signer_name": event.signer_name,
                "team_or_franchise": event.team_or_franchise,
                "date_time": event.date_time,
                "location": event.location,
                "business_name": event.business_name,
                "price": event.price,
                "image_url": event.image_url,
                "contact_info": event.contact_info,
                "source_url": event.source_url,
                "source_site": event.source_site,
                "scraped_at": event.scraped_at.isoformat(),
            }
        )

    try:
        result = client.table(TABLE_NAME).upsert(
            rows,
            on_conflict="signer_name,date_time,source_site",
        ).execute()
        count = len(result.data) if result.data else 0
        logger.info("Upserted %d events to Supabase", count)
        return count
    except Exception:
        logger.exception("Failed to upsert events to Supabase")
        return 0


def get_events(
    client: Client,
    source_site: str | None = None,
    since: datetime | None = None,
) -> list[dict]:
    """Retrieve signing events from Supabase with optional filters."""
    query = client.table(TABLE_NAME).select("*")

    if source_site:
        query = query.eq("source_site", source_site)
    if since:
        query = query.gte("scraped_at", since.isoformat())

    result = query.order("scraped_at", desc=True).execute()
    return result.data or []
