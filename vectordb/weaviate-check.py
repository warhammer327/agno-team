import warnings

warnings.filterwarnings("ignore")

import weaviate
import weaviate.classes.config as wvc
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def main():
    # Connect to Weaviate v4
    client = weaviate.connect_to_local(headers={"X-OpenAI-Api-Key": OPENAI_API_KEY})
    print("Connected to Weaviate")

    try:
        # Delete collection if it exists to recreate with correct schema
        if client.collections.exists("ProductDocuments"):
            client.collections.delete("ProductDocuments")
            print("Deleted existing ProductDocuments collection")

        # Create collection with properties that Agno expects
        client.collections.create(
            "ProductDocuments",
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small"
            ),
            properties=[
                wvc.Property(
                    name="name", data_type=wvc.DataType.TEXT
                ),  # Agno expects this
                wvc.Property(
                    name="content", data_type=wvc.DataType.TEXT
                ),  # Main text content
                wvc.Property(
                    name="meta_data", data_type=wvc.DataType.TEXT
                ),  # Agno expects this
                wvc.Property(
                    name="filename", data_type=wvc.DataType.TEXT
                ),  # Original filename
            ],
        )
        print("Created ProductDocuments collection with correct schema")

        collection = client.collections.get("ProductDocuments")

        # Ingest all .txt files
        for file_path in Path("clean_text").glob("*.txt"):
            content = file_path.read_text(encoding="utf-8")

            # Create metadata as JSON string
            metadata = {
                "filename": file_path.name,
                "source": "product_documents",
                "type": "text",
                "file_size": len(content),
            }

            # Insert with all required properties for Agno
            collection.data.insert(
                {
                    "name": file_path.stem,  # filename without extension for Agno
                    "content": content,
                    "meta_data": json.dumps(metadata),  # metadata as JSON string
                    "filename": file_path.name,  # full filename for reference
                }
            )
            print(f"Added: {file_path.name}")

        # Show total count
        count = collection.aggregate.over_all(total_count=True).total_count
        print(f"\nTotal documents: {count}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
