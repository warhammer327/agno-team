import os
import re
from firecrawl import FirecrawlApp, JsonConfig
from dotenv import load_dotenv
from pydantic import BaseModel
from urllib.parse import urlparse
import time

load_dotenv()
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
if not firecrawl_api_key:
    raise ValueError(
        "firecrawl api key not found in environment variables. Please check your .env file."
    )
firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)


def remove_all_links(markdown_text):
    """
    Remove all types of links from markdown text
    """
    if not markdown_text:
        return markdown_text
    # Remove markdown links [text](url) - keep only the text
    markdown_text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", markdown_text)
    # Remove standalone URLs (http/https)
    markdown_text = re.sub(r"https?://[^\s\)\]\,]+", "", markdown_text)
    # Remove image links ![alt](url) - remove entirely
    markdown_text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", "", markdown_text)
    # Remove reference-style links [text][ref] - keep only the text
    markdown_text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", markdown_text)
    # Remove standalone www URLs
    markdown_text = re.sub(r"www\.[^\s\)\]\,]+", "", markdown_text)
    # Remove email addresses
    markdown_text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", markdown_text
    )
    # Clean up multiple empty lines
    markdown_text = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown_text)
    # Clean up spaces before and after newlines
    markdown_text = re.sub(r" +\n", "\n", markdown_text)
    markdown_text = re.sub(r"\n +", "\n", markdown_text)
    # Remove lines that are just dashes or empty
    lines = markdown_text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not re.match(r"^[-\s]*$", stripped):
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def get_filename_from_url(url):
    """
    Generate a safe filename from URL
    """
    parsed_url = urlparse(url)
    # Get the path and remove leading/trailing slashes
    path = parsed_url.path.strip("/")
    # Replace path separators and other unsafe characters
    filename = re.sub(r"[^\w\-_.]", "_", path)
    # Remove multiple underscores
    filename = re.sub(r"_+", "_", filename)
    # Ensure it's not empty and add .md extension
    if not filename or filename == "_":
        filename = parsed_url.netloc.replace(".", "_")
    return f"{filename}.md"


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "scraped_content")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

urls = [
    "https://www.sevensix.co.jp/products/hc_nktp/",
]

print(f"Starting to scrape {len(urls)} URLs...")
print(f"Output directory: {output_dir}")

for i, url in enumerate(urls, 1):
    print(f"\nProcessing {i}/{len(urls)}: {url}")

    try:
        # Scrape the URL
        llm_extraction_result = firecrawl_app.scrape_url(
            url,
            only_main_content=True,
            timeout=120000,
        )

        # Extract and clean the markdown content
        cleaned_markdown = None
        if (
            hasattr(llm_extraction_result, "markdown")
            and llm_extraction_result.markdown
        ):
            cleaned_markdown = remove_all_links(llm_extraction_result.markdown)
        elif (
            isinstance(llm_extraction_result, dict)
            and "markdown" in llm_extraction_result
        ):
            cleaned_markdown = remove_all_links(llm_extraction_result["markdown"])

        if cleaned_markdown:
            # Generate filename and save to file
            filename = get_filename_from_url(url)
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Content from: {url}\n\n")
                f.write(cleaned_markdown)

            print(f"✓ Saved to: {filename}")
            print(f"  Content length: {len(cleaned_markdown)} characters")
        else:
            print(f"✗ No markdown content found for {url}")
            print(f"  Raw result: {llm_extraction_result}")

            # Save error info to file
            filename = get_filename_from_url(url)
            filename = filename.replace(".md", "_error.txt")
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Error scraping: {url}\n\n")
                f.write(f"Result: {str(llm_extraction_result)}")

            print(f"✗ Error info saved to: {filename}")

    except Exception as e:
        print(f"✗ Error scraping {url}: {str(e)}")

        # Save error to file
        filename = get_filename_from_url(url)
        filename = filename.replace(".md", "_error.txt")
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Exception scraping: {url}\n\n")
            f.write(f"Error: {str(e)}")

        print(f"✗ Error saved to: {filename}")

    # Add a small delay between requests to be respectful
    if i < len(urls):
        time.sleep(1)

print(f"\n🎉 Scraping complete! Check the '{output_dir}' directory for results.")
