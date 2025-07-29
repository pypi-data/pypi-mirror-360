# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .drop_record import DropRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class DropNpcRecord:
    """
    Record of potential drops from an NPC
    """
    _byte_size: int = 0
    _npc_id: int
    _drops_count: int
    _drops: tuple[DropRecord, ...]

    def __init__(self, *, npc_id: int, drops: Iterable[DropRecord]):
        """
        Create a new instance of DropNpcRecord.

        Args:
            npc_id (int): (Value range is 0-64008.)
            drops (Iterable[DropRecord]): (Length must be 64008 or less.)
        """
        self._npc_id = npc_id
        self._drops = tuple(drops)
        self._drops_count = len(self._drops)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_id(self) -> int:
        return self._npc_id

    @property
    def drops(self) -> tuple[DropRecord, ...]:
        return self._drops

    @staticmethod
    def serialize(writer: EoWriter, data: "DropNpcRecord") -> None:
        """
        Serializes an instance of `DropNpcRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (DropNpcRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_id is None:
                raise SerializationError("npc_id must be provided.")
            writer.add_short(data._npc_id)
            if data._drops_count is None:
                raise SerializationError("drops_count must be provided.")
            writer.add_short(data._drops_count)
            if data._drops is None:
                raise SerializationError("drops must be provided.")
            if len(data._drops) > 64008:
                raise SerializationError(f"Expected length of drops to be 64008 or less, got {len(data._drops)}.")
            for i in range(data._drops_count):
                DropRecord.serialize(writer, data._drops[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "DropNpcRecord":
        """
        Deserializes an instance of `DropNpcRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            DropNpcRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_id = reader.get_short()
            drops_count = reader.get_short()
            drops = []
            for i in range(drops_count):
                drops.append(DropRecord.deserialize(reader))
            result = DropNpcRecord(npc_id=npc_id, drops=drops)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"DropNpcRecord(byte_size={repr(self._byte_size)}, npc_id={repr(self._npc_id)}, drops={repr(self._drops)})"
