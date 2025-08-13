import weaviate
from app.config import config

# Connect to Weaviate
client = weaviate.connect_to_custom(
    http_host=config.WEAVIATE_HTTP_HOST,
    http_port=config.WEAVIATE_HTTP_PORT,
    http_secure=False,
    grpc_host=config.WEAVIATE_GRPC_HOST,
    grpc_port=config.WEAVIATE_GRPC_PORT,
    grpc_secure=False,
    headers={"X-OpenAI-Api-Key": config.OPENAI_API_KEY},
)


def semantic_search(collection_name, query, limit=3):
    """Perform a simple semantic search on a collection"""
    collection = client.collections.get(collection_name)
    response = collection.query.near_text(
        query=query, limit=limit, return_metadata=["distance"]
    )
    return response


def show_collection_data(collection_name, limit=2):
    """Show sample data from a collection"""
    try:
        collection = client.collections.get(collection_name)
        response = collection.query.fetch_objects(limit=limit)

        print(f"\n📊 Sample data from '{collection_name}':")
        if not response.objects:
            print("No data found in this collection.")
        else:
            for obj in response.objects:
                print(f"\n- ID: {obj.uuid}")
                print(f"  Properties: {obj.properties}")
    except Exception as e:
        print(f"Error fetching data from collection: {str(e)}")


try:
    if client.is_ready():
        print("✅ Successfully connected to remote Weaviate server!")

        # Get all collections
        collections = client.collections.list_all()
        if not collections:
            print("No collections found in Weaviate.")
        else:
            print(f"\nFound {len(collections)} collections:")

            # Print collection names and show sample data
            for collection_name in collections.keys():
                print(f"\n- {collection_name}")
                show_collection_data(collection_name)

            # Let user choose a collection for semantic search
            print("\n🎯 Let's try semantic search!")
            target_collection = input("\nEnter the collection name to search in: ")

            if target_collection not in collections:
                print(
                    f"❌ Collection '{target_collection}' not found. Available collections:"
                )
                for name in collections.keys():
                    print(f"- {name}")
            else:
                search_query = input(
                    f"\nEnter your search query for '{target_collection}': "
                )

                try:
                    results = semantic_search(target_collection, search_query)

                    print(f"\n🔍 Semantic search results for '{search_query}':")
                    if not results.objects:
                        print("No results found.")
                    else:
                        for obj in results.objects:
                            print(f"\n- ID: {obj.uuid}")
                            print(f"  Properties: {obj.properties}")
                            if obj.metadata:
                                print(f"  Distance: {obj.metadata.distance:.3f}")
                except Exception as e:
                    print(f"Error performing search: {str(e)}")

    else:
        print("❌ Failed to connect to Weaviate server")

finally:
    client.close()
