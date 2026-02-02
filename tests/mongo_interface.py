"""Not a real test. I need to map out what mongo db functions and interfaces I want to use."""

from pprint import pprint

from pymongo import MongoClient

client = MongoClient("mongodb://admin:password@localhost:27017/")

try:
    db = client["_testdb"]

    collection = db["data"]

    document = {"name": "John", "age": 30, "city": "New York"}
    result = collection.insert_one(document)
    print(f"Inserted document ID: {result.inserted_id}")

    db_dict = {}
    # Find documents
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        documents = list(collection.find())  # Convert cursor to list of dicts
        db_dict[collection_name] = documents  # Store collection as a list of dicts

    pprint(db_dict, indent=2)
finally:
    # Close connection
    client.close()
