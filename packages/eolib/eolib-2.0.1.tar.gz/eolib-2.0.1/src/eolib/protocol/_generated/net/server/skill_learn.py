# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .skill_stat_requirements import SkillStatRequirements
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SkillLearn:
    """
    A skill that can be learned from a skill master NPC
    """
    _byte_size: int = 0
    _id: int
    _level_requirement: int
    _class_requirement: int
    _cost: int
    _skill_requirements: tuple[int, ...]
    _stat_requirements: SkillStatRequirements

    def __init__(self, *, id: int, level_requirement: int, class_requirement: int, cost: int, skill_requirements: Iterable[int], stat_requirements: SkillStatRequirements):
        """
        Create a new instance of SkillLearn.

        Args:
            id (int): (Value range is 0-64008.)
            level_requirement (int): (Value range is 0-252.)
            class_requirement (int): (Value range is 0-252.)
            cost (int): (Value range is 0-4097152080.)
            skill_requirements (Iterable[int]): (Length must be `4`.) (Element value range is 0-64008.)
            stat_requirements (SkillStatRequirements): 
        """
        self._id = id
        self._level_requirement = level_requirement
        self._class_requirement = class_requirement
        self._cost = cost
        self._skill_requirements = tuple(skill_requirements)
        self._stat_requirements = stat_requirements

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
    def level_requirement(self) -> int:
        return self._level_requirement

    @property
    def class_requirement(self) -> int:
        return self._class_requirement

    @property
    def cost(self) -> int:
        return self._cost

    @property
    def skill_requirements(self) -> tuple[int, ...]:
        return self._skill_requirements

    @property
    def stat_requirements(self) -> SkillStatRequirements:
        return self._stat_requirements

    @staticmethod
    def serialize(writer: EoWriter, data: "SkillLearn") -> None:
        """
        Serializes an instance of `SkillLearn` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SkillLearn): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._level_requirement is None:
                raise SerializationError("level_requirement must be provided.")
            writer.add_char(data._level_requirement)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_char(data._class_requirement)
            if data._cost is None:
                raise SerializationError("cost must be provided.")
            writer.add_int(data._cost)
            if data._skill_requirements is None:
                raise SerializationError("skill_requirements must be provided.")
            if len(data._skill_requirements) != 4:
                raise SerializationError(f"Expected length of skill_requirements to be exactly 4, got {len(data._skill_requirements)}.")
            for i in range(4):
                writer.add_short(data._skill_requirements[i])
            if data._stat_requirements is None:
                raise SerializationError("stat_requirements must be provided.")
            SkillStatRequirements.serialize(writer, data._stat_requirements)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SkillLearn":
        """
        Deserializes an instance of `SkillLearn` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SkillLearn: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            id = reader.get_short()
            level_requirement = reader.get_char()
            class_requirement = reader.get_char()
            cost = reader.get_int()
            skill_requirements = []
            for i in range(4):
                skill_requirements.append(reader.get_short())
            stat_requirements = SkillStatRequirements.deserialize(reader)
            result = SkillLearn(id=id, level_requirement=level_requirement, class_requirement=class_requirement, cost=cost, skill_requirements=skill_requirements, stat_requirements=stat_requirements)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SkillLearn(byte_size={repr(self._byte_size)}, id={repr(self._id)}, level_requirement={repr(self._level_requirement)}, class_requirement={repr(self._class_requirement)}, cost={repr(self._cost)}, skill_requirements={repr(self._skill_requirements)}, stat_requirements={repr(self._stat_requirements)})"
