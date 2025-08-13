import os
import weaviate
import weaviate.classes.config as wc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import config


def create_proper_schema(client, collection_name="Product_collection"):
    """Create a proper schema for the product collection"""
    try:
        # Delete existing collection if it exists
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)
            print(f"🗑️  Deleted existing collection '{collection_name}'")

        client.collections.create(
            name=collection_name,
            vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
        )
        print(f"✅ Created new collection '{collection_name}' with proper schema")
        return True
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False


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

try:
    collection_name = "Product_collection"

    # Create proper schema first
    if not create_proper_schema(client, collection_name):
        raise Exception("Failed to create schema")

    # Read and parse products
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "product_data", "example_products.txt")
    with open(file_path, "r") as f:
        content = f.read()

    products = []
    for i, section in enumerate(content.split("---")):
        if not section.strip():
            continue

        lines = section.strip().split("\n")
        product = {
            "id": f"{i + 1}",
            "title": "",
            "text": section.strip(),
            "website": "",
            "pdf_links": [],
            "youtube_links": [],
            "image_links": [],
        }

        for line in lines:
            if line.startswith("Title: "):
                product["title"] = line.replace("Title: ", "")
            elif "https://" in line and "youtube" in line:
                product["youtube_links"].append(line.strip("- ").strip())
            elif "https://" in line and ".pdf" in line:
                product["pdf_links"].append(line.strip("- ").strip())
            elif "https://" in line and any(
                ext in line for ext in [".jpg", ".png", ".gif"]
            ):
                product["image_links"].append(line.strip("- ").strip())
            elif (
                "https://" in line
                and line.strip("- ").strip()
                not in product["pdf_links"]
                + product["youtube_links"]
                + product["image_links"]
            ):
                product["website"] = line.strip("- ").strip()

        products.append(product)

    # Chunk the text
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    chunks = []

    for product in products:
        text_chunks = splitter.split_text(product["text"])

        for idx, chunk_text in enumerate(text_chunks):
            # Prepare metadata with all links
            metadata = {
                "product_id": product["id"],
                "title": product["title"],
                "chunk_index": idx,
                "total_chunks": len(text_chunks),
                "website": product["website"],
                "pdf_links": product["pdf_links"],
                "youtube_links": product["youtube_links"],
                "image_links": product["image_links"],
            }

            chunks.append(
                {
                    "content": chunk_text,
                    "source": product["title"],
                    "metadata": metadata,
                }
            )

        print(f"📦 Processed {product['title']} into {len(text_chunks)} chunks")

    # Get collection and insert chunks
    collection = client.collections.get(collection_name)

    with collection.batch.dynamic() as batch:
        for chunk in chunks:
            batch.add_object(properties=chunk)

    print(
        f"✅ Successfully ingested {len(chunks)} chunks from {len(products)} products into '{collection_name}'"
    )

finally:
    client.close()
