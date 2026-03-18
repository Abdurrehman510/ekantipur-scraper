"""
Ekantipur News Scraper
=======================
This script uses Playwright to scrape data from https://ekantipur.com.

Task 1: Extract the top 5 entertainment news articles from /entertainment.
Task 2: Extract the Cartoon of the Day from the homepage.

Output is saved to output.json.
"""

import json
import re
import sys
from playwright.sync_api import sync_playwright


def scrape_entertainment_news(page) -> list[dict]:
    """
    Navigate to the Entertainment section and extract the top 5 news articles.

    Each article entity on the page follows this HTML structure:
        <div class="category">
            <div class="category-inner-wrapper">
                <div class="category-description">
                    <h2><a href="...">Title</a></h2>
                    <div class="author-name"><p><a>Author</a></p></div>
                    ...
                </div>
                <div class="category-image">
                    <a><figure><img src="image_url"></figure></a>
                </div>
            </div>
        </div>

    Returns:
        A list of dicts with keys: title, image_url, category, author
    """
    # Navigate to the entertainment section
    page.goto("https://ekantipur.com/entertainment")

    # Wait for the article cards to load on the page
    page.wait_for_selector("div.category", timeout=15000)

    # Wait for network to settle so all dynamic content (images, etc.) is loaded
    page.wait_for_load_state("networkidle")

    # Scroll down the page to trigger lazy-loaded images.
    # Some article images below the fold won't have their src loaded until scrolled into view.
    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)  # Allow time for lazy-loaded images to render

    # Scroll back to top for consistency
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_load_state("networkidle")

    # Select all article entities on the page (each is a div.category)
    article_elements = page.query_selector_all("div.category")

    # We only need the first 5 articles
    top_5_elements = article_elements[:5]

    articles = []

    for index, article in enumerate(top_5_elements, start=1):
        try:
            # --- Extract Title ---
            # Title is inside: .category-description > h2 > a
            title_element = article.query_selector(".category-description h2 a")
            title = title_element.text_content().strip() if title_element else None

            # --- Extract Image URL ---
            # Image is inside: .category-image > a > figure > img (src attribute)
            # Some images are lazy-loaded; try "src" first, then fall back to "data-src"
            img_element = article.query_selector(".category-image img")
            image_url = None
            if img_element:
                image_url = img_element.get_attribute("src") or img_element.get_attribute("data-src")

            # --- Extract Category ---
            # The category/section label. Since we are on the Entertainment (मनोरञ्जन) page,
            # the default category is "मनोरञ्जन". If individual articles have a subcategory
            # label (e.g., "बलिउड"), we try to extract it from within the article card.
            # Looking for any span or tag that might contain a subcategory label.
            category_element = article.query_selector(".category-label, .sub-category, .tag")
            if category_element:
                category = category_element.text_content().strip()
            else:
                # Default to the section name since we're on the entertainment page
                category = "मनोरञ्जन"

            # --- Extract Author ---
            # Author is inside: .author-name > p > a
            # Use null (None) if not found, as per task requirements
            author_element = article.query_selector(".author-name p a")
            author = author_element.text_content().strip() if author_element else None

            article_data = {
                "title": title,
                "image_url": image_url,
                "category": category,
                "author": author,
            }

            articles.append(article_data)
            print(f"[OK] Article {index}: {title}")

        except Exception as e:
            # Robust error handling: log the error but continue scraping other articles
            print(f"[WARN] Error extracting article {index}: {e}")
            continue

    return articles


def scrape_cartoon_of_the_day(page) -> dict:
    """
    Navigate to the ekantipur homepage and extract the Cartoon of the Day.

    The cartoon is displayed inside a Swiper carousel with this HTML structure:
        <div class="swiper-slide c-slide swiper-slide-active ...">
            <figure>
                <a class="loading-img" href="..." data-fancybox="gallery">
                    <img class="loaded" alt="caption text" src="image_url">
                </a>
            </figure>
        </div>

    The cartoonist's name is embedded in the img 'alt' attribute.
    For example: "कान्तिपुर दैनिकमा आज प्रकाशित अविनको कार्टुन" -> author is "अविन"

    Returns:
        A dict with keys: title, image_url, author
    """
    # Navigate to the ekantipur homepage where the cartoon section lives
    page.goto("https://ekantipur.com")

    # Wait for the page content to fully load
    page.wait_for_load_state("networkidle")

    # Scroll down the page to ensure the cartoon carousel section is loaded
    # (it may be below the fold and lazy-loaded)
    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    # Wait for the Swiper carousel slide to be present in the DOM
    page.wait_for_selector("div.swiper-slide.c-slide", timeout=15000)

    try:
        # Select the currently active/first slide in the cartoon Swiper carousel
        active_slide = page.query_selector(
            "div.swiper-slide.c-slide.swiper-slide-active"
        )

        # Fallback: if no slide has the 'active' class, pick the first slide
        if not active_slide:
            active_slide = page.query_selector("div.swiper-slide.c-slide")

        if not active_slide:
            print("[WARN] Could not find any cartoon slide on the page.")
            return {"title": None, "image_url": None, "author": None}

        # --- Extract the cartoon image element ---
        img_element = active_slide.query_selector("figure img")

        # --- Extract Title ---
        # The cartoon title/caption is stored in the img's alt attribute
        title = img_element.get_attribute("alt").strip() if img_element else None

        # --- Extract Image URL ---
        # Try 'src' first, then 'data-src' for lazy-loaded images
        image_url = None
        if img_element:
            image_url = (
                img_element.get_attribute("src")
                or img_element.get_attribute("data-src")
            )

        # --- Extract Author ---
        # The cartoonist's name is embedded in the alt text with the pattern:
        # "...प्रकाशित <AUTHOR_NAME>को कार्टुन"
        # We use a regex to extract the name before "को कार्टुन"
        author = None
        if title:
            match = re.search(r"(\S+)को\s*कार्टुन", title)
            if match:
                author = match.group(1)

        cartoon_data = {
            "title": title,
            "image_url": image_url,
            "author": author,
        }

        print(f"[OK] Cartoon: {title}")
        return cartoon_data

    except Exception as e:
        print(f"[WARN] Error extracting Cartoon of the Day: {e}")
        return {"title": None, "image_url": None, "author": None}


def main():
    """
    Main entry point: launches the browser, scrapes both tasks,
    prints results to the console, and saves output.json.
    """
    # Fix Windows console encoding to support Nepali/Devanagari text
    sys.stdout.reconfigure(encoding="utf-8")

    with sync_playwright() as p:
        # Launch Chromium in headed mode for debugging (use headless=True for production)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("=" * 60)
        print("Ekantipur News Scraper")
        print("=" * 60)

        # --- Task 1: Scrape Entertainment News ---
        print()
        print("Task 1: Extracting top 5 Entertainment News articles...")
        print("-" * 60)
        entertainment_news = scrape_entertainment_news(page)
        print(f"  -> Extracted {len(entertainment_news)} articles.")

        # --- Task 2: Scrape Cartoon of the Day ---
        print()
        print("Task 2: Extracting Cartoon of the Day...")
        print("-" * 60)
        cartoon_of_the_day = scrape_cartoon_of_the_day(page)

        # --- Combine Results ---
        output = {
            "entertainment_news": entertainment_news,
            "cartoon_of_the_day": cartoon_of_the_day,
        }

        # Pretty-print the full results to console
        print()
        print("=" * 60)
        print("FINAL OUTPUT")
        print("=" * 60)
        output_json = json.dumps(
            output,
            indent=2,
            ensure_ascii=False,  # Important: preserve Nepali/Devanagari characters
        )
        print(output_json)

        # Save to output.json
        with open("output.json", "w", encoding="utf-8") as f:
            f.write(output_json)
        print()
        print("[OK] Output saved to output.json")

        # Clean up
        browser.close()


if __name__ == "__main__":
    main()
