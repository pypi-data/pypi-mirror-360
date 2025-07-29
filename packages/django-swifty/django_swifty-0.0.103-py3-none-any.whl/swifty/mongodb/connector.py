"""MongoDB Connector"""

from time import sleep
from typing import Union, List, Dict
import six

from mongoengine import connect
from mongoengine.base import BaseDocument
from mongoengine.errors import MongoEngineException

from swifty.logging.logger import swifty_logger


def init_mongodb_connections(database_pool: Dict):
    """Init mongo connections

    Args:
        database_pool (dict): _description_
    """
    for alias, database in (database_pool or {}).items():
        swifty_logger.info(
            f"[SwiftyMongoConnection] - Establish connection to alias {alias}",
            database=database,
        )
        connect_to_db(alias=alias, **database)


def connect_to_db(alias: str, count: int = 3, **kwargs) -> None:  # type: ignore
    """
    Context manager to connect to the MongoDB database with retry logic.

    Args:
        alias (str): The alias for the connection.
        count (int, optional): Number of retry attempts. Defaults to 3.

    Raises:
        MongoEngineException: If unable to connect after specified attempts.
    """
    retry_count = 0
    exception = None
    connected = False

    while retry_count < count:
        try:
            # Attempt to connect
            connect(alias=alias, **kwargs)
            connected = True
            break  # Exit retry loop on successful connection
        except (MongoEngineException, ConnectionError) as ex:
            retry_count += 1
            exception = six.text_type(ex)
            sleep(0.3)  # Wait 300ms before retrying

    if not connected:
        raise MongoEngineException(
            f"Unable to connect to database after {count} attempts, specific error: {exception}"
        )


class MongoConnector:
    """MongoDB Connector class for handling database operations.

    Args:
        SwiftyLoggerMixin (_type_): _description_
    """

    def __init__(self, mongo_collection: BaseDocument) -> None:
        if not mongo_collection or not issubclass(mongo_collection, BaseDocument):
            raise MongoEngineException("Mongo collection is not defined")
        self.mongo_collection = mongo_collection

    @property
    def mongo_objects(self):
        """Get the objects manager for the MongoDB collection."""
        return getattr(self.mongo_collection, "objects")

    def insert(self, data: dict) -> None:
        """Insert a single document into the MongoDB collection.

        Args:
            data (dict): The document data to insert.
        """
        self.mongo_objects.insert(self.mongo_collection(**data))

    def insert_many(self, list_of_data: List[Dict]) -> None:
        """Insert multiple documents into the MongoDB collection.

        Args:
            list_of_data (List[Dict]): A list of document data to insert.
        """
        self.mongo_objects.insert(
            [self.mongo_collection(**data) for data in list_of_data],
        )

    def update(
        self,
        data: dict,
        filters: Union[dict, None] = None,
        q_combine: Union[None, str] = None,
        upsert: bool = True,  # ✅ Allow insert if not found
    ) -> None:
        """Update documents in the MongoDB collection.

        Args:
            data (dict): The data to update.
            filters (Union[dict, None], optional): Filters to apply. Defaults to None.
            q_combine (Union[None, str], optional): Query combination. Defaults to None.
        """
        self.mongo_objects(q_combine, **(filters or {})).update(
            __raw__={"$set": data}, upsert=upsert
        )

    def update_many(self, list_of_data: List[Dict]) -> None:
        """Replace multiple documents in the MongoDB collection.

        Args:
            list_of_data (List[Dict]): A list of document data to replace.
        """
        self.mongo_objects.replace(
            [self.mongo_collection(**data) for data in list_of_data],
        )

    def aggregate(self, pipeline: List[dict]) -> List[dict]:
        """Perform aggregation on the MongoDB collection.

        Args:
            pipeline (List[dict]): The aggregation pipeline.

        Returns:
            List[dict]: The results of the aggregation.
        """
        return self.mongo_objects.aggregate(pipeline)

    def __find(
        self,
        filters: Union[dict, None] = None,
        q_combine: Union[None, str] = None,
        order_by: str = "-version",
    ) -> List[dict]:
        """Find documents in the MongoDB collection.

        Args:
            filters (Union[dict, None], optional): Filters to apply. Defaults to None.
            q_combine (Union[None, str], optional): Query combination. Defaults to None.
            order_by (str, optional): Field to order by. Defaults to "-version".

        Returns:
            List[dict]: The found documents.
        """
        return self.mongo_objects.filter(q_combine, **(filters or {})).order_by(
            order_by
        )

    def find_one(
        self,
        filters: Union[dict, None] = None,
        q_combine: Union[None, str] = None,
        order_by: str = "-version",
    ) -> Union[None, dict]:
        """Find a single document in the MongoDB collection.

        Args:
            filters (Union[dict, None], optional): Filters to apply. Defaults to None.
            q_combine (Union[None, str], optional): Query combination. Defaults to None.
            order_by (str, optional): Field to order by. Defaults to "-version".

        Returns:
            Union[None, dict]: The found document or None if not found.
        """
        return self.__find(
            filters=filters, q_combine=q_combine, order_by=order_by
        ).first()

    def find_many(
        self,
        filters: Union[dict, None] = None,
        q_combine: Union[None, str] = None,
        order_by: str = "-version",
    ) -> List[dict]:
        """Find multiple documents in the MongoDB collection.

        Args:
            filters (Union[dict, None], optional): Filters to apply. Defaults to None.
            q_combine (Union[None, str], optional): Query combination. Defaults to None.
            order_by (str, optional): Field to order by. Defaults to "-version".

        Returns:
            List[dict]: A list of found documents.
        """
        return self.__find(
            filters=filters, q_combine=q_combine, order_by=order_by
        ).all()
