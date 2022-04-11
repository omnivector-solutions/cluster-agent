from pydantic import BaseModel


class BaseDataStoreOps:
    """
    Base class to implement the interface to push data to any datastore.

    Define two methods that must be overridden:

    - connect(): Connect to the datastore, e.g.

    from elasticsearch_dsl import connections
    connections.create_connection(
        hosts=[http://osl:rats@localhost:9200],
        verify_certs=False,
    )

    - push(): Push data to the desired datastore, e.g.

    def push(self):
        # send data to elasticsearch
        DocumentInstance(
            _id="asb1249d"
            cluster_agent_is="awesome",
            omnivector="solutions"
        ).save(refresh=True)
    """

    settings: BaseModel = None
    database_name: str = None

    def _connect(self):
        """
        Provide a method to connect against the datastore
        """
        raise NotImplementedError

    def _push(self):
        """
        Provide a method to push the data to the datastore

        Usage example calling more than one operation:

        def _push_something(self):
            # logic here

        def _push_anything_else(self):
            # logic here

        def push(self):
            self._push_something()
            self._push_anything_else()
        """
        raise NotImplementedError

    @classmethod
    def run(cls):
        """Run all needed operations"""
        cls._connect()
        cls._push()
