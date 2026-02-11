"""Command-line interface for the signing event scraper."""

from __future__ import annotations

import argparse
import logging
import sys

from scrapper.config import Settings, load_site_configs
from scrapper.scheduler import run_all_scrapers, start_scheduler
from scrapper.scraper import scrape_site


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_run(settings: Settings) -> None:
    """Run all scrapers once and exit."""
    total = run_all_scrapers(settings)
    print(f"Scrape complete. {total} events saved to Supabase.")


def cmd_schedule(settings: Settings) -> None:
    """Start the recurring scheduler."""
    start_scheduler(settings)


def cmd_test(args: argparse.Namespace) -> None:
    """Test scraping a site without saving to Supabase (dry run)."""
    sites = load_site_configs()
    target = args.site

    matched = [s for s in sites if s.name.lower() == target.lower()]
    if not matched:
        available = [s.name for s in sites]
        print(f"Site '{target}' not found. Available sites: {available}")
        sys.exit(1)

    site = matched[0]
    print(f"Testing scraper for: {site.name}")
    events = scrape_site(site)

    if not events:
        print("No events found.")
        return

    print(f"\nFound {len(events)} events:\n")
    for i, event in enumerate(events, 1):
        print(f"--- Event {i} ---")
        print(f"  Signer:    {event.signer_name}")
        print(f"  Team:      {event.team_or_franchise or 'N/A'}")
        print(f"  Date/Time: {event.date_time or 'N/A'}")
        print(f"  Location:  {event.location or 'N/A'}")
        print(f"  Business:  {event.business_name or 'N/A'}")
        print(f"  Price:     {event.price or 'N/A'}")
        print(f"  Image:     {event.image_url or 'N/A'}")
        print(f"  Contact:   {event.contact_info or 'N/A'}")
        print()


def cmd_list_sites() -> None:
    """List all configured sites."""
    sites = load_site_configs()
    if not sites:
        print("No sites configured. Add YAML files to the sites/ directory.")
        return

    print("Configured sites:\n")
    for site in sites:
        print(f"  - {site.name}")
        print(f"    URL: {site.base_url}")
        print(f"    Pages: {len(site.pages)}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Autograph signing event web scraper"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("run", help="Run all scrapers once")
    subparsers.add_parser("schedule", help="Start the recurring scrape scheduler")

    test_parser = subparsers.add_parser("test", help="Test a scraper (dry run)")
    test_parser.add_argument("site", help="Site name to test")

    subparsers.add_parser("sites", help="List all configured sites")

    args = parser.parse_args()

    settings = Settings()
    setup_logging(settings.log_level)

    match args.command:
        case "run":
            cmd_run(settings)
        case "schedule":
            cmd_schedule(settings)
        case "test":
            cmd_test(args)
        case "sites":
            cmd_list_sites()
        case _:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
