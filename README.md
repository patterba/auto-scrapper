# Auto Scrapper - Signing Event Web Scraper

A configurable Python web scraper that collects autograph signing event data from websites and stores it in Supabase. Runs on a 7-day schedule.

## Data Collected

For each signing event, the scraper extracts:

- Signer's name
- Team / franchise
- Date and time of signing
- Location
- Hosting business name
- Price
- Signer image URL
- Business contact info

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Run the migration SQL in your Supabase SQL Editor:
   - Open `supabase/migration.sql`
   - Paste and run it in Dashboard -> SQL Editor
3. Copy your project URL and API key from Settings -> API

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SCRAPE_INTERVAL_DAYS=7
```

### 4. Add site configurations

Create YAML files in the `sites/` directory for each website you want to scrape. See `sites/example_site.yaml` for the template.

Each YAML file defines:
- `base_url` - The website URL
- `pages` - List of paths to scrape
- `selectors` - CSS selectors mapping HTML elements to event fields
- `pagination` - (optional) How to follow paginated results

#### Finding CSS selectors

1. Open the target website in Chrome/Firefox
2. Right-click on a signing event element -> **Inspect**
3. Identify the repeating container (e.g., `div.event-card`)
4. Within it, find selectors for name, date, price, etc.
5. Map them in your YAML config

## Usage

```bash
# Run all scrapers once
python -m scrapper.cli run

# Start the 7-day recurring scheduler
python -m scrapper.cli schedule

# Test a scraper without saving (dry run)
python -m scrapper.cli test "Example Signing Site"

# List all configured sites
python -m scrapper.cli sites
```

## Project Structure

```
auto-scrapper/
  scrapper/
    __init__.py
    cli.py          # CLI entry point
    config.py       # Settings and YAML config loader
    models.py       # Pydantic data models
    scraper.py      # Core scraping engine
    scheduler.py    # 7-day recurring schedule
    storage.py      # Supabase integration
  sites/
    example_site.yaml   # Example site config template
  supabase/
    migration.sql       # Database table setup
  .env.example
  requirements.txt
  pyproject.toml
```

## Adding a New Site

1. Copy `sites/example_site.yaml` to `sites/your_site.yaml`
2. Update `name`, `base_url`, `pages`, and all `selectors` fields
3. Test with: `python -m scrapper.cli test "Your Site Name"`
4. Once working, events will be included in the next `run` or `schedule` cycle
