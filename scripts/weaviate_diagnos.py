import weaviate
from app.config import config


def comprehensive_diagnostics():
    """Run comprehensive diagnostics to identify the search issue"""

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
        print("🔍 WEAVIATE DIAGNOSTIC REPORT")
        print("=" * 50)

        # 1. Check Weaviate health and version
        print("\n1. WEAVIATE SERVER STATUS:")
        try:
            if client.is_ready():
                print("   ✅ Weaviate server is ready")
                meta = client.get_meta()
                print(f"   Version: {meta.get('version', 'Unknown')}")
                print(f"   Hostname: {meta.get('hostname', 'Unknown')}")
            else:
                print("   ❌ Weaviate server not ready")
                return
        except Exception as e:
            print(f"   ❌ Server check failed: {e}")
            return

        # 2. Check collections and their configurations
        print("\n2. COLLECTION ANALYSIS:")
        collections = client.collections.list_all()

        for collection_name in collections.keys():
            print(f"\n   📦 Collection: {collection_name}")

            try:
                collection = client.collections.get(collection_name)

                # Get collection configuration
                config_obj = collection.config.get()
                print(config_obj)
                print(f"      Vectorizer: {config_obj.vectorizer}")
                print(f"      Vector Index: {config_obj.vector_index_type}")

                # Count objects
                aggregate = collection.aggregate.over_all(total_count=True)
                count = aggregate.total_count
                print(f"      Object count: {count}")

                # Check if vectors exist
                sample = collection.query.fetch_objects(limit=1, include_vector=True)
                if sample.objects:
                    obj = sample.objects[0]
                    if hasattr(obj, "vector") and obj.vector:
                        print(f"      ✅ Vectors present (dim: {len(obj.vector)})")
                    else:
                        print(f"      ❌ NO VECTORS FOUND - This is likely the issue!")

                    # Show sample content
                    content_preview = str(obj.properties.get("content", ""))[:100]
                    print(f"      Sample content: {content_preview}...")
                else:
                    print(f"      ❌ No objects found in collection")

            except Exception as e:
                print(f"      ❌ Collection analysis failed: {e}")

        # 3. Test different search methods
        print("\n3. SEARCH METHOD TESTING:")
        test_collection = "Product_collection"  # Adjust if needed

        if test_collection in collections:
            collection = client.collections.get(test_collection)

            # Test simple fetch first
            print(f"\n   Testing basic fetch from {test_collection}:")
            try:
                fetch_result = collection.query.fetch_objects(limit=1)
                if fetch_result.objects:
                    print("      ✅ Basic fetch works")
                else:
                    print("      ❌ Basic fetch returns no objects")
            except Exception as e:
                print(f"      ❌ Basic fetch failed: {e}")

            # Test semantic search with very simple query
            print("\n   Testing semantic search:")
            test_queries = ["temperature", "monitor", "laser"]

            for query in test_queries:
                try:
                    # Try with very relaxed parameters
                    result = collection.query.near_text(
                        query=query,
                        limit=1,
                        distance=1.0,  # Maximum distance allowed
                        return_metadata=["distance", "certainty"],
                    )

                    if result.objects:
                        distance = (
                            result.objects[0].metadata.distance
                            if result.objects[0].metadata
                            else "N/A"
                        )
                        print(f"      ✅ '{query}' found result (distance: {distance})")
                    else:
                        print(f"      ❌ '{query}' no results")

                except Exception as e:
                    print(f"      ❌ '{query}' search failed: {e}")

            # Test BM25 if available
            print("\n   Testing BM25 search:")
            try:
                bm25_result = collection.query.bm25(query="temperature", limit=1)
                if bm25_result.objects:
                    print("      ✅ BM25 search works")
                else:
                    print("      ❌ BM25 search returns no results")
            except Exception as e:
                print(f"      ❌ BM25 search failed: {e}")

        # 4. Check OpenAI connection
        print("\n4. OPENAI CONNECTION TEST:")
        try:
            # Test if we can reach OpenAI API
            import requests

            headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
            response = requests.get(
                "https://api.openai.com/v1/models", headers=headers, timeout=10
            )

            if response.status_code == 200:
                print("      ✅ OpenAI API accessible")
            else:
                print(f"      ❌ OpenAI API error: {response.status_code}")

        except Exception as e:
            print(f"      ❌ OpenAI connection test failed: {e}")

        # 5. Provide recommendations
        print("\n5. RECOMMENDATIONS:")
        print_recommendations()

    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")

    finally:
        client.close()


def print_recommendations():
    """Print troubleshooting recommendations"""
    print("""
   Based on common issues:
   
   🔧 If no vectors are found:
   - Check if vectorization was enabled during data import
   - Verify OpenAI API key is correct and has credits
   - Re-import data with proper vectorization settings
   
   🔧 If searches return no results:
   - Try fetch_objects() first to ensure data exists
   - Use very high distance threshold (0.8-1.0) initially
   - Check if the vectorizer module is properly configured
   
   🔧 If specific error messages appear:
   - "module not found": Weaviate vectorizer module not installed
   - "rate limit": OpenAI API quota exceeded
   - "authentication": Invalid API key
   
   📝 Next steps:
   1. Run this diagnostic
   2. Check the vector presence result
   3. If no vectors: re-import with vectorization enabled
   4. If vectors exist: adjust search parameters
   """)


def quick_fix_test():
    """Test potential quick fixes"""
    print("\n🚀 QUICK FIX ATTEMPTS:")

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

        # Quick fix 1: Search with no distance limit
        print("\n1. Trying search with no distance limit:")
        try:
            result = collection.query.near_text(
                query="temperature monitor",
                limit=3,
                # No distance parameter = no limit
            )
            print(f"   Results: {len(result.objects)}")
            for obj in result.objects:
                if obj.metadata:
                    print(f"   Distance: {obj.metadata.distance:.3f}")
        except Exception as e:
            print(f"   Failed: {e}")

        # Quick fix 2: Use where filter with near_text
        print("\n2. Trying with where filter:")
        try:
            result = collection.query.near_text(
                query="monitor",
                where={
                    "path": ["content"],
                    "operator": "ContainsAny",
                    "valueText": ["temperature", "monitor", "optical"],
                },
                limit=3,
            )
            print(f"   Results: {len(result.objects)}")
        except Exception as e:
            print(f"   Failed: {e}")

        # Quick fix 3: Simple property search
        print("\n3. Trying property-based search:")
        try:
            result = collection.query.where(
                {"path": ["content"], "operator": "Like", "valueText": "*temperature*"},
                limit=3,
            )
            print(f"   Results: {len(result.objects)}")
        except Exception as e:
            print(f"   Failed: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    comprehensive_diagnostics()
    quick_fix_test()
