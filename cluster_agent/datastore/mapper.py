"""Base module to map all classes that makes operations against any sort of database"""
import inspect

from cluster_agent.datastore import BaseDataStoreOps
from cluster_agent.datastore.interfaces import operations
from cluster_agent.utils.logging import logger


class DataStoreMapper:
    def __init__(self) -> None:

        self._ops_classes = list()

        # iterate over every ops class
        for class_name, obj in inspect.getmembers(operations, inspect.isclass):
            if issubclass(obj, BaseDataStoreOps) and obj.settings is not None:
                logger.debug(f"Found {class_name} operation class. Database: {obj.database_name}")
                self._ops_classes.append(obj)
                logger.debug(f"Added {class_name} to ops_classes list")

    def call_ops(self) -> None:
        logger.debug(self._ops_classes)
        for ops_class in self._ops_classes:
            logger.debug(f"Calling `run` method from {ops_class.__name__}")
            ops_class.run()


async def push_to_datastores():
    """
    Instantiates the DataStoreMapper class and call the `call_ops` method.
    """
    data_store_mapper = DataStoreMapper()
    data_store_mapper.call_ops()
