# Ekantipur News Scraper

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-green)
![uv](https://img.shields.io/badge/uv-Package_Manager-orange)

A professional browser automation script using Python and Playwright to extract structured data from [Ekantipur.com](https://ekantipur.com), a prominent Nepali news website. This project was developed as a practical test for the **Web Scraping Intern** position at Audio Bee.

## Features

This project implements two specific data extraction tasks:

### Task 1: Entertainment News Extraction
- Navigates to the [Entertainment Section (मनोरञ्जन)](https://ekantipur.com/entertainment).
- Extracts the top 5 news articles, capturing:
  - `title`: Headline of the article.
  - `image_url`: Full URL of the thumbnail image.
  - `category`: Section label (defaults to "मनोरञ्जन" for this section).
  - `author`: Author name (or `null` if not found).
- **Technical Highlight**: Implements auto-scrolling to trigger and capture lazy-loaded images below the fold, ensuring complete data extraction.

### Task 2: Cartoon of the Day Extraction
- Navigates to the Ekantipur Homepage.
- Locates the **"Cartoon of the Day" (व्यंग्यचित्र)** within a Swiper carousel.
- Extracts:
  - `title`: The cartoon's title/caption from the image metadata.
  - `image_url`: Direct URL to the cartoon image.
  - `author`: The cartoonist's name, accurately parsed from the description text using regular expressions.

## Project Structure

```text
ekantipur-scraper/
├── pyproject.toml    # Project dependencies managed by uv
├── uv.lock           # Dependency lock file
├── scraper.py        # Main Playwright automation script
├── prompts.txt       # AI prompts used during development
├── output.json       # Generated output containing scraped data
└── README.md         # Project documentation
```

## Setup & Installation

The project uses `uv` as an extremely fast Python package and project manager.

**1. Install `uv`**

macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone the Repository & Install Dependencies**
```bash
git clone https://github.com/Abdurrehman510/ekantipur-scraper.git
cd ekantipur-scraper
uv sync
```

**3. Install Playwright Browsers**
```bash
uv run playwright install chromium
```

## Usage

To execute the scraper and generate the `output.json` file:

```bash
uv run python scraper.py
```

The script will launch a visible Chromium browser (helpful for debugging and visually verifying actions), perform the extractions, print the results to the console, and save them to `output.json` with proper UTF-8 encoding to preserve Devanagari characters.

## Technical Considerations

- **Robust Waits**: Uses `networkidle` and explicit element waits (`wait_for_selector`) to handle dynamic content loading gracefully.
- **Error Handling**: Implements `try-except` blocks around element extraction to prevent a failure in one article from crashing the entire process.
- **Data Integrity**: Uses `ensure_ascii=False` when saving JSON to properly support Nepali (Devanagari) characters.
- **Lazy Loading Strategy**: Evaluates JavaScript to physically scroll the page, ensuring images deferred by lazy-loading are correctly injected into the DOM before extraction.
