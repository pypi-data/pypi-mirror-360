# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..spell import Spell
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillAcceptServerPacket(Packet):
    """
    Response to spending skill points
    """
    _byte_size: int = 0
    _skill_points: int
    _spell: Spell

    def __init__(self, *, skill_points: int, spell: Spell):
        """
        Create a new instance of StatSkillAcceptServerPacket.

        Args:
            skill_points (int): (Value range is 0-64008.)
            spell (Spell): 
        """
        self._skill_points = skill_points
        self._spell = spell

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def skill_points(self) -> int:
        return self._skill_points

    @property
    def spell(self) -> Spell:
        return self._spell

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
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillAcceptServerPacket") -> None:
        """
        Serializes an instance of `StatSkillAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillAcceptServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._skill_points is None:
                raise SerializationError("skill_points must be provided.")
            writer.add_short(data._skill_points)
            if data._spell is None:
                raise SerializationError("spell must be provided.")
            Spell.serialize(writer, data._spell)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillAcceptServerPacket":
        """
        Deserializes an instance of `StatSkillAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillAcceptServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            skill_points = reader.get_short()
            spell = Spell.deserialize(reader)
            result = StatSkillAcceptServerPacket(skill_points=skill_points, spell=spell)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillAcceptServerPacket(byte_size={repr(self._byte_size)}, skill_points={repr(self._skill_points)}, spell={repr(self._spell)})"
