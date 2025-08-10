import requests
from bs4 import BeautifulSoup
import time
import re
import os


def clean_filename(url):
    """Make a clean filename from URL"""
    # Remove trailing slashes and split
    url_clean = url.rstrip("/")
    parts = [part for part in url_clean.split("/") if part]

    # Get the last meaningful part (usually after 'products/')
    if "products" in parts:
        try:
            products_index = parts.index("products")
            if products_index + 1 < len(parts):
                name = parts[products_index + 1]
            else:
                name = parts[-1] if parts else "unknown"
        except:
            name = parts[-1] if parts else "unknown"
    else:
        name = parts[-1] if parts else "unknown"

    # Clean the filename
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    name = name.strip("_")  # Remove leading/trailing underscores

    # Ensure we have a name
    if not name:
        name = "unknown"

    return f"{name}.txt"


def clean_text(text):
    """Clean text for vector database ingestion"""
    if not text:
        return ""

    # Remove extra whitespace and normalize
    text = " ".join(text.split())

    # Remove special characters but keep Japanese, English, numbers, and basic punctuation
    text = re.sub(r"[^\w\s\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf.,!?:;()-]", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Remove empty lines and extra newlines
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    return "\n".join(lines)


def check_for_error_pages(soup, url):
    """Check if page contains error messages like 404, not found, etc."""
    error_patterns = [
        r"お探しのページが見つかりません",
        r"ページが見つかりません",
        r"404",
        r"Not Found",
        r"ページが存在しません",
        r"アクセスできません",
        r"エラーが発生しました",
        r"このページは存在しません",
        r"Page not found",
        r"File not found",
        r"The page you requested was not found",
    ]

    # Get all text content from the page
    page_text = soup.get_text()

    # Check for error patterns
    for pattern in error_patterns:
        if re.search(pattern, page_text, re.IGNORECASE):
            return True, pattern

    # Also check HTTP status indicators in content
    title = soup.find("title")
    if title:
        title_text = title.get_text().lower()
        if any(
            error in title_text
            for error in ["404", "not found", "error", "見つかりません"]
        ):
            return True, f"Title: {title.get_text()}"

    return False, None


def extract_text_content(soup):
    """Extract clean text content without HTML tags or links"""

    # Remove unwanted elements completely
    for tag in soup(
        ["script", "style", "nav", "footer", "header", "aside", "menu", "a"]
    ):
        tag.decompose()

    # Get all text content
    text_parts = []

    # Extract title
    title = soup.find("title")
    if title:
        title_text = clean_text(title.get_text())
        if title_text:
            text_parts.append(f"Title: {title_text}")

    # Look for main content areas
    main_selectors = [
        "main",
        ".main-content",
        ".content",
        "#content",
        ".product-info",
        ".product-details",
        ".entry-content",
        "article",
        ".post-content",
    ]

    main_content = None
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break

    # If no main content found, use body
    if not main_content:
        main_content = soup.find("body")

    if main_content:
        # Get all text, preserving some structure
        for element in main_content.find_all(string=True):
            text = clean_text(element.strip())
            if text and len(text) > 2:  # Only meaningful text
                text_parts.append(text)

    # Join all parts with single newlines
    full_text = "\n".join(text_parts)

    # Final cleanup
    full_text = re.sub(r"\n\s*\n", "\n", full_text)  # Remove multiple newlines
    full_text = re.sub(r"^\s+|\s+$", "", full_text, flags=re.MULTILINE)  # Trim lines

    return full_text.strip()


def scrape_page(url):
    """Scrape page and return clean text suitable for vector DB"""
    try:
        print(f"Scraping: {url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.content, "html.parser")

        # Check for error pages first
        is_error, error_pattern = check_for_error_pages(soup, url)
        if is_error:
            return None, "error_page", error_pattern

        # Extract clean text
        content = extract_text_content(soup)

        if not content:
            return None, "no_content", None

        # Add metadata for vector DB
        metadata = f"URL: {url}\nScraped: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return metadata + content, "success", None

    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
        return None, "request_error", str(e)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, "general_error", str(e)


# Load URLs
urls = []
with open("product_links.txt", "r", encoding="utf-8") as f:
    for line in f:
        url = line.strip()
        if url.startswith("https://"):
            urls.append(url)

# Remove duplicates
urls = list(set(urls))

# Create output folder
os.makedirs("clean_text", exist_ok=True)

print(f"Found {len(urls)} URLs to scrape")

# Track results
successful = 0
failed = 0
error_pages = []
no_content_pages = []
request_errors = []

for i, url in enumerate(urls):
    print(f"Progress: {i + 1}/{len(urls)}")

    content, status, error_info = scrape_page(url)

    if status == "success" and content and len(content.strip()) > 100:
        filename = clean_filename(url)
        filepath = f"clean_text/{filename}"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Saved: {filename} ({len(content)} chars)")
        successful += 1

    elif status == "error_page":
        error_pages.append((url, error_info))
        print(f"⚠ Error page detected: {url} (Pattern: {error_info})")
        failed += 1

    elif status == "no_content":
        no_content_pages.append(url)
        print(f"✗ No content: {url}")
        failed += 1

    elif status in ["request_error", "general_error"]:
        request_errors.append((url, error_info))
        print(f"✗ {status}: {url}")
        failed += 1
    else:
        print(f"✗ Failed: {url}")
        failed += 1

    time.sleep(1)

print(f"\n" + "=" * 50)
print(f"SCRAPING COMPLETED!")
print(f"=" * 50)
print(f"Total URLs processed: {len(urls)}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")

if error_pages:
    print(f"\n❌ ERROR PAGES FOUND ({len(error_pages)}):")
    print("-" * 40)
    for url, pattern in error_pages:
        print(f"• {url}")
        print(f"  Error pattern: {pattern}")
        print()

if no_content_pages:
    print(f"\n📝 NO CONTENT PAGES ({len(no_content_pages)}):")
    print("-" * 40)
    for url in no_content_pages:
        print(f"• {url}")

if request_errors:
    print(f"\n🌐 REQUEST ERRORS ({len(request_errors)}):")
    print("-" * 40)
    for url, error in request_errors:
        print(f"• {url}")
        print(f"  Error: {error}")
        print()

print(f"\n📁 Output folder: clean_text/")
print("Files are ready for vector database ingestion.")

# Save error report to file
if error_pages or no_content_pages or request_errors:
    with open("scraping_errors.txt", "w", encoding="utf-8") as f:
        f.write("SCRAPING ERROR REPORT\n")
        f.write("=" * 50 + "\n\n")

        if error_pages:
            f.write(f"ERROR PAGES ({len(error_pages)}):\n")
            f.write("-" * 30 + "\n")
            for url, pattern in error_pages:
                f.write(f"{url} - Pattern: {pattern}\n")
            f.write("\n")

        if no_content_pages:
            f.write(f"NO CONTENT PAGES ({len(no_content_pages)}):\n")
            f.write("-" * 30 + "\n")
            for url in no_content_pages:
                f.write(f"{url}\n")
            f.write("\n")

        if request_errors:
            f.write(f"REQUEST ERRORS ({len(request_errors)}):\n")
            f.write("-" * 30 + "\n")
            for url, error in request_errors:
                f.write(f"{url} - Error: {error}\n")

    print("📋 Error report saved to: scraping_errors.txt")
