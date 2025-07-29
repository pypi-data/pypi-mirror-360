# -*- coding: utf-8 -*-
# @Author: Cursor
# @Date: 2025-02-12
# @Last Modified by: Gemini
# @Last Modified time: 2025-07-01

import logging
from typing import List, Dict, Union, Optional
from langchain_milvus import Zilliz
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureOpenAIEmbeddings
from pymilvus import MilvusClient

from crewplus.services.init_services import get_model_balancer
from crewplus.vectorstores.milvus.schema_milvus import SchemaMilvus

class VDBService(object):
    """
    A service to manage connections to Milvus/Zilliz vector databases and embedding models.

    This service centralizes the configuration and instantiation of the Milvus client
    and provides helper methods to get embedding functions and vector store instances.

    Args:
        settings (dict): A dictionary containing configuration for the vector store
                         and embedding models.
        schema (str, optional): The schema definition for a collection. Defaults to None.
        logger (logging.Logger, optional): An optional logger instance. Defaults to None.

    Raises:
        ValueError: If required configurations are missing from the settings dictionary.
        NotImplementedError: If an unsupported provider is specified.
        RuntimeError: If the MilvusClient fails to initialize after a retry.

    Example:
        >>> settings = {
        ...     "embedder": {
        ...         "provider": "azure-openai",
        ...         "config": {
        ...             "model": "text-embedding-3-small",
        ...             "api_version": "2023-05-15",
        ...             "api_key": "YOUR_AZURE_OPENAI_KEY",
        ...             "openai_base_url": "YOUR_AZURE_OPENAI_ENDPOINT",
        ...             "embedding_dims": 1536
        ...         }
        ...     },
        ...     "vector_store": {
        ...         "provider": "milvus",
        ...         "config": {
        ...             "host": "localhost",
        ...             "port": 19530,
        ...             "user": "root",
        ...             "password": "password",
        ...             "db_name": "default"
        ...         }
        ...     },
        ...     "index_params": {
        ...         "metric_type": "L2",
        ...         "index_type": "AUTOINDEX",
        ...         "params": {}
        ...     }
        ... }
        >>> vdb_service = VDBService(settings=settings)
        >>> # Get the raw Milvus client
        >>> client = vdb_service.get_vector_client()
        >>> print(client.list_collections())
        >>> # Get an embedding function
        >>> embeddings = vdb_service.get_embeddings()
        >>> print(embeddings)
        >>> # Get a LangChain vector store instance (will be cached)
        >>> vector_store = vdb_service.get_vector_store(collection_name="my_collection")
        >>> print(vector_store)
        >>> same_vector_store = vdb_service.get_vector_store(collection_name="my_collection")
        >>> assert vector_store is same_vector_store
    """
    _client: MilvusClient
    _instances: Dict[str, Zilliz] = {}

    schema: str
    embedding_function: Embeddings
    index_params: dict
    connection_args: dict
    settings: dict
    
    def __init__(self, settings: dict, schema: str = None, logger: logging.Logger = None):
        """
        Initializes the VDBService.
        
        Args:
            settings (dict): Configuration dictionary for the service.
            schema (str, optional): Default schema for new collections. Defaults to None.
            logger (logging.Logger, optional): Logger instance. Defaults to None.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.settings = settings

        vector_store_settings = self.settings.get("vector_store")
        if not vector_store_settings:
            msg = "'vector_store' not found in settings"
            self.logger.error(msg)
            raise ValueError(msg)

        provider = vector_store_settings.get("provider")
        self.connection_args = vector_store_settings.get("config")

        if not provider or not self.connection_args:
            msg = "'provider' or 'config' not found in 'vector_store' settings"
            self.logger.error(msg)
            raise ValueError(msg)

        self._client = self._initialize_milvus_client(provider)

        self.schema = schema
        self.index_params = self.settings.get("index_params")
        
        self.logger.info("VDBService initialized successfully")

    def _initialize_milvus_client(self, provider: str) -> MilvusClient:
        """
        Initializes and returns a MilvusClient with a retry mechanism.
        """
        client_args = {}
        if provider == "milvus":
            host = self.connection_args.get("host", "localhost")
            port = self.connection_args.get("port", 19530)
            
            # Use https for remote hosts, and http for local connections.
            scheme = "https" if host not in ["localhost", "127.0.0.1"] else "http"
            uri = f"{scheme}://{host}:{port}"
            
            client_args = {
                "uri": uri,
                "user": self.connection_args.get("user"),
                "password": self.connection_args.get("password"),
                "db_name": self.connection_args.get("db_name")
            }
            # Filter out None values to use client defaults
            client_args = {k: v for k, v in client_args.items() if v is not None}

        elif provider == "zilliz":
            client_args = self.connection_args
        else:
            self.logger.error(f"Unsupported vector store provider: {provider}")
            raise NotImplementedError(f"Vector store provider '{provider}' is not supported.")

        try:
            # First attempt to connect
            return MilvusClient(**client_args)
        except Exception as e:
            self.logger.error(f"Failed to initialize MilvusClient, trying again. Error: {e}")
            # Second attempt after failure
            try:
                return MilvusClient(**client_args)
            except Exception as e_retry:
                self.logger.error(f"Failed to initialize MilvusClient on retry. Final error: {e_retry}")
                raise RuntimeError(f"Could not initialize MilvusClient after retry: {e_retry}")

    def get_vector_client(self) -> MilvusClient:
        """
        Returns the active MilvusClient instance.

        Returns:
            MilvusClient: The initialized client for interacting with the vector database.
        """
        return self._client

    def get_embeddings(self, from_model_balancer: bool = False, model_type: Optional[str] = "embedding-large") -> Embeddings:
        """
        Gets an embedding function, either from the model balancer or directly from settings.

        Args:
            from_model_balancer (bool): If True, uses the central model balancer service.
                                        If False, creates a new instance based on 'embedder' settings.
            model_type (str, optional): The type of model to get from the balancer. Defaults to "embedding-large".

        Returns:
            Embeddings: An instance of a LangChain embedding model.
        """
        if from_model_balancer:
            model_balancer = get_model_balancer()
            return model_balancer.get_model(model_type=model_type)

        embedder_config = self.settings.get("embedder")
        if not embedder_config:
            self.logger.error("'embedder' configuration not found in settings.")
            raise ValueError("'embedder' configuration not found in settings.")

        provider = embedder_config.get("provider")
        config = embedder_config.get("config")

        if not provider or not config:
            self.logger.error("Embedder 'provider' or 'config' not found in settings.")
            raise ValueError("Embedder 'provider' or 'config' not found in settings.")

        if provider == "azure-openai":
            # Map the settings config to AzureOpenAIEmbeddings parameters.
            azure_config = {
                "azure_deployment": config.get("model"),
                "openai_api_version": config.get("api_version"),
                "api_key": config.get("api_key"),
                "azure_endpoint": config.get("openai_base_url"),
                "dimensions": config.get("embedding_dims"),
                "chunk_size": config.get("chunk_size", 16),
                "request_timeout": config.get("request_timeout", 60),
                "max_retries": config.get("max_retries", 2)
            }
            # Filter out None values to use client defaults.
            azure_config = {k: v for k, v in azure_config.items() if v is not None}
            
            return AzureOpenAIEmbeddings(**azure_config)
        else:
            self.logger.error(f"Unsupported embedding provider: {provider}")
            raise NotImplementedError(f"Embedding provider '{provider}' is not supported yet.")
        
    def get_vector_store(self, collection_name: str, embeddings: Embeddings = None, metric_type: str = "L2") -> Zilliz:
        """
        Gets a vector store instance, creating it if it doesn't exist for the collection.

        This method caches instances by collection name to avoid re-instantiation.

        Args:
            collection_name (str): The name of the collection in the vector database.
            embeddings (Embeddings, optional): An embedding model instance. If None, one is created.
            metric_type (str): The distance metric for the index. Defaults to "L2".

        Returns:
            Zilliz: LangChain Zilliz instance, which is compatible with both Zilliz and Milvus.
        """
        if not collection_name:
            self.logger.error("get_vector_store called with no collection_name.")
            raise ValueError("collection_name must be provided.")

        # Return the cached instance if it already exists.
        if collection_name in self._instances:
            self.logger.info(f"Returning existing vector store instance for collection: {collection_name}")
            return self._instances[collection_name]

        self.logger.info(f"Creating new vector store instance for collection: {collection_name}")
        if embeddings is None:
            embeddings = self.get_embeddings()

        index_params = self.index_params or {
            "metric_type": metric_type,
            "index_type": "AUTOINDEX",
            "params": {}
        }
        
        vdb = Zilliz(
            embedding_function=embeddings,
            collection_name=collection_name,
            connection_args=self.connection_args,
            index_params=index_params
        )

        # Cache the newly created instance.
        self._instances[collection_name] = vdb

        return vdb

    def delete_old_indexes(self, url: str = None, vdb: Zilliz = None) -> None:
        """ Delete old indexes of the same source_url

        Args:
            url (str): source url
        """
        if url is None or vdb is None:
            return

        # Delete indexes of the same source_url
        expr = "source in [\"" + url + "\"]"
        pks = vdb.get_pks(expr)

        # Delete entities by pks
        if pks is not None and len(pks) > 0 :
            old_items = vdb.delete(pks)
            self.logger.info("ingesting document -- delete old indexes -- " + str(old_items))

    def delete_old_indexes_by_id(self, id: str = None, vdb: Zilliz = None) -> None:
        """ Delete old indexes of the same source_id

        Args:
            id (str): source id
        """
        self.logger.info(f"Delete old indexes of the same source_id:{id}")

        if id is None or vdb is None:
            return

        # Delete indexes of the same source_id
        expr = "source_id in [\"" + id + "\"]"
        pks = vdb.get_pks(expr)

        # Delete entities by pks
        if pks is not None and len(pks) > 0 :
            old_items = vdb.delete(pks)
            self.logger.info("ingesting document -- delete old indexes -- " + str(old_items))

    def drop_collection(self, collection_name: str) -> None:
        """
        Deletes a collection from the vector database and removes it from the cache.

        Args:
            collection_name (str): The name of the collection to drop.

        Raises:
            ValueError: If collection_name is not provided.
            RuntimeError: If the operation fails on the database side.
        """
        if not collection_name:
            self.logger.error("drop_collection called without a collection_name.")
            raise ValueError("collection_name must be provided.")

        self.logger.info(f"Attempting to drop collection: {collection_name}")

        try:
            client = self.get_vector_client()
            client.drop_collection(collection_name=collection_name)
            self.logger.info(f"Successfully dropped collection: {collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to drop collection '{collection_name}': {e}")
            raise RuntimeError(f"An error occurred while dropping collection '{collection_name}'.") from e
        finally:
            # Whether successful or not, remove the stale instance from the cache.
            if collection_name in self._instances:
                del self._instances[collection_name]
                self.logger.info(f"Removed '{collection_name}' from instance cache.")

    def delete_data_by_filter(self, collection_name: str = None, filter: str = None) -> None:
        """ Delete a collection

        Args:
            collection_name (str): scollection_name
        """
        self.logger.info(f"drop a collection by name:{collection_name}")

        try:
            client=self.get_vector_client()
            if collection_name is None or client is None or filter is None:
                return RuntimeError(f"collection_name must be not null or check out your client to link milvus")
            client.delete(collection_name=collection_name, filter=filter)
        except Exception as e:
            raise RuntimeError(f"delete collection data failed: {str(e)}")