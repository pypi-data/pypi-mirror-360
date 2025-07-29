# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .ecf_record import EcfRecord
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Ecf:
    """
    Endless Class File
    """
    _byte_size: int = 0
    _rid: tuple[int, ...]
    _total_classes_count: int
    _version: int
    _classes: tuple[EcfRecord, ...]

    def __init__(self, *, rid: Iterable[int], total_classes_count: int, version: int, classes: Iterable[EcfRecord]):
        """
        Create a new instance of Ecf.

        Args:
            rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
            total_classes_count (int): (Value range is 0-64008.)
            version (int): (Value range is 0-252.)
            classes (Iterable[EcfRecord]): 
        """
        self._rid = tuple(rid)
        self._total_classes_count = total_classes_count
        self._version = version
        self._classes = tuple(classes)

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
    def total_classes_count(self) -> int:
        return self._total_classes_count

    @property
    def version(self) -> int:
        return self._version

    @property
    def classes(self) -> tuple[EcfRecord, ...]:
        return self._classes

    @staticmethod
    def serialize(writer: EoWriter, data: "Ecf") -> None:
        """
        Serializes an instance of `Ecf` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Ecf): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("ECF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._total_classes_count is None:
                raise SerializationError("total_classes_count must be provided.")
            writer.add_short(data._total_classes_count)
            if data._version is None:
                raise SerializationError("version must be provided.")
            writer.add_char(data._version)
            if data._classes is None:
                raise SerializationError("classes must be provided.")
            for i in range(len(data._classes)):
                EcfRecord.serialize(writer, data._classes[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Ecf":
        """
        Deserializes an instance of `Ecf` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Ecf: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            rid = []
            for i in range(2):
                rid.append(reader.get_short())
            total_classes_count = reader.get_short()
            version = reader.get_char()
            classes = []
            while reader.remaining > 0:
                classes.append(EcfRecord.deserialize(reader))
            result = Ecf(rid=rid, total_classes_count=total_classes_count, version=version, classes=classes)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Ecf(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, total_classes_count={repr(self._total_classes_count)}, version={repr(self._version)}, classes={repr(self._classes)})"
