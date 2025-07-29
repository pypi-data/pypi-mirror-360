# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .skill_master_skill_record import SkillMasterSkillRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SkillMasterRecord:
    """
    Record of Skill Master data in an Endless Skill Master File
    """
    _byte_size: int = 0
    _behavior_id: int
    _name_length: int
    _name: str
    _min_level: int
    _max_level: int
    _class_requirement: int
    _skills_count: int
    _skills: tuple[SkillMasterSkillRecord, ...]

    def __init__(self, *, behavior_id: int, name: str, min_level: int, max_level: int, class_requirement: int, skills: Iterable[SkillMasterSkillRecord]):
        """
        Create a new instance of SkillMasterRecord.

        Args:
            behavior_id (int): Behavior ID of the Skill Master NPC (Value range is 0-64008.)
            name (str): (Length must be 252 or less.)
            min_level (int): Minimum level required to use this Skill Master (Value range is 0-252.)
            max_level (int): Maximum level allowed to use this Skill Master (Value range is 0-252.)
            class_requirement (int): Class required to use this Skill Master (Value range is 0-252.)
            skills (Iterable[SkillMasterSkillRecord]): (Length must be 64008 or less.)
        """
        self._behavior_id = behavior_id
        self._name = name
        self._name_length = len(self._name)
        self._min_level = min_level
        self._max_level = max_level
        self._class_requirement = class_requirement
        self._skills = tuple(skills)
        self._skills_count = len(self._skills)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        """
        Behavior ID of the Skill Master NPC
        """
        return self._behavior_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def min_level(self) -> int:
        """
        Minimum level required to use this Skill Master
        """
        return self._min_level

    @property
    def max_level(self) -> int:
        """
        Maximum level allowed to use this Skill Master
        """
        return self._max_level

    @property
    def class_requirement(self) -> int:
        """
        Class required to use this Skill Master
        """
        return self._class_requirement

    @property
    def skills(self) -> tuple[SkillMasterSkillRecord, ...]:
        return self._skills

    @staticmethod
    def serialize(writer: EoWriter, data: "SkillMasterRecord") -> None:
        """
        Serializes an instance of `SkillMasterRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SkillMasterRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._min_level is None:
                raise SerializationError("min_level must be provided.")
            writer.add_char(data._min_level)
            if data._max_level is None:
                raise SerializationError("max_level must be provided.")
            writer.add_char(data._max_level)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_char(data._class_requirement)
            if data._skills_count is None:
                raise SerializationError("skills_count must be provided.")
            writer.add_short(data._skills_count)
            if data._skills is None:
                raise SerializationError("skills must be provided.")
            if len(data._skills) > 64008:
                raise SerializationError(f"Expected length of skills to be 64008 or less, got {len(data._skills)}.")
            for i in range(data._skills_count):
                SkillMasterSkillRecord.serialize(writer, data._skills[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SkillMasterRecord":
        """
        Deserializes an instance of `SkillMasterRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SkillMasterRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            behavior_id = reader.get_short()
            name_length = reader.get_char()
            name = reader.get_fixed_string(name_length, False)
            min_level = reader.get_char()
            max_level = reader.get_char()
            class_requirement = reader.get_char()
            skills_count = reader.get_short()
            skills = []
            for i in range(skills_count):
                skills.append(SkillMasterSkillRecord.deserialize(reader))
            result = SkillMasterRecord(behavior_id=behavior_id, name=name, min_level=min_level, max_level=max_level, class_requirement=class_requirement, skills=skills)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SkillMasterRecord(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, name={repr(self._name)}, min_level={repr(self._min_level)}, max_level={repr(self._max_level)}, class_requirement={repr(self._class_requirement)}, skills={repr(self._skills)})"
