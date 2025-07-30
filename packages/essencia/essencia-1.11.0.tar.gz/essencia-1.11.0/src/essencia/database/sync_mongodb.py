__all__ = ['Database']

import logging
import time
from typing import Optional

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout

logger = logging.getLogger(__name__)


class Database:
    """
    Database class for managing MongoDB connections and operations.
    This is a sync version for compatibility with existing code.
    """
    def __init__(self, database_name: str, mongodb_url: str = None):
        """
        Initializes the Database instance with the specified database name.

        Args:
            database_name (str): The name of the database to connect to.
            mongodb_url (str): MongoDB connection URL. If not provided, must be set later.
        """
        self.database_name: str = database_name
        self.mongodb_url = mongodb_url
        self._connected = False
        self._last_ping_time = 0
        self._ping_interval = 30  # Check connectivity every 30 seconds
        
        if mongodb_url:
            self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize the MongoDB connection."""
        try:
            # Add connection pooling with more resilient settings
            self.client: MongoClient = MongoClient(
                self.mongodb_url, 
                server_api=ServerApi('1'),
                maxPoolSize=20,  # Reduced pool size for better stability
                minPoolSize=5,
                maxIdleTimeMS=60000,  # Increased idle time
                connectTimeoutMS=10000,  # Reduced connection timeout
                serverSelectionTimeoutMS=5000,  # Reduced server selection timeout
                socketTimeoutMS=10000,  # Added socket timeout
                heartbeatFrequencyMS=10000,  # More frequent heartbeats
                retryWrites=True,
                retryReads=True,
                # Add SSL settings for Atlas
                tls=True,
                tlsAllowInvalidCertificates=False
            )
            # Test connection
            self._connected = self.ping()
            if self._connected:
                self._ensure_indexes()
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            self.client = None
            self._connected = False
    
    def _ensure_indexes(self):
        """Create indexes for common queries to improve performance"""
        try:
            db = self.client[self.database_name]
            logger.info("Database indexes created/verified successfully")
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")
    
    def _create_index_safe(self, collection, index_spec, **kwargs):
        """
        Safely create an index, handling existing indexes gracefully.
        
        Args:
            collection: MongoDB collection
            index_spec: Index specification (list of tuples)
            **kwargs: Additional index options (unique, sparse, etc.)
        """
        try:
            collection.create_index(index_spec, background=True, **kwargs)
        except Exception as e:
            if "already exists" not in str(e):
                logger.warning(f"Failed to create index on {collection.name}: {e}")
        
    def ping(self):
        """
        Pings the MongoDB server to check the connection status.
        Returns True if connected, False otherwise.
        """
        try:
            if not self.client:
                return False
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            self._connected = True
            self._last_ping_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
    
    def is_connected(self):
        """
        Check if database is currently connected.
        Performs periodic connectivity checks.
        """
        current_time = time.time()
        
        # If we haven't checked connectivity recently, do a ping
        if current_time - self._last_ping_time > self._ping_interval:
            return self.ping()
        
        return self._connected
    
    def reconnect(self, max_retries=3):
        """
        Attempt to reconnect to MongoDB with retries.
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to reconnect to MongoDB (attempt {attempt + 1}/{max_retries})")
                
                # Close existing connection if any
                if self.client:
                    self.client.close()
                
                # Create new client
                self.client = MongoClient(
                    self.mongodb_url, 
                    server_api=ServerApi('1'),
                    maxPoolSize=20,
                    minPoolSize=5,
                    maxIdleTimeMS=60000,
                    connectTimeoutMS=10000,
                    serverSelectionTimeoutMS=5000,
                    socketTimeoutMS=10000,
                    heartbeatFrequencyMS=10000,
                    retryWrites=True,
                    retryReads=True,
                    tls=True,
                    tlsAllowInvalidCertificates=False
                )
                
                # Test connection
                if self.ping():
                    logger.info("Successfully reconnected to MongoDB!")
                    return True
                    
            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error("Failed to reconnect to MongoDB after all attempts")
        self._connected = False
        return False
    
    def execute_with_retry(self, operation_func, *args, **kwargs):
        """
        Execute a database operation with automatic retry on connection failures.
        """
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                # Check connectivity before operation
                if not self.is_connected():
                    if not self.reconnect():
                        raise ConnectionFailure("Unable to establish database connection")
                
                return operation_func(*args, **kwargs)
                
            except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout) as e:
                logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries:
                    # Try to reconnect
                    if self.reconnect():
                        continue
                    else:
                        time.sleep(1)  # Brief pause before retry
                else:
                    logger.error("Database operation failed after all retries")
                    raise e
            except Exception as e:
                # For non-connection errors, don't retry
                logger.error(f"Database operation error: {e}")
                raise e
    
    def find_one(self, collection: str, query: dict) -> dict:
        """
        Finds a single document in the specified collection that matches the query.

        Args:
            collection (str): The name of the collection to search.
            query (dict): The query to filter the documents.

        Returns:
            dict: The found document, or None if no document matches the query.
        """
        def _find_one_operation():
            if not self.client:
                logger.error("MongoDB client not initialized")
                return None
            table = self.get_collection(collection)
            return table.find_one(query)
        
        try:
            return self.execute_with_retry(_find_one_operation)
        except Exception as e:
            logger.error(f"Error finding document in {collection}: {e}")
            return None

    def find(self, collection: str, query: dict) -> list[dict]:
        """
        Finds all documents in the specified collection that match the query.

        Args:
            collection (str): The name of the collection to search.
            query (dict): The query to filter the documents.

        Returns:
            list[dict]: A list of documents that match the query.
        """
        def _find_operation():
            if not self.client:
                logger.error("MongoDB client not initialized")
                return []
            table = self.get_collection(collection)
            result = []
            for item in list(table.find(query)):
                result.append(item)
            return result
        
        try:
            return self.execute_with_retry(_find_operation)
        except Exception as e:
            logger.error(f"Error finding documents in {collection}: {e}")
            return []

    def save_one(self, collection: str, data: dict) -> Optional[dict]:
        """
        Saves a single document to the specified collection.
        If the document has an _id, it will replace the existing document.
        If not, it will create a new document.

        Args:
            collection (str): The name of the collection to save the document.
            data (dict): The document data to save.

        Returns:
            Optional[dict]: The saved document, or None if the operation fails.
        """
        table = self.get_collection(collection)
        
        # Check if document has an _id (existing document)
        if '_id' in data and data['_id'] is not None:
            # Replace existing document (keeping the same _id)
            doc_id = data['_id']
            result = table.replace_one({'_id': doc_id}, data, upsert=True)
            return self.find_one(collection, {'_id': doc_id})
        else:
            # Insert new document
            result = table.insert_one(data)
            return self.find_one(collection, {'_id': result.inserted_id})

    def save_many(self, collection: str, data: list[dict]):
        """
        Saves multiple documents to the specified collection.

        Args:
            collection (str): The name of the collection to save the documents.
            data (list[dict]): A list of document data to save.

        Returns:
            The result of the insert operation.
        """
        table = self.get_collection(collection)
        result = table.insert_many(data)
        return result

    def update_one(self, collection: str, query: dict, updates: dict) -> Optional[dict]:
        """
        Updates a single document in the specified collection that matches the query.

        Args:
            collection (str): The name of the collection to update.
            query (dict): The query to find the document to update.
            updates (dict): The updates to apply to the document.

        Returns:
            Optional[dict]: The updated document, or None if the operation fails.
        """
        table = self.get_collection(collection)
        logger.debug(f"Updating collection: {collection} with query: {query}")
        result = table.update_one(filter=query, update=updates)
        logger.debug(f"Update result: modified_count={result.modified_count}")
        return self.find_one(collection, query)

    def update_many(self, collection: str, query: dict, updates: dict) -> int:
        """
        Updates multiple documents in the specified collection that match the query.

        Args:
            collection (str): The name of the collection to update.
            query (dict): The query to find documents to update.
            updates (dict): The updates to apply to the documents.

        Returns:
            int: The number of documents modified.
        """
        table = self.get_collection(collection)
        result = table.update_many(filter=query, update=updates)
        logger.debug(f"Updated {result.modified_count} documents in {collection}")
        return result.modified_count

    def check(self, collection: str, query: dict) -> dict:
        """
        Checks for the existence of a document in the specified collection that matches the query.

        Args:
            collection (str): The name of the collection to check.
            query (dict): The query to filter the documents.

        Returns:
            dict: The found document, or None if no document matches the query.
        """
        table = self.get_collection(collection)
        return table.find_one(query)
    
    def delete_one(self, collection: str, query: dict):
        """
        Deletes a single document from the specified collection that matches the query.

        Args:
            collection (str): The name of the collection to delete from.
            query (dict): The query to find the document to delete.
        """
        table = self.get_collection(collection)
        table.delete_one(query)
    
    def find_paginated(self, collection: str, query: dict, page: int = 1, 
                      page_size: int = 50, sort: list = None) -> dict:
        """
        Paginated queries for large datasets.
        
        Args:
            collection: Collection name
            query: MongoDB query
            page: Page number (1-based)
            page_size: Number of items per page
            sort: List of (field, direction) tuples
            
        Returns:
            Dictionary with results, page info, and total count
        """
        table = self.get_collection(collection)
        skip = (page - 1) * page_size
        
        cursor = table.find(query).skip(skip).limit(page_size)
        if sort:
            cursor = cursor.sort(sort)
            
        results = list(cursor)
        total = table.count_documents(query)
        
        return {
            'results': results,
            'page': page,
            'pages': (total + page_size - 1) // page_size,
            'total': total,
            'has_next': page * page_size < total,
            'has_prev': page > 1
        }
    
    def aggregate(self, collection: str, pipeline: list) -> list:
        """
        Execute aggregation pipeline for complex queries.
        
        Args:
            collection: Collection name
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            List of aggregation results
        """
        table = self.get_collection(collection)
        return list(table.aggregate(pipeline))
    
    def get_collection(self, collection: str):
        """
        Retrieves the specified collection from the database.

        Args:
            collection (str): The name of the collection to retrieve.

        Returns:
            The collection object.
        """
        return self.client[self.database_name][collection]