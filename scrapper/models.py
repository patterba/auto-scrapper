"""Data models for signing events."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SigningEvent(BaseModel):
    """Represents a single autograph signing event."""

    signer_name: str = Field(description="Name of the person signing autographs")
    team_or_franchise: str | None = Field(
        default=None, description="Team or franchise the signer is associated with"
    )
    date_time: str | None = Field(
        default=None, description="Date and time of the signing event"
    )
    location: str | None = Field(
        default=None, description="Physical location of the signing"
    )
    business_name: str | None = Field(
        default=None, description="Business or company hosting the signing event"
    )
    price: str | None = Field(
        default=None, description="Price of the signing (e.g., '$50', 'Free')"
    )
    image_url: str | None = Field(
        default=None, description="URL of the signer's image"
    )
    contact_info: str | None = Field(
        default=None,
        description="Contact information for the hosting business (phone, email, etc.)",
    )
    source_url: str = Field(description="URL the event was scraped from")
    source_site: str = Field(description="Name/identifier of the source website")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class SiteConfig(BaseModel):
    """Configuration for scraping a specific website."""

    name: str = Field(description="Human-readable name for this site")
    base_url: str = Field(description="Base URL to scrape")
    pages: list[str] = Field(
        default_factory=lambda: [""],
        description="List of URL paths to scrape (appended to base_url)",
    )
    selectors: SiteSelectors = Field(description="CSS selectors for extracting data")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Custom HTTP headers for requests"
    )
    pagination: PaginationConfig | None = Field(
        default=None, description="Pagination configuration"
    )


class SiteSelectors(BaseModel):
    """CSS selectors for extracting signing event data from a page."""

    event_container: str = Field(
        description="Selector for each event block/card on the page"
    )
    signer_name: str = Field(description="Selector for signer's name within container")
    team_or_franchise: str | None = Field(
        default=None, description="Selector for team/franchise"
    )
    date_time: str | None = Field(default=None, description="Selector for date/time")
    location: str | None = Field(default=None, description="Selector for location")
    business_name: str | None = Field(
        default=None, description="Selector for business name"
    )
    price: str | None = Field(default=None, description="Selector for price")
    image_url: str | None = Field(
        default=None, description="Selector for image (extracts src attribute)"
    )
    contact_info: str | None = Field(
        default=None, description="Selector for contact info"
    )
    detail_link: str | None = Field(
        default=None,
        description="Selector for link to detail page (extracts href attribute)",
    )


class PaginationConfig(BaseModel):
    """Configuration for handling paginated content."""

    next_page_selector: str | None = Field(
        default=None, description="CSS selector for the 'next page' link"
    )
    max_pages: int = Field(default=10, description="Maximum number of pages to scrape")
    page_param: str | None = Field(
        default=None,
        description="URL query parameter for page number (e.g., 'page')",
    )
