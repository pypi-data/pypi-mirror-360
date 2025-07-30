from mongodbvector import MongoDBVector

# Example configuration for MongoDB connection
config = {
    "connection_string": "mongodb://localhost:27017",
    "data_base": "example_db",
    "collection": "example_collection"
}

# Initialize MongoDBVector with the configuration
mongo_vector = MongoDBVector(config)

# Connect to the MongoDB database
try:
    mongo_vector.connect()
    print("Connected to MongoDB successfully.")
except ConnectionError as e:
    print(e)

# Create a search index
try:
    index_name = "example_index"
    result = mongo_vector.create_search_index(name=index_name, dimension=1536)
    print(result)
except Exception as e:
    print(f"Error creating search index: {e}")

# Example query payload
query_payload = {
    "index_name": "example_index",
    "path": "plot_embedding",
    "query_vector": [0.1, 0.2, 0.3, ...],  # Example vector
    "numCandidates": 10,
    "limit": 5,
    "match_filter": {"field": "value"},  # Example filter
    "project_fields": {"field1": 1, "field2": 1}  # Example projection
}

# Perform a query
try:
    results = mongo_vector.query(query_payload)
    for result in results:
        print(result)
except Exception as e:
    print(f"Error querying MongoDB: {e}") 