import fastapi
import gremlin_python.driver.driver_remote_connection
import gremlin_python.process.anonymous_traversal

from ...const import logger

try:
    import janusgraph_python.driver.serializer

    serializer = janusgraph_python.driver.serializer
except ImportError:
    logger.warning(
        "janusgraph_python is not installed. Some Gremlin features may not work as expected."
    )
    serializer = None

from ...globals import g

__all__ = ["get_connection_factory", "get_graph_traversal_factory"]


def get_connection_factory(keep_open=False):
    """
    Returns a FastAPI dependency that provides a Gremlin connection.

    Args:
        keep_open (bool, optional): Whether to keep the connection open after use. Defaults to False.

    Returns:
        Callable: A function that yields a Gremlin connection.
    """

    def get_connection():
        url, graph_object = g.config["GREMLIN_URL"]
        connection = (
            gremlin_python.driver.driver_remote_connection.DriverRemoteConnection(
                url,
                graph_object,
                # session=True, #! When true, can not add Edge
                message_serializer=serializer.JanusGraphSONSerializersV3d0()
                if serializer
                else None,
            )
        )
        try:
            if keep_open:
                logger.warning(
                    f"Connection {connection} is kept open. Make sure to close it manually when done."
                )
            yield connection
        except Exception:
            connection.rollback()
            raise
        finally:
            if keep_open:
                return
            connection.close()

    return get_connection


def get_graph_traversal_factory(keep_open=False):
    """
    Returns a FastAPI dependency that provides a Gremlin graph traversal.

    Args:
        keep_open (bool, optional): Whether to keep the connection open after use. Defaults to False.

    Returns:
        Callable: A function that yields a Gremlin graph traversal.
    """

    def get_graph_traversal(
        connection: gremlin_python.driver.driver_remote_connection.DriverRemoteConnection = fastapi.Depends(
            get_connection_factory(keep_open)
        ),
    ):
        traversal = gremlin_python.process.anonymous_traversal.traversal().withRemote(
            connection
        )
        traversal.remote_connection = connection
        return traversal

    return get_graph_traversal
