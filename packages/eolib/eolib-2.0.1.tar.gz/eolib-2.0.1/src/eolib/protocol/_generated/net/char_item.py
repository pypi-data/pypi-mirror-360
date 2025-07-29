# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class CharItem:
    """
    An item reference with a 1-byte amount.
    Used for craft ingredients.
    """
    _byte_size: int = 0
    _id: int
    _amount: int

    def __init__(self, *, id: int, amount: int):
        """
        Create a new instance of CharItem.

        Args:
            id (int): (Value range is 0-64008.)
            amount (int): (Value range is 0-252.)
        """
        self._id = id
        self._amount = amount

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def id(self) -> int:
        return self._id

    @property
    def amount(self) -> int:
        return self._amount

    @staticmethod
    def serialize(writer: EoWriter, data: "CharItem") -> None:
        """
        Serializes an instance of `CharItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharItem): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_char(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharItem":
        """
        Deserializes an instance of `CharItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharItem: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            id = reader.get_short()
            amount = reader.get_char()
            result = CharItem(id=id, amount=amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharItem(byte_size={repr(self._byte_size)}, id={repr(self._id)}, amount={repr(self._amount)})"
