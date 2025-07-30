import typing

import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy import types as sa_types

__all__ = ["FileColumn", "ImageColumn", "JSONFileColumns", "JSONBFileColumns"]


class FileColumn(sa_types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify a File Column
    """

    impl = sa_types.Text
    cache_ok = True


class ImageColumn(sa_types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify an Image Column

    """

    impl = sa_types.Text
    cache_ok = True

    def __init__(self, thumbnail_size=(20, 20, True), size=(100, 100, True), **kw):
        sa_types.TypeDecorator.__init__(self, **kw)
        self.thumbnail_size = thumbnail_size
        self.size = size


class JSONFileColumns(sa_types.TypeDecorator):
    impl = sa_types.JSON

    def process_bind_param(self, value, dialect):
        # Value must be a list of filenames
        if value:
            if not isinstance(value, list):
                raise ValueError("Value must be a list")
            for v in value:
                if not isinstance(v, str):
                    raise ValueError("Value must be a list of strings")
        return value


class JSONBFileColumns(JSONFileColumns):
    impl = postgresql.JSONB


ExportMode = typing.Literal["simplified", "detailed"]
