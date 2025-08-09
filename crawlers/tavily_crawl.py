import os
from tavily import TavilyClient
from dotenv import load_dotenv
import json

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY not found in environment variables. Please check your .env file."
    )

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=tavily_api_key)

print("=== Finding ALL product pages from sevensix.co.jp/products/ ===")

# Step 2. Multiple crawling strategies focused only on products

# Strategy 1: Deep crawl from products section
print("\n[1/3] Deep crawling from products section...")
response1 = tavily_client.crawl(
    url="https://www.sevensix.co.jp/products/",
    instructions="Find all individual product pages under /products/",
    max_depth=4,
    max_breadth=300,
    limit=1000,
    select_paths=["/products/*"],  # Only product paths
    exclude_paths=["/products/feed.*"],  # Exclude feeds
    extract_depth="basic",
)

# Strategy 2: Try different entry points to products
print("[2/3] Crawling from homepage but filtering for products only...")
response2 = tavily_client.crawl(
    url="https://www.sevensix.co.jp/",
    instructions="Find all product pages",
    max_depth=3,
    max_breadth=200,
    limit=800,
    select_paths=["/products/*"],  # Only product paths
    exclude_paths=["/products/feed.*", "/products/category.*"],
    extract_depth="basic",
)

# Strategy 3: Try sitemap or category approach
print("[3/3] Looking for product categories and listings...")
response3 = tavily_client.crawl(
    url="https://www.sevensix.co.jp/products/",
    instructions="Find product categories, manufacturer pages, and all related product listings",
    max_depth=3,
    max_breadth=500,
    limit=1200,
    select_paths=["/products/*"],
    exclude_paths=["/products/feed.*"],
    extract_depth="basic",
)

# Step 3. Combine all results and extract ONLY product URLs
product_urls = []

# Combine results from all strategies
for response in [response1, response2, response3]:
    for result in response.get("results", []):
        url = result.get("url", "")

        # Only keep URLs that match the product pattern exactly
        if (
            url.startswith("https://www.sevensix.co.jp/products/")
            and url
            != "https://www.sevensix.co.jp/products/"  # Not the main products page
            and "/feed" not in url  # Not RSS feeds
            and "?" not in url  # No query parameters
            and "#" not in url
        ):  # No anchors
            product_urls.append(url)

# Remove duplicates and sort
unique_product_urls = sorted(list(set(product_urls)))

print(f"\n=== FOUND {len(unique_product_urls)} UNIQUE PRODUCT PAGES ===\n")

# Step 4. Display all product URLs with clean formatting
for i, url in enumerate(unique_product_urls, 1):
    # Extract product name from URL for better readability
    product_name = url.split("/")[-1].replace("_", " ").replace("-", " ").title()
    print(f"{i:3d}. {url}")

# Step 5. Save results
try:
    output_data = {
        "total_product_pages": len(unique_product_urls),
        "base_url": "https://www.sevensix.co.jp/products/",
        "product_urls": unique_product_urls,
    }

    with open("sevensix_product_urls.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(
        f"\n✅ Saved {len(unique_product_urls)} product URLs to: sevensix_product_urls.json"
    )

    # Also save as simple text file - just the URLs
    with open("sevensix_product_urls.txt", "w", encoding="utf-8") as f:
        for url in unique_product_urls:
            f.write(f"{url}\n")

    print(f"✅ Saved product URLs list to: sevensix_product_urls.txt")

except Exception as e:
    print(f"❌ Error saving files: {e}")

print(f"\n🎉 Found {len(unique_product_urls)} total product pages!")
