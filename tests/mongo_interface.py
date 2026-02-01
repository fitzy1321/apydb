"""Not a real test. I need to map out what mongo db functions and interfaces I want to use."""

from pymongo import MongoClient

client = MongoClient("mongodb://admin:password@localhost:27017/")

try:
    db = client["_testdb"]

    collection = db["data"]

    document = {"name": "John", "age": 30, "city": "New York"}
    result = collection.insert_one(document)
    print(f"Inserted document ID: {result.inserted_id}")

    # Find documents
    for doc in collection.find():
        print(doc)
finally:
    # Close connection
    client.close()
