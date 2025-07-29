# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .eif_record import EifRecord
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Eif:
    """
    Endless Item File
    """
    _byte_size: int = 0
    _rid: tuple[int, ...]
    _total_items_count: int
    _version: int
    _items: tuple[EifRecord, ...]

    def __init__(self, *, rid: Iterable[int], total_items_count: int, version: int, items: Iterable[EifRecord]):
        """
        Create a new instance of Eif.

        Args:
            rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
            total_items_count (int): (Value range is 0-64008.)
            version (int): (Value range is 0-252.)
            items (Iterable[EifRecord]): 
        """
        self._rid = tuple(rid)
        self._total_items_count = total_items_count
        self._version = version
        self._items = tuple(items)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rid(self) -> tuple[int, ...]:
        return self._rid

    @property
    def total_items_count(self) -> int:
        return self._total_items_count

    @property
    def version(self) -> int:
        return self._version

    @property
    def items(self) -> tuple[EifRecord, ...]:
        return self._items

    @staticmethod
    def serialize(writer: EoWriter, data: "Eif") -> None:
        """
        Serializes an instance of `Eif` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Eif): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("EIF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._total_items_count is None:
                raise SerializationError("total_items_count must be provided.")
            writer.add_short(data._total_items_count)
            if data._version is None:
                raise SerializationError("version must be provided.")
            writer.add_char(data._version)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                EifRecord.serialize(writer, data._items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Eif":
        """
        Deserializes an instance of `Eif` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Eif: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            rid = []
            for i in range(2):
                rid.append(reader.get_short())
            total_items_count = reader.get_short()
            version = reader.get_char()
            items = []
            while reader.remaining > 0:
                items.append(EifRecord.deserialize(reader))
            result = Eif(rid=rid, total_items_count=total_items_count, version=version, items=items)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Eif(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, total_items_count={repr(self._total_items_count)}, version={repr(self._version)}, items={repr(self._items)})"
