# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AvatarReplyServerPacket(Packet):
    """
    Nearby player hit by another player
    """
    _byte_size: int = 0
    _player_id: int
    _victim_id: int
    _damage: int
    _direction: Direction
    _hp_percentage: int
    _dead: bool

    def __init__(self, *, player_id: int, victim_id: int, damage: int, direction: Direction, hp_percentage: int, dead: bool):
        """
        Create a new instance of AvatarReplyServerPacket.

        Args:
            player_id (int): (Value range is 0-64008.)
            victim_id (int): (Value range is 0-64008.)
            damage (int): (Value range is 0-16194276.)
            direction (Direction): 
            hp_percentage (int): (Value range is 0-252.)
            dead (bool): 
        """
        self._player_id = player_id
        self._victim_id = victim_id
        self._damage = damage
        self._direction = direction
        self._hp_percentage = hp_percentage
        self._dead = dead

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
    def victim_id(self) -> int:
        return self._victim_id

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @property
    def dead(self) -> bool:
        return self._dead

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Avatar

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AvatarReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AvatarReplyServerPacket") -> None:
        """
        Serializes an instance of `AvatarReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AvatarReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._victim_id is None:
                raise SerializationError("victim_id must be provided.")
            writer.add_short(data._victim_id)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._dead is None:
                raise SerializationError("dead must be provided.")
            writer.add_char(1 if data._dead else 0)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AvatarReplyServerPacket":
        """
        Deserializes an instance of `AvatarReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AvatarReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            victim_id = reader.get_short()
            damage = reader.get_three()
            direction = Direction(reader.get_char())
            hp_percentage = reader.get_char()
            dead = reader.get_char() != 0
            result = AvatarReplyServerPacket(player_id=player_id, victim_id=victim_id, damage=damage, direction=direction, hp_percentage=hp_percentage, dead=dead)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AvatarReplyServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, victim_id={repr(self._victim_id)}, damage={repr(self._damage)}, direction={repr(self._direction)}, hp_percentage={repr(self._hp_percentage)}, dead={repr(self._dead)})"
