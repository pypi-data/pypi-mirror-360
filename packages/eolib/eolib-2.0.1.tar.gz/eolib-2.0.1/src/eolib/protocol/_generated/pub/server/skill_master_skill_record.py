# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SkillMasterSkillRecord:
    """
    Record of a skill that a Skill Master NPC can teach
    """
    _byte_size: int = 0
    _skill_id: int
    _level_requirement: int
    _class_requirement: int
    _price: int
    _skill_requirements: tuple[int, ...]
    _str_requirement: int
    _int_requirement: int
    _wis_requirement: int
    _agi_requirement: int
    _con_requirement: int
    _cha_requirement: int

    def __init__(self, *, skill_id: int, level_requirement: int, class_requirement: int, price: int, skill_requirements: Iterable[int], str_requirement: int, int_requirement: int, wis_requirement: int, agi_requirement: int, con_requirement: int, cha_requirement: int):
        """
        Create a new instance of SkillMasterSkillRecord.

        Args:
            skill_id (int): (Value range is 0-64008.)
            level_requirement (int): Level required to learn this skill (Value range is 0-252.)
            class_requirement (int): Class required to learn this skill (Value range is 0-252.)
            price (int): (Value range is 0-4097152080.)
            skill_requirements (Iterable[int]): IDs of skills that must be learned before a player can learn this skill (Length must be `4`.) (Element value range is 0-64008.)
            str_requirement (int): Strength required to learn this skill (Value range is 0-64008.)
            int_requirement (int): Intelligence required to learn this skill (Value range is 0-64008.)
            wis_requirement (int): Wisdom required to learn this skill (Value range is 0-64008.)
            agi_requirement (int): Agility required to learn this skill (Value range is 0-64008.)
            con_requirement (int): Constitution required to learn this skill (Value range is 0-64008.)
            cha_requirement (int): Charisma required to learn this skill (Value range is 0-64008.)
        """
        self._skill_id = skill_id
        self._level_requirement = level_requirement
        self._class_requirement = class_requirement
        self._price = price
        self._skill_requirements = tuple(skill_requirements)
        self._str_requirement = str_requirement
        self._int_requirement = int_requirement
        self._wis_requirement = wis_requirement
        self._agi_requirement = agi_requirement
        self._con_requirement = con_requirement
        self._cha_requirement = cha_requirement

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def skill_id(self) -> int:
        return self._skill_id

    @property
    def level_requirement(self) -> int:
        """
        Level required to learn this skill
        """
        return self._level_requirement

    @property
    def class_requirement(self) -> int:
        """
        Class required to learn this skill
        """
        return self._class_requirement

    @property
    def price(self) -> int:
        return self._price

    @property
    def skill_requirements(self) -> tuple[int, ...]:
        """
        IDs of skills that must be learned before a player can learn this skill
        """
        return self._skill_requirements

    @property
    def str_requirement(self) -> int:
        """
        Strength required to learn this skill
        """
        return self._str_requirement

    @property
    def int_requirement(self) -> int:
        """
        Intelligence required to learn this skill
        """
        return self._int_requirement

    @property
    def wis_requirement(self) -> int:
        """
        Wisdom required to learn this skill
        """
        return self._wis_requirement

    @property
    def agi_requirement(self) -> int:
        """
        Agility required to learn this skill
        """
        return self._agi_requirement

    @property
    def con_requirement(self) -> int:
        """
        Constitution required to learn this skill
        """
        return self._con_requirement

    @property
    def cha_requirement(self) -> int:
        """
        Charisma required to learn this skill
        """
        return self._cha_requirement

    @staticmethod
    def serialize(writer: EoWriter, data: "SkillMasterSkillRecord") -> None:
        """
        Serializes an instance of `SkillMasterSkillRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SkillMasterSkillRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._skill_id is None:
                raise SerializationError("skill_id must be provided.")
            writer.add_short(data._skill_id)
            if data._level_requirement is None:
                raise SerializationError("level_requirement must be provided.")
            writer.add_char(data._level_requirement)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_char(data._class_requirement)
            if data._price is None:
                raise SerializationError("price must be provided.")
            writer.add_int(data._price)
            if data._skill_requirements is None:
                raise SerializationError("skill_requirements must be provided.")
            if len(data._skill_requirements) != 4:
                raise SerializationError(f"Expected length of skill_requirements to be exactly 4, got {len(data._skill_requirements)}.")
            for i in range(4):
                writer.add_short(data._skill_requirements[i])
            if data._str_requirement is None:
                raise SerializationError("str_requirement must be provided.")
            writer.add_short(data._str_requirement)
            if data._int_requirement is None:
                raise SerializationError("int_requirement must be provided.")
            writer.add_short(data._int_requirement)
            if data._wis_requirement is None:
                raise SerializationError("wis_requirement must be provided.")
            writer.add_short(data._wis_requirement)
            if data._agi_requirement is None:
                raise SerializationError("agi_requirement must be provided.")
            writer.add_short(data._agi_requirement)
            if data._con_requirement is None:
                raise SerializationError("con_requirement must be provided.")
            writer.add_short(data._con_requirement)
            if data._cha_requirement is None:
                raise SerializationError("cha_requirement must be provided.")
            writer.add_short(data._cha_requirement)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SkillMasterSkillRecord":
        """
        Deserializes an instance of `SkillMasterSkillRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SkillMasterSkillRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            skill_id = reader.get_short()
            level_requirement = reader.get_char()
            class_requirement = reader.get_char()
            price = reader.get_int()
            skill_requirements = []
            for i in range(4):
                skill_requirements.append(reader.get_short())
            str_requirement = reader.get_short()
            int_requirement = reader.get_short()
            wis_requirement = reader.get_short()
            agi_requirement = reader.get_short()
            con_requirement = reader.get_short()
            cha_requirement = reader.get_short()
            result = SkillMasterSkillRecord(skill_id=skill_id, level_requirement=level_requirement, class_requirement=class_requirement, price=price, skill_requirements=skill_requirements, str_requirement=str_requirement, int_requirement=int_requirement, wis_requirement=wis_requirement, agi_requirement=agi_requirement, con_requirement=con_requirement, cha_requirement=cha_requirement)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SkillMasterSkillRecord(byte_size={repr(self._byte_size)}, skill_id={repr(self._skill_id)}, level_requirement={repr(self._level_requirement)}, class_requirement={repr(self._class_requirement)}, price={repr(self._price)}, skill_requirements={repr(self._skill_requirements)}, str_requirement={repr(self._str_requirement)}, int_requirement={repr(self._int_requirement)}, wis_requirement={repr(self._wis_requirement)}, agi_requirement={repr(self._agi_requirement)}, con_requirement={repr(self._con_requirement)}, cha_requirement={repr(self._cha_requirement)})"
