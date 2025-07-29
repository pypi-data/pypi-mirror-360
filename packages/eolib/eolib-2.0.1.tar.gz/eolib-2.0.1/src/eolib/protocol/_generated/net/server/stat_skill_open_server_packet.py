# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .skill_learn import SkillLearn
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillOpenServerPacket(Packet):
    """
    Response from talking to a skill master NPC
    """
    _byte_size: int = 0
    _session_id: int
    _shop_name: str
    _skills: tuple[SkillLearn, ...]

    def __init__(self, *, session_id: int, shop_name: str, skills: Iterable[SkillLearn]):
        """
        Create a new instance of StatSkillOpenServerPacket.

        Args:
            session_id (int): (Value range is 0-64008.)
            shop_name (str): 
            skills (Iterable[SkillLearn]): 
        """
        self._session_id = session_id
        self._shop_name = shop_name
        self._skills = tuple(skills)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def shop_name(self) -> str:
        return self._shop_name

    @property
    def skills(self) -> tuple[SkillLearn, ...]:
        return self._skills

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.StatSkill

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillOpenServerPacket") -> None:
        """
        Serializes an instance of `StatSkillOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._shop_name is None:
                raise SerializationError("shop_name must be provided.")
            writer.add_string(data._shop_name)
            writer.add_byte(0xFF)
            if data._skills is None:
                raise SerializationError("skills must be provided.")
            for i in range(len(data._skills)):
                SkillLearn.serialize(writer, data._skills[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillOpenServerPacket":
        """
        Deserializes an instance of `StatSkillOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillOpenServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            session_id = reader.get_short()
            shop_name = reader.get_string()
            reader.next_chunk()
            skills_length = int(reader.remaining / 28)
            skills = []
            for i in range(skills_length):
                skills.append(SkillLearn.deserialize(reader))
            reader.chunked_reading_mode = False
            result = StatSkillOpenServerPacket(session_id=session_id, shop_name=shop_name, skills=skills)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillOpenServerPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, shop_name={repr(self._shop_name)}, skills={repr(self._skills)})"
