import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Locate and load .env file
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_paths = [
    os.path.join(backend_dir, ".env"),
    os.path.join(os.getcwd(), ".env"),
    os.path.join(os.getcwd(), "backend", ".env")
]

for p in env_paths:
    if os.path.exists(p):
        load_dotenv(dotenv_path=p)
        break

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_threat_shield")

class MongoDatabase:
    _instance = None

    def __init__(self):
        self.uri = MONGODB_URI
        self.db_name = MONGODB_DB_NAME
        self.client: Optional[MongoClient] = None
        self.db = None
        self.scans = None
        self._connected = False
        self._init_connection()

    @classmethod
    def get_instance(cls) -> "MongoDatabase":
        if cls._instance is None:
            cls._instance = MongoDatabase()
        return cls._instance

    def _init_connection(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2500)
            # Verify server is reachable
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.scans = self.db["scans"]
            # Ensure indexes
            self.scans.create_index("id", unique=True)
            self.scans.create_index([("timestamp", -1)])
            self._connected = True
            print(f"[Database] Successfully connected to MongoDB at {self.uri} (DB: {self.db_name})")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self._connected = False
            self.client = None
            self.db = None
            self.scans = None
            print(f"[Database Warning] Could not connect to MongoDB at {self.uri}: {e}")

    def is_connected(self) -> bool:
        if not self._connected or not self.client:
            # Try to reconnect lazily
            self._init_connection()
        return self._connected

    def save_scan(self, scan_data: Dict[str, Any]) -> bool:
        """
        Saves or updates a scan evaluation document in MongoDB.
        """
        if not self.is_connected() or self.scans is None:
            return False

        try:
            doc = dict(scan_data)
            # Remove any existing _id if present
            doc.pop("_id", None)
            
            scan_id = doc.get("id")
            if not scan_id:
                return False

            # Add server ingestion timestamp
            doc["saved_at"] = datetime.utcnow().isoformat() + "Z"

            self.scans.update_one(
                {"id": scan_id},
                {"$set": doc},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[Database Error] Failed to save scan #{scan_data.get('id')}: {e}")
            return False

    def get_recent_scans(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves the most recent scans sorted by timestamp descending.
        """
        if not self.is_connected() or self.scans is None:
            return []

        try:
            cursor = self.scans.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"[Database Error] Failed to fetch scan history: {e}")
            return []

    def get_counts(self) -> Dict[str, int]:
        """
        Computes count breakdown of all stored scans.
        """
        counts = {"Ham": 0, "Spam": 0, "Phishing": 0, "total": 0}
        if not self.is_connected() or self.scans is None:
            return counts

        try:
            total = self.scans.count_documents({})
            ham = self.scans.count_documents({"predicted_class": "Ham"})
            spam = self.scans.count_documents({"predicted_class": "Spam"})
            phishing = self.scans.count_documents({"predicted_class": "Phishing"})
            return {
                "total": total,
                "Ham": ham,
                "Spam": spam,
                "Phishing": phishing
            }
        except Exception as e:
            print(f"[Database Error] Failed to compute counts: {e}")
            return counts

    def clear_all(self) -> bool:
        """
        Clears all stored scans.
        """
        if not self.is_connected() or self.scans is None:
            return False

        try:
            self.scans.delete_many({})
            return True
        except Exception as e:
            print(f"[Database Error] Failed to clear scans: {e}")
            return False

# Global database instance
db = MongoDatabase.get_instance()

