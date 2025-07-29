# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class DropRecord:
    """
    Record of an item an NPC can drop when killed
    """
    _byte_size: int = 0
    _item_id: int
    _min_amount: int
    _max_amount: int
    _rate: int

    def __init__(self, *, item_id: int, min_amount: int, max_amount: int, rate: int):
        """
        Create a new instance of DropRecord.

        Args:
            item_id (int): (Value range is 0-64008.)
            min_amount (int): (Value range is 0-16194276.)
            max_amount (int): (Value range is 0-16194276.)
            rate (int): Chance (x in 64,000) of the item being dropped (Value range is 0-64008.)
        """
        self._item_id = item_id
        self._min_amount = min_amount
        self._max_amount = max_amount
        self._rate = rate

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def min_amount(self) -> int:
        return self._min_amount

    @property
    def max_amount(self) -> int:
        return self._max_amount

    @property
    def rate(self) -> int:
        """
        Chance (x in 64,000) of the item being dropped
        """
        return self._rate

    @staticmethod
    def serialize(writer: EoWriter, data: "DropRecord") -> None:
        """
        Serializes an instance of `DropRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (DropRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._min_amount is None:
                raise SerializationError("min_amount must be provided.")
            writer.add_three(data._min_amount)
            if data._max_amount is None:
                raise SerializationError("max_amount must be provided.")
            writer.add_three(data._max_amount)
            if data._rate is None:
                raise SerializationError("rate must be provided.")
            writer.add_short(data._rate)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "DropRecord":
        """
        Deserializes an instance of `DropRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            DropRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item_id = reader.get_short()
            min_amount = reader.get_three()
            max_amount = reader.get_three()
            rate = reader.get_short()
            result = DropRecord(item_id=item_id, min_amount=min_amount, max_amount=max_amount, rate=rate)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"DropRecord(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, min_amount={repr(self._min_amount)}, max_amount={repr(self._max_amount)}, rate={repr(self._rate)})"
