# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillTakeServerPacket(Packet):
    """
    Response from learning a skill from a skill master
    """
    _byte_size: int = 0
    _spell_id: int
    _gold_amount: int

    def __init__(self, *, spell_id: int, gold_amount: int):
        """
        Create a new instance of StatSkillTakeServerPacket.

        Args:
            spell_id (int): (Value range is 0-64008.)
            gold_amount (int): (Value range is 0-4097152080.)
        """
        self._spell_id = spell_id
        self._gold_amount = gold_amount

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def spell_id(self) -> int:
        return self._spell_id

    @property
    def gold_amount(self) -> int:
        return self._gold_amount

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
        return PacketAction.Take

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillTakeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillTakeServerPacket") -> None:
        """
        Serializes an instance of `StatSkillTakeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillTakeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillTakeServerPacket":
        """
        Deserializes an instance of `StatSkillTakeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillTakeServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            spell_id = reader.get_short()
            gold_amount = reader.get_int()
            result = StatSkillTakeServerPacket(spell_id=spell_id, gold_amount=gold_amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillTakeServerPacket(byte_size={repr(self._byte_size)}, spell_id={repr(self._spell_id)}, gold_amount={repr(self._gold_amount)})"
