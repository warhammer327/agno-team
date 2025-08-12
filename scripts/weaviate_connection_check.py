import weaviate

client = weaviate.connect_to_custom(
    http_host="10.10.10.80",
    http_port=8080,
    http_secure=False,  # Set to True if using HTTPS
    grpc_host="10.10.10.80",
    grpc_port=50051,  # Default gRPC port
    grpc_secure=False,  # Set to True if using secure gRPC
)

if client.is_ready():
    print("✅ Successfully connected to remote Weaviate server!")
else:
    print("❌ Failed to connect to Weaviate server")

client.close()
