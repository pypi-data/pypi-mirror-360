# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from .npc_kill_steal_protection_state import NpcKillStealProtectionState
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcReplyServerPacket(Packet):
    """
    Nearby NPC hit by a player
    """
    _byte_size: int = 0
    _player_id: int
    _player_direction: Direction
    _npc_index: int
    _damage: int
    _hp_percentage: int
    _kill_steal_protection: Optional[NpcKillStealProtectionState]

    def __init__(self, *, player_id: int, player_direction: Direction, npc_index: int, damage: int, hp_percentage: int, kill_steal_protection: Optional[NpcKillStealProtectionState] = None):
        """
        Create a new instance of NpcReplyServerPacket.

        Args:
            player_id (int): (Value range is 0-64008.)
            player_direction (Direction): 
            npc_index (int): (Value range is 0-64008.)
            damage (int): (Value range is 0-16194276.)
            hp_percentage (int): (Value range is 0-64008.)
            kill_steal_protection (Optional[NpcKillStealProtectionState]): This field should be sent to the attacker, but not nearby players
        """
        self._player_id = player_id
        self._player_direction = player_direction
        self._npc_index = npc_index
        self._damage = damage
        self._hp_percentage = hp_percentage
        self._kill_steal_protection = kill_steal_protection

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
    def player_direction(self) -> Direction:
        return self._player_direction

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @property
    def kill_steal_protection(self) -> Optional[NpcKillStealProtectionState]:
        """
        This field should be sent to the attacker, but not nearby players
        """
        return self._kill_steal_protection

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Npc

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
        NpcReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcReplyServerPacket") -> None:
        """
        Serializes an instance of `NpcReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._player_direction is None:
                raise SerializationError("player_direction must be provided.")
            writer.add_char(int(data._player_direction))
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_short(data._hp_percentage)
            reached_missing_optional = data._kill_steal_protection is None
            if not reached_missing_optional:
                writer.add_char(int(cast(NpcKillStealProtectionState, data._kill_steal_protection)))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcReplyServerPacket":
        """
        Deserializes an instance of `NpcReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            player_direction = Direction(reader.get_char())
            npc_index = reader.get_short()
            damage = reader.get_three()
            hp_percentage = reader.get_short()
            kill_steal_protection: Optional[NpcKillStealProtectionState] = None
            if reader.remaining > 0:
                kill_steal_protection = NpcKillStealProtectionState(reader.get_char())
            result = NpcReplyServerPacket(player_id=player_id, player_direction=player_direction, npc_index=npc_index, damage=damage, hp_percentage=hp_percentage, kill_steal_protection=kill_steal_protection)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcReplyServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, player_direction={repr(self._player_direction)}, npc_index={repr(self._npc_index)}, damage={repr(self._damage)}, hp_percentage={repr(self._hp_percentage)}, kill_steal_protection={repr(self._kill_steal_protection)})"
