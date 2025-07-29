# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from .npc_killed_data import NpcKilledData
from .level_up_stats import LevelUpStats
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcAcceptServerPacket(Packet):
    """
    Nearby NPC killed and killer leveled up
    """
    _byte_size: int = 0
    _npc_killed_data: NpcKilledData
    _experience: Optional[int]
    _level_up: Optional[LevelUpStats]

    def __init__(self, *, npc_killed_data: NpcKilledData, experience: Optional[int] = None, level_up: Optional[LevelUpStats] = None):
        """
        Create a new instance of NpcAcceptServerPacket.

        Args:
            npc_killed_data (NpcKilledData): 
            experience (Optional[int]): This field should be sent to the killer, but not nearby players (Value range is 0-4097152080.)
            level_up (Optional[LevelUpStats]): This field should be sent to the killer if they leveled up, but not nearby players
        """
        self._npc_killed_data = npc_killed_data
        self._experience = experience
        self._level_up = level_up

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_killed_data(self) -> NpcKilledData:
        return self._npc_killed_data

    @property
    def experience(self) -> Optional[int]:
        """
        This field should be sent to the killer, but not nearby players
        """
        return self._experience

    @property
    def level_up(self) -> Optional[LevelUpStats]:
        """
        This field should be sent to the killer if they leveled up, but not nearby players
        """
        return self._level_up

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
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcAcceptServerPacket") -> None:
        """
        Serializes an instance of `NpcAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcAcceptServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_killed_data is None:
                raise SerializationError("npc_killed_data must be provided.")
            NpcKilledData.serialize(writer, data._npc_killed_data)
            reached_missing_optional = data._experience is None
            if not reached_missing_optional:
                writer.add_int(cast(int, data._experience))
            reached_missing_optional = reached_missing_optional or data._level_up is None
            if not reached_missing_optional:
                LevelUpStats.serialize(writer, cast(LevelUpStats, data._level_up))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcAcceptServerPacket":
        """
        Deserializes an instance of `NpcAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcAcceptServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_killed_data = NpcKilledData.deserialize(reader)
            experience: Optional[int] = None
            if reader.remaining > 0:
                experience = reader.get_int()
            level_up: Optional[LevelUpStats] = None
            if reader.remaining > 0:
                level_up = LevelUpStats.deserialize(reader)
            result = NpcAcceptServerPacket(npc_killed_data=npc_killed_data, experience=experience, level_up=level_up)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcAcceptServerPacket(byte_size={repr(self._byte_size)}, npc_killed_data={repr(self._npc_killed_data)}, experience={repr(self._experience)}, level_up={repr(self._level_up)})"
