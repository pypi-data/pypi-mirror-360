import typing

from ...bases.model import BasicModel
from .column import UNSET, GenericColumn, _PKAutoIncrement
from .exceptions import (
    ColumnNotSetException,
    MultipleColumnsException,
    PKMissingException,
    PKMultipleException,
)

if typing.TYPE_CHECKING:
    from .session import Table

__all__ = ["GenericModel"]


class GenericModel(BasicModel):
    """
    GenericModel is a base class for all models that does not use SQLAlchemy, but want to behave like one.

    Attributes:
        __table__: The table object that can be used as a way to check whether the model is queried from a table.
    """

    pk: str = None
    properties: dict[str, GenericColumn] = None
    columns: list[str] = None

    __table__: "Table | None" = None
    __ignore_init__: bool

    def __init_subclass__(cls) -> None:
        if getattr(cls, "__ignore_init__", False):
            # If the child class defines '__ignore_init__', skip the parent's logic
            return

        # Take all the columns from the base classes, this allow the use of multiple inheritance
        base_list = list(cls.__bases__)
        base_list.append(cls)
        self_attr = {}
        for base in base_list:
            self_attr.update(
                {k: v for k, v in vars(base).items() if isinstance(v, GenericColumn)}
            )

        cls.properties = {}
        cls.columns = []

        for key, value in self_attr.items():
            if isinstance(value, GenericColumn):
                cls.properties[key] = value
                cls.columns.append(key)

                if value.primary_key:
                    if cls.pk and cls.pk != key:
                        raise PKMultipleException(
                            cls.__name__, "Only one primary key is allowed"
                        )
                    cls.pk = key

        if not cls.pk:
            raise PKMissingException(cls.__name__, "Primary key is missing")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.columns:
                continue
            setattr(self, key, value)

    def get_pk(self) -> str | int | _PKAutoIncrement:
        """
        Get the primary key of the model.

        Returns:
            str | int | _PKAutoIncrement: The primary key of the model.
        """
        return getattr(self, self.pk)

    def set_pk(self, value: str | int):
        """
        Set the primary key of the model.

        Args:
            value (str | int): The value to set as the primary key.
        """
        setattr(self, self.pk, value)

    def get_col_type(self, col_name: str):
        return self.properties[col_name].col_type

    def update(self, data):
        super().update(data)

        # Check if the model is valid
        self.is_model_valid()

    def is_model_valid(self):
        """
        Check if the model is valid. A model is valid if all the columns are set.

        Raises:
            MultipleColumnsException: If any column is not set.
        """
        errors: list[Exception] = []
        for key in self.columns:
            if getattr(self, key) is UNSET:
                errors.append(ColumnNotSetException(self, f"Column {key} is not set"))

        if errors:
            # Rollback to last valid state
            last_valid_data = getattr(self, "_last_valid_state", {})
            self.update(last_valid_data)
            raise MultipleColumnsException(self, errors)

        # Save last valid state
        self._last_valid_state = {key: getattr(self, key) for key in self.columns}

    @classmethod
    def get_pk_attrs(cls):
        return [cls.pk]

    def __repr__(self):
        return str(self)

    def __str__(self):
        str = self.__class__.__name__ + "=("
        for col in self.columns:
            str += "{0}:{1};".format(col, getattr(self, col))
        str += ")"
        return str
