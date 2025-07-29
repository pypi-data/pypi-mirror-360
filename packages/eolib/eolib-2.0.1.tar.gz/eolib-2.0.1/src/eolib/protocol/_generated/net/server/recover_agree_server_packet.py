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

class RecoverAgreeServerPacket(Packet):
    """
    Nearby player gained HP
    """
    _byte_size: int = 0
    _player_id: int
    _heal_hp: int
    _hp_percentage: int

    def __init__(self, *, player_id: int, heal_hp: int, hp_percentage: int):
        """
        Create a new instance of RecoverAgreeServerPacket.

        Args:
            player_id (int): (Value range is 0-64008.)
            heal_hp (int): (Value range is 0-4097152080.)
            hp_percentage (int): (Value range is 0-252.)
        """
        self._player_id = player_id
        self._heal_hp = heal_hp
        self._hp_percentage = hp_percentage

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def heal_hp(self) -> int:
        return self._heal_hp

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Recover

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        RecoverAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "RecoverAgreeServerPacket") -> None:
        """
        Serializes an instance of `RecoverAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (RecoverAgreeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._heal_hp is None:
                raise SerializationError("heal_hp must be provided.")
            writer.add_int(data._heal_hp)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "RecoverAgreeServerPacket":
        """
        Deserializes an instance of `RecoverAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            RecoverAgreeServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            heal_hp = reader.get_int()
            hp_percentage = reader.get_char()
            result = RecoverAgreeServerPacket(player_id=player_id, heal_hp=heal_hp, hp_percentage=hp_percentage)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"RecoverAgreeServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, heal_hp={repr(self._heal_hp)}, hp_percentage={repr(self._hp_percentage)})"
