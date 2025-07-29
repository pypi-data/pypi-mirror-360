from __future__ import annotations
from typing import TypeVar, Generic, Type, Callable
from .base_container_with_collection import ChattyAssetCollectionInterface, ChattyAssetContainerWithCollection, CacheConfig
from ...models.base_models import ChattyAssetModel
from ...models.data_base.mongo_connection import MongoConnection
import logging
import os
logger = logging.getLogger("AssetService")
T = TypeVar('T', bound=ChattyAssetModel)

db_name = os.getenv("MONGO_DB_NAME")
logger.info(f"🚨🚨🚨🚨🚨🚨 db_name: {db_name}")
if db_name is None:
    raise ValueError("MONGO_DB_NAME is not set in the environment variables")


class AssetCollection(Generic[T], ChattyAssetCollectionInterface[T]):
    def __init__(self,
                 collection: str,
                 asset_type: Type[T],
                 connection: MongoConnection,
                 create_instance_method: Callable[[dict], T]):
        logger.debug(f"AssetCollection {self.__class__.__name__} initializing for {collection}")
        super().__init__(
            database=db_name, #type: ignore
            collection=collection,
            connection=connection,
            type=asset_type
        )
        self._create_instance_method = create_instance_method
        logger.debug(f"AssetCollection {self.__class__.__name__} initialized for {collection}")

    def create_instance(self, data: dict) -> T:
        if not isinstance(data, dict):
            raise ValueError(f"Data must be a dictionary, got {type(data)}: {data}")
        return self._create_instance_method(data)

class AssetService(Generic[T], ChattyAssetContainerWithCollection[T]):
    """Generic service for handling CRUD operations for any Chatty asset"""

    def __init__(self,
                 collection_name: str,
                 asset_type: Type[T],
                 connection: MongoConnection,
                 create_instance_method: Callable[[dict], T],
                 cache_config: CacheConfig = CacheConfig.default()):
        logger.debug(f"AssetService {self.__class__.__name__} initializing for {collection_name}")
        asset_collection = AssetCollection(
            collection=collection_name,
            asset_type=asset_type,
            connection=connection,
            create_instance_method=create_instance_method
        )
        super().__init__(
            item_type=asset_type,
            collection=asset_collection,
            cache_config=cache_config,
        )
        logger.debug(f"AssetService {self.__class__.__name__} initialized for {collection_name}")

