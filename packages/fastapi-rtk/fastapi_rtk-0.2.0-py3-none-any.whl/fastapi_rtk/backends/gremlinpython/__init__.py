__all__ = [
    # .column
    "GremlinColumn",
    "GremlinRelationship",
    # .db
    "GremlinQueryBuilder",
    # .exceptions
    "GremlinMissingLabelException",
    "LKMultipleException",
    # .filters
    "GremlinBaseFilter",
    "GremlinFilterTextContains",
    "GremlinFilterEqual",
    "GremlinFilterNotEqual",
    "GremlinFilterStartsWith",
    "GremlinFilterNotStartsWith",
    "GremlinFilterEndsWith",
    "GremlinFilterNotEndsWith",
    "GremlinFilterContains",
    "GremlinFilterNotContains",
    "GremlinFilterGreater",
    "GremlinFilterSmaller",
    "GremlinFilterGreaterEqual",
    "GremlinFilterSmallerEqual",
    "GremlinFilterIn",
    "GremlinFilterConverter",
    # .interface
    "GremlinInterface",
    # .model
    "GremlinModel",
    # .session
    "get_connection_factory",
    "get_graph_traversal_factory",
]

try:
    import gremlin_python

    from .column import *
    from .db import *
    from .exceptions import *
    from .filters import *
    from .interface import *
    from .model import *
    from .session import *


except ImportError:

    class _GremlinImportError:
        def __init__(self, name):
            self._name = name

        def __getattr__(self, attr):
            raise ImportError(
                f"gremlin_python is not installed, but you tried to access '{self._name}.{attr}'. "
                "Please install gremlin_python to use Gremlin features."
            )

        def __call__(self, *args, **kwargs):
            raise ImportError(
                f"gremlin_python is not installed, but you tried to instantiate '{self._name}'. "
                "Please install gremlin_python to use Gremlin features."
            )

    GremlinColumn = _GremlinImportError("GremlinColumn")
    GremlinRelationship = _GremlinImportError("GremlinRelationship")
    GremlinQueryBuilder = _GremlinImportError("GremlinQueryBuilder")
    GremlinMissingLabelException = _GremlinImportError("GremlinMissingLabelException")
    LKMultipleException = _GremlinImportError("LKMultipleException")
    GremlinBaseFilter = _GremlinImportError("GremlinBaseFilter")
    GremlinFilterTextContains = _GremlinImportError("GremlinFilterTextContains")
    GremlinFilterEqual = _GremlinImportError("GremlinFilterEqual")
    GremlinFilterNotEqual = _GremlinImportError("GremlinFilterNotEqual")
    GremlinFilterStartsWith = _GremlinImportError("GremlinFilterStartsWith")
    GremlinFilterNotStartsWith = _GremlinImportError("GremlinFilterNotStartsWith")
    GremlinFilterEndsWith = _GremlinImportError("GremlinFilterEndsWith")
    GremlinFilterNotEndsWith = _GremlinImportError("GremlinFilterNotEndsWith")
    GremlinFilterContains = _GremlinImportError("GremlinFilterContains")
    GremlinFilterNotContains = _GremlinImportError("GremlinFilterNotContains")
    GremlinFilterGreater = _GremlinImportError("GremlinFilterGreater")
    GremlinFilterSmaller = _GremlinImportError("GremlinFilterSmaller")
    GremlinFilterGreaterEqual = _GremlinImportError("GremlinFilterGreaterEqual")
    GremlinFilterSmallerEqual = _GremlinImportError("GremlinFilterSmallerEqual")
    GremlinFilterIn = _GremlinImportError("GremlinFilterIn")
    GremlinFilterConverter = _GremlinImportError("GremlinFilterConverter")
    GremlinInterface = _GremlinImportError("GremlinInterface")
    GremlinModel = _GremlinImportError("GremlinModel")
    get_connection_factory = _GremlinImportError("get_connection_factory")
    get_graph_traversal_factory = _GremlinImportError("get_graph_traversal_factory")
