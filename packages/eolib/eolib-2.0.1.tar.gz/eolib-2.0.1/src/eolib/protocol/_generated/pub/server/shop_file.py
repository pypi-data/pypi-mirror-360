# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .shop_record import ShopRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopFile:
    """
    Endless Shop File
    """
    _byte_size: int = 0
    _shops: tuple[ShopRecord, ...]

    def __init__(self, *, shops: Iterable[ShopRecord]):
        """
        Create a new instance of ShopFile.

        Args:
            shops (Iterable[ShopRecord]): 
        """
        self._shops = tuple(shops)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def shops(self) -> tuple[ShopRecord, ...]:
        return self._shops

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopFile") -> None:
        """
        Serializes an instance of `ShopFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("ESF", 3, False)
            if data._shops is None:
                raise SerializationError("shops must be provided.")
            for i in range(len(data._shops)):
                ShopRecord.serialize(writer, data._shops[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopFile":
        """
        Deserializes an instance of `ShopFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopFile: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            shops = []
            while reader.remaining > 0:
                shops.append(ShopRecord.deserialize(reader))
            result = ShopFile(shops=shops)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopFile(byte_size={repr(self._byte_size)}, shops={repr(self._shops)})"
