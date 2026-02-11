"""Application configuration and settings."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings

from scrapper.models import SiteConfig

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent / "sites"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    supabase_url: str = ""
    supabase_key: str = ""
    scrape_interval_days: int = 7
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def load_site_configs(config_dir: Path | None = None) -> list[SiteConfig]:
    """Load all site configurations from YAML files in the sites/ directory."""
    directory = config_dir or CONFIG_DIR
    configs: list[SiteConfig] = []

    if not directory.exists():
        logger.warning("Sites config directory not found: %s", directory)
        return configs

    for yaml_file in sorted(directory.glob("*.yaml")):
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data:
                config = SiteConfig(**data)
                configs.append(config)
                logger.info("Loaded site config: %s from %s", config.name, yaml_file.name)
        except Exception:
            logger.exception("Failed to load site config from %s", yaml_file)

    return configs
