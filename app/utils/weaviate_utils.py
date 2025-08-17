from app.config import config


def get_collection_by_security_level(level: str):
    collection_list = []
    weaviate_client = config.weaviate_client
    all_collections = weaviate_client.collections.list_all(simple=True)
    for collection_name, collection_config in all_collections.items():
        if collection_config.description == level:
            collection_list.append(collection_name)

    weaviate_client.close()
    return collection_list
