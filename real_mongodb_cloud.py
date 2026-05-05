from pymongo import MongoClient

class RealCloudLayer:
    """
    Real Cloud Layer: Uses MongoDB to store authenticated and trusted data permanently.
    """
    def __init__(self, connection_string="mongodb://localhost:27017/"):
        print(f"[RealCloudLayer] Connecting to MongoDB at {connection_string}")
        self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        try:
            self.client.server_info()
            print("[RealCloudLayer] Successfully connected to MongoDB.")
        except Exception as e:
            print(f"[RealCloudLayer] WARNING: Could not connect to MongoDB. Is it running? Error: {e}")
            
        self.db = self.client["iot_cloud"]
        self.collection = self.db["trusted_data"]
        
    def store_data(self, data):
        """
        Stores legitimate data from trusted IoT devices into MongoDB.
        """
        # Insert the data into MongoDB
        result = self.collection.insert_one(data)
        
        # We need to remove the _id added by pymongo if we want to return a clean dict
        if "_id" in data:
            del data["_id"]
            
        total_count = self.collection.count_documents({})
        
        return {
            "status": "success",
            "message": "Data securely stored in MongoDB",
            "storage_size": total_count,
            "inserted_id": str(result.inserted_id)
        }
