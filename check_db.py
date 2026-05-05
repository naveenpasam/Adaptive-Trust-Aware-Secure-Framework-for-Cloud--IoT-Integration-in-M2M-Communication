from pymongo import MongoClient
import json

def check_database():
    print("Connecting to local MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["iot_cloud"]
    collection = db["trusted_data"]
    
    total = collection.count_documents({})
    print(f"\nTotal legitimate records saved in the Cloud: {total}\n")
    
    if total > 0:
        print("Here are the last 3 data entries successfully saved:")
        print("-" * 50)
        # Fetch the last 3 documents (sorting by _id descending)
        recent_data = collection.find({}, {"_id": 0}).sort("_id", -1).limit(3)
        for doc in recent_data:
            # Print it nicely formatted
            print(json.dumps(doc, indent=4))
        print("-" * 50)

if __name__ == "__main__":
    check_database()
