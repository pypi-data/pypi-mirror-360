# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopSoldItem:
    """
    A sold item when selling an item to a shop
    """
    _byte_size: int = 0
    _amount: int
    _id: int

    def __init__(self, *, amount: int, id: int):
        """
        Create a new instance of ShopSoldItem.

        Args:
            amount (int): (Value range is 0-4097152080.)
            id (int): (Value range is 0-64008.)
        """
        self._amount = amount
        self._id = id

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def id(self) -> int:
        return self._id

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopSoldItem") -> None:
        """
        Serializes an instance of `ShopSoldItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopSoldItem): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_int(data._amount)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopSoldItem":
        """
        Deserializes an instance of `ShopSoldItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopSoldItem: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            amount = reader.get_int()
            id = reader.get_short()
            result = ShopSoldItem(amount=amount, id=id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopSoldItem(byte_size={repr(self._byte_size)}, amount={repr(self._amount)}, id={repr(self._id)})"
