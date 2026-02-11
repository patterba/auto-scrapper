"""Scheduling logic for recurring scrapes."""

from __future__ import annotations

import logging
import time

import schedule

from scrapper.config import Settings, load_site_configs
from scrapper.scraper import scrape_site
from scrapper.storage import get_client, upsert_events

logger = logging.getLogger(__name__)


def run_all_scrapers(settings: Settings) -> int:
    """Run scrapers for all configured sites and store results.

    Returns total number of events upserted.
    """
    sites = load_site_configs()
    if not sites:
        logger.warning("No site configurations found in sites/ directory")
        return 0

    client = get_client(settings.supabase_url, settings.supabase_key)
    total = 0

    for site in sites:
        logger.info("Scraping site: %s", site.name)
        try:
            events = scrape_site(site)
            if events:
                count = upsert_events(client, events)
                total += count
        except Exception:
            logger.exception("Error scraping site: %s", site.name)

    logger.info("Scrape cycle complete. Total events upserted: %d", total)
    return total


def start_scheduler(settings: Settings) -> None:
    """Start the recurring scrape scheduler.

    Runs an immediate scrape, then schedules subsequent runs
    at the configured interval.
    """
    interval_days = settings.scrape_interval_days
    logger.info("Starting scheduler with %d-day interval", interval_days)

    # Run immediately on start
    run_all_scrapers(settings)

    # Schedule recurring runs
    schedule.every(interval_days).days.do(run_all_scrapers, settings=settings)

    logger.info("Scheduler running. Next scrape in %d days. Press Ctrl+C to stop.", interval_days)
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
