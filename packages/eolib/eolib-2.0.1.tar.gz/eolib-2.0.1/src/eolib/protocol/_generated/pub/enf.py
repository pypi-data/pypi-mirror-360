# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .enf_record import EnfRecord
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Enf:
    """
    Endless NPC File
    """
    _byte_size: int = 0
    _rid: tuple[int, ...]
    _total_npcs_count: int
    _version: int
    _npcs: tuple[EnfRecord, ...]

    def __init__(self, *, rid: Iterable[int], total_npcs_count: int, version: int, npcs: Iterable[EnfRecord]):
        """
        Create a new instance of Enf.

        Args:
            rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
            total_npcs_count (int): (Value range is 0-64008.)
            version (int): (Value range is 0-252.)
            npcs (Iterable[EnfRecord]): 
        """
        self._rid = tuple(rid)
        self._total_npcs_count = total_npcs_count
        self._version = version
        self._npcs = tuple(npcs)

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
    def total_npcs_count(self) -> int:
        return self._total_npcs_count

    @property
    def version(self) -> int:
        return self._version

    @property
    def npcs(self) -> tuple[EnfRecord, ...]:
        return self._npcs

    @staticmethod
    def serialize(writer: EoWriter, data: "Enf") -> None:
        """
        Serializes an instance of `Enf` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Enf): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("ENF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._total_npcs_count is None:
                raise SerializationError("total_npcs_count must be provided.")
            writer.add_short(data._total_npcs_count)
            if data._version is None:
                raise SerializationError("version must be provided.")
            writer.add_char(data._version)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            for i in range(len(data._npcs)):
                EnfRecord.serialize(writer, data._npcs[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Enf":
        """
        Deserializes an instance of `Enf` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Enf: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            rid = []
            for i in range(2):
                rid.append(reader.get_short())
            total_npcs_count = reader.get_short()
            version = reader.get_char()
            npcs = []
            while reader.remaining > 0:
                npcs.append(EnfRecord.deserialize(reader))
            result = Enf(rid=rid, total_npcs_count=total_npcs_count, version=version, npcs=npcs)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Enf(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, total_npcs_count={repr(self._total_npcs_count)}, version={repr(self._version)}, npcs={repr(self._npcs)})"
