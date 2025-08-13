import weaviate
from agno.vectordb.search import SearchType
from app.config import config


def debug_weaviate_setup():
    """Debug the Weaviate setup and search capabilities"""

    # Test direct connection using the same config as ingestion
    client = weaviate.connect_to_custom(
        http_host=config.WEAVIATE_HTTP_HOST,
        http_port=config.WEAVIATE_HTTP_PORT,
        http_secure=False,
        grpc_host=config.WEAVIATE_GRPC_HOST,
        grpc_port=config.WEAVIATE_GRPC_PORT,
        grpc_secure=False,
    )

    try:
        collection_name = "Product_collection"

        # 1. Check if collection exists
        if not client.collections.exists(collection_name):
            print(f"❌ Collection '{collection_name}' does not exist!")
            return False

        print(f"✅ Collection '{collection_name}' exists")

        # 2. Get collection info
        collection = client.collections.get(collection_name)

        # 3. Check collection contents
        response = collection.query.fetch_objects(limit=5)
        print(f"📊 Total objects in collection: {len(response.objects)}")

        if response.objects:
            # Show structure of first object
            first_obj = response.objects[0]
            print(f"🔍 First object properties: {list(first_obj.properties.keys())}")
            print(
                f"📝 Sample content: {first_obj.properties.get('content', 'N/A')[:200]}..."
            )
            print(f"📁 Source: {first_obj.properties.get('source', 'N/A')}")

        # 4. Test search for solar products
        print("\n🔍 Testing solar product search...")

        search_response = collection.query.near_text(
            query="solar product", limit=3, return_metadata=["score"]
        )

        print(f"🎯 Found {len(search_response.objects)} results for 'solar product':")

        for i, obj in enumerate(search_response.objects):
            print(f"\n--- Result {i + 1} ---")
            print(f"Source: {obj.properties.get('source', 'Unknown')}")
            print(f"Content: {obj.properties.get('content', 'N/A')[:300]}...")
            print(
                f"Score: {obj.metadata.score if hasattr(obj.metadata, 'score') else 'N/A'}"
            )

            # Check metadata
            metadata = obj.properties.get("metadata", {})
            if metadata:
                if metadata.get("website"):
                    print(f"Website: {metadata['website']}")
                if metadata.get("pdf_links"):
                    print(f"PDF Links: {metadata['pdf_links']}")

        return True

    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        client.close()


def test_agno_weaviate_config():
    """Test if the issue is with Agno's Weaviate configuration"""
    from agno.vectordb.weaviate import Weaviate
    from agno.embedder.openai import OpenAIEmbedder

    try:
        embedder = OpenAIEmbedder(
            id="text-embedding-3-small",
            api_key=config.OPENAI_API_KEY,
        )

        # Try different configurations
        configs_to_try = [
            {
                "name": "Basic Vector Search",
                "config": {
                    "collection": "Product_collection",
                    "search_type": SearchType.vector,
                    "local": True,
                    "embedder": embedder,
                },
            },
            {
                "name": "Custom Connection",
                "config": {
                    "collection": "Product_collection",
                    "search_type": SearchType.vector,
                    "host": config.WEAVIATE_HTTP_HOST,
                    "port": config.WEAVIATE_HTTP_PORT,
                    "embedder": embedder,
                },
            },
        ]

        for config_test in configs_to_try:
            print(f"\n🧪 Testing: {config_test['name']}")
            try:
                vector_db = Weaviate(**config_test["config"])
                # Try a simple search
                results = vector_db.search("solar product", limit=2)
                print(f"✅ Success! Found {len(results)} results")

                for result in results:
                    print(f"  - {result.get('source', 'Unknown source')}")

            except Exception as e:
                print(f"❌ Failed: {e}")

    except Exception as e:
        print(f"❌ Error in Agno config test: {e}")


if __name__ == "__main__":
    print("🚀 Starting Weaviate debugging...")

    if debug_weaviate_setup():
        print("\n" + "=" * 50)
        print("Testing Agno Weaviate configurations...")
        test_agno_weaviate_config()

    print("\n✅ Debugging complete!")
