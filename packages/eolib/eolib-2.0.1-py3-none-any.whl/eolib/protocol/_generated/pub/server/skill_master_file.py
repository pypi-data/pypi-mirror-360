# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .skill_master_record import SkillMasterRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SkillMasterFile:
    """
    Endless Skill Master File
    """
    _byte_size: int = 0
    _skill_masters: tuple[SkillMasterRecord, ...]

    def __init__(self, *, skill_masters: Iterable[SkillMasterRecord]):
        """
        Create a new instance of SkillMasterFile.

        Args:
            skill_masters (Iterable[SkillMasterRecord]): 
        """
        self._skill_masters = tuple(skill_masters)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def skill_masters(self) -> tuple[SkillMasterRecord, ...]:
        return self._skill_masters

    @staticmethod
    def serialize(writer: EoWriter, data: "SkillMasterFile") -> None:
        """
        Serializes an instance of `SkillMasterFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SkillMasterFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("EMF", 3, False)
            if data._skill_masters is None:
                raise SerializationError("skill_masters must be provided.")
            for i in range(len(data._skill_masters)):
                SkillMasterRecord.serialize(writer, data._skill_masters[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SkillMasterFile":
        """
        Deserializes an instance of `SkillMasterFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SkillMasterFile: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            skill_masters = []
            while reader.remaining > 0:
                skill_masters.append(SkillMasterRecord.deserialize(reader))
            result = SkillMasterFile(skill_masters=skill_masters)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SkillMasterFile(byte_size={repr(self._byte_size)}, skill_masters={repr(self._skill_masters)})"
