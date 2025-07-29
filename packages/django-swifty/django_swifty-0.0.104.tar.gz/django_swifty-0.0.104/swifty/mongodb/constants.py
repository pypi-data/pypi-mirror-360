"""Constants"""

from dataclasses import dataclass


@dataclass
class MongoConnectorEvents:
    """_summary_"""

    MONGO_CONNECTION = "MONGO_CONNECTION"
    TIMEOUT_CONNECTION = (
        f"{MONGO_CONNECTION}: Mongo connection timed out. Reconnecting."
    )
    ERROR_CONNECTION = f"{MONGO_CONNECTION}: Error connecting from mongo"
    ERROR_DISCONNECTING = f"{MONGO_CONNECTION}: Error disconnecting from mongo"
    ERROR_EXECUTION = f"{MONGO_CONNECTION}: Error execution from mongo"
