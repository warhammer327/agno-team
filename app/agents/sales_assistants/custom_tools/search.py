from app.config import config
from app.utils.weaviate_utils import get_collection_by_security_level


def search_knowledge_base(query: str) -> str:
    """
    Search for products in the knowledge base
    Args:
        query: Search query for products
    Returns:
        Formatted search results with product information and links
    """

    client = config.weaviate_client
    try:
        collection = client.collections.get("Product_collection_demo")
        # Perform semantic search
        response = collection.query.near_text(
            query=query,
            limit=3,
            return_properties=["content", "source", "image_urls", "youtube_urls"],
            return_metadata=["score"],
        )

        if not response.objects:
            return f"No products found matching '{query}'"

        results = []
        seen_sources = set()  # Avoid duplicates

        for obj in response.objects:
            source = obj.properties.get("source", "Unknown Product")

            # Skip duplicates
            if source in seen_sources:
                continue
            seen_sources.add(source)

            content = obj.properties.get("content", "")
            image_urls = (
                obj.properties.get("image_urls", "").split("\n")
                if obj.properties.get("image_urls")
                else []
            )
            youtube_urls = (
                obj.properties.get("youtube_urls", "").split("\n")
                if obj.properties.get("youtube_urls")
                else []
            )

            # Clean up URLs by removing any whitespace
            image_urls = [url.strip() for url in image_urls if url.strip()]
            youtube_urls = [url.strip() for url in youtube_urls if url.strip()]

            result_text = f"Product: {source}\n\n"

            # Add content (limit for readability)
            if len(content) > 500:
                result_text += f"{content[:500]}...\n\n"
            else:
                result_text += f"{content}\n\n"

            # Add resources
            resources = []
            if source.startswith(("http://", "https://")):
                resources.append(f"Product Page: {source}")

            if youtube_urls:
                for url in youtube_urls[:2]:  # Limit to 2 videos
                    resources.append(f"Video: {url}")

            if image_urls:
                for url in image_urls[:3]:  # Limit to 3 images
                    resources.append(f"Image: {url}")

            if resources:
                result_text += "Available Resources:\n" + "\n".join(
                    f"- {r}" for r in resources
                )

            results.append(result_text)

        return "\n\n" + ("\n" + "=" * 50 + "\n\n").join(results)

    except Exception as e:
        return f"Error searching products: {str(e)}"

    finally:
        client.close()
