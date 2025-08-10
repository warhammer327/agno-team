import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin, urldefrag


class SevensixSpider(scrapy.Spider):
    name = "sevensix_products_links"
    allowed_domains = ["sevensix.co.jp"]
    start_urls = ["https://www.sevensix.co.jp/"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DEPTH_LIMIT": 0,  # Crawl entire site
        "CONCURRENT_REQUESTS": 16,
        "LOG_LEVEL": "INFO",
    }
    visited_links = set()
    saved_product_links = set()  # Track saved product links to avoid duplicates

    def parse(self, response):
        for href in response.css("a::attr(href)").getall():
            # Build absolute URL
            url = urljoin(response.url, href)
            # Remove any fragment after '#'
            url, _ = urldefrag(url)

            # Skip duplicates and external links
            if "sevensix.co.jp" not in url or url in self.visited_links:
                continue

            # Skip wp-content links
            if "/wp-content/" in url:
                continue
            if "%" in url:
                continue
            if "?" in url:
                continue

            self.visited_links.add(url)

            # Only save links that match the products pattern
            if url.startswith("https://www.sevensix.co.jp/products/"):
                # Remove double slashes at the end and ensure single slash
                cleaned_url = url.rstrip("/") + "/"

                # Only save if we haven't saved this cleaned URL before
                if cleaned_url not in self.saved_product_links:
                    self.saved_product_links.add(cleaned_url)
                    print(cleaned_url)
                    # Save to file
                    with open("product_links.txt", "a", encoding="utf-8") as f:
                        f.write(cleaned_url + "\n")

            # Continue crawling all links to find more products links
            yield response.follow(url, callback=self.parse)


if __name__ == "__main__":
    # Clear old file before crawling
    open("product_links.txt", "w", encoding="utf-8").close()
    process = CrawlerProcess()
    process.crawl(SevensixSpider)
    process.start()
