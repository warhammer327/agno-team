from agno.agent import Agent
from app.common.llm_models import get_gpt4o_model
from app.config import config
import weaviate


def search_knowledge_base(query: str) -> str:
    """
    Search for products in the knowledge base
    Args:
        query: Search query for products
    Returns:
        Formatted search results with product information and links
    """

    client = weaviate.connect_to_custom(
        http_host=config.WEAVIATE_HTTP_HOST,
        http_port=config.WEAVIATE_HTTP_PORT,
        http_secure=False,
        grpc_host=config.WEAVIATE_GRPC_HOST,
        grpc_port=config.WEAVIATE_GRPC_PORT,
        grpc_secure=False,
        headers={"X-OpenAI-Api-Key": config.OPENAI_API_KEY},
    )

    try:
        collection = client.collections.get("Product_collection")
        # Perform semantic search
        response = collection.query.near_text(
            query=query,
            limit=5,
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

        print("*" * 50)
        print(results)
        print("*" * 50)
        return "\n\n" + ("\n" + "=" * 50 + "\n\n").join(results)

    except Exception as e:
        return f"Error searching products: {str(e)}"

    finally:
        client.close()


# Create the model
model = get_gpt4o_model()

# Create agent with the function as a tool
product_agent = Agent(
    name="ProductSearchAgent",
    model=model,
    debug_mode=True,
    tools=[search_knowledge_base],
    stream_intermediate_steps=True,
    show_tool_calls=True,
    description="Searches for and retrieves detailed product information from the knowledge base.",
    system_message="""
        You are a helpful product information assistant with access to a product database.

        When users ask about products:
            1. Use the search_knowledge_base function with relevant keywords from their query
            2. Present the returned results clearly and helpfully
            3. The search results will include product descriptions and available resources
            4. If no matches are found, tell clearly that data was not found
            5. Always include any websites, manuals, videos, or other resources mentioned in the results

        Be conversational and helpful while presenting the factual information from the search results.
    """,
    instructions="""
        For any product-related query:

        1. Extract the main keywords from the user's question
        2. Use the search_knowledge_base function with those keywords
        3. Present the search results in a friendly, conversational manner
        4. Include all available resources (websites, PDFs, videos, images)
        5. If no results are found, suggest related search terms
        6. Only respond with results from search_knowledge_base, DO NOT RESPOND WITH INTERNAL KNOWLEDGE

        The search function will return formatted results - present them clearly to help the user.
    """,
)

# Test the agent
# if __name__ == "__main__":
#    while True:
#        user_input = input("\n👤 You: ").strip()
#        product_agent.print_response(user_input)
