"""Core scraping engine."""

from __future__ import annotations

import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from scrapper.models import PaginationConfig, SigningEvent, SiteConfig, SiteSelectors

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def scrape_site(site: SiteConfig) -> list[SigningEvent]:
    """Scrape all signing events from a configured site."""
    events: list[SigningEvent] = []
    headers = {**DEFAULT_HEADERS, **site.headers}

    for path in site.pages:
        url = urljoin(site.base_url, path)
        page_events = _scrape_url(url, site, headers)
        events.extend(page_events)

    logger.info("Scraped %d events from %s", len(events), site.name)
    return events


def _scrape_url(
    url: str,
    site: SiteConfig,
    headers: dict[str, str],
) -> list[SigningEvent]:
    """Scrape events from a single URL, following pagination if configured."""
    all_events: list[SigningEvent] = []
    current_url: str | None = url
    pages_scraped = 0
    max_pages = site.pagination.max_pages if site.pagination else 1

    while current_url and pages_scraped < max_pages:
        logger.debug("Fetching: %s", current_url)
        try:
            response = requests.get(current_url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Failed to fetch %s", current_url)
            break

        soup = BeautifulSoup(response.text, "lxml")
        events = _extract_events(soup, site.selectors, current_url, site.name)
        all_events.extend(events)
        pages_scraped += 1

        current_url = _get_next_page_url(soup, current_url, site.pagination)

    return all_events


def _extract_events(
    soup: BeautifulSoup,
    selectors: SiteSelectors,
    source_url: str,
    source_site: str,
) -> list[SigningEvent]:
    """Extract signing events from a parsed HTML page."""
    events: list[SigningEvent] = []
    containers = soup.select(selectors.event_container)

    if not containers:
        logger.warning(
            "No event containers found with selector '%s' on %s",
            selectors.event_container,
            source_url,
        )
        return events

    for container in containers:
        try:
            event = _parse_event(container, selectors, source_url, source_site)
            if event:
                events.append(event)
        except Exception:
            logger.exception("Failed to parse event from %s", source_url)

    return events


def _parse_event(
    container: Tag,
    selectors: SiteSelectors,
    source_url: str,
    source_site: str,
) -> SigningEvent | None:
    """Parse a single event from an HTML container element."""
    signer_name = _get_text(container, selectors.signer_name)
    if not signer_name:
        return None

    image_url = None
    if selectors.image_url:
        img = container.select_one(selectors.image_url)
        if img:
            image_url = img.get("src") or img.get("data-src")
            if image_url and not str(image_url).startswith("http"):
                image_url = urljoin(source_url, str(image_url))

    return SigningEvent(
        signer_name=signer_name,
        team_or_franchise=_get_text(container, selectors.team_or_franchise),
        date_time=_get_text(container, selectors.date_time),
        location=_get_text(container, selectors.location),
        business_name=_get_text(container, selectors.business_name),
        price=_get_text(container, selectors.price),
        image_url=str(image_url) if image_url else None,
        contact_info=_get_text(container, selectors.contact_info),
        source_url=source_url,
        source_site=source_site,
    )


def _get_text(container: Tag, selector: str | None) -> str | None:
    """Extract cleaned text from an element matching the selector."""
    if not selector:
        return None
    el = container.select_one(selector)
    if el is None:
        return None
    text = el.get_text(strip=True)
    return text if text else None


def _get_next_page_url(
    soup: BeautifulSoup,
    current_url: str,
    pagination: PaginationConfig | None,
) -> str | None:
    """Determine the next page URL based on pagination config."""
    if not pagination or not pagination.next_page_selector:
        return None

    next_link = soup.select_one(pagination.next_page_selector)
    if not next_link:
        return None

    href = next_link.get("href")
    if not href:
        return None

    return urljoin(current_url, str(href))
