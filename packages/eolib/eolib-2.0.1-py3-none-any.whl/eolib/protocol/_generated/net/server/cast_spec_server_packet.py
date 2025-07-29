# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from .npc_killed_data import NpcKilledData
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CastSpecServerPacket(Packet):
    """
    Nearby NPC killed by player spell
    """
    _byte_size: int = 0
    _spell_id: int
    _npc_killed_data: NpcKilledData
    _caster_tp: Optional[int]
    _experience: Optional[int]

    def __init__(self, *, spell_id: int, npc_killed_data: NpcKilledData, caster_tp: Optional[int] = None, experience: Optional[int] = None):
        """
        Create a new instance of CastSpecServerPacket.

        Args:
            spell_id (int): (Value range is 0-64008.)
            npc_killed_data (NpcKilledData): 
            caster_tp (Optional[int]): This field should be sent to the killer, but not nearby players (Value range is 0-64008.)
            experience (Optional[int]): This field should be sent to the killer, but not nearby players (Value range is 0-4097152080.)
        """
        self._spell_id = spell_id
        self._npc_killed_data = npc_killed_data
        self._caster_tp = caster_tp
        self._experience = experience

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
    def npc_killed_data(self) -> NpcKilledData:
        return self._npc_killed_data

    @property
    def caster_tp(self) -> Optional[int]:
        """
        This field should be sent to the killer, but not nearby players
        """
        return self._caster_tp

    @property
    def experience(self) -> Optional[int]:
        """
        This field should be sent to the killer, but not nearby players
        """
        return self._experience

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Cast

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Spec

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CastSpecServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CastSpecServerPacket") -> None:
        """
        Serializes an instance of `CastSpecServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CastSpecServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
            if data._npc_killed_data is None:
                raise SerializationError("npc_killed_data must be provided.")
            NpcKilledData.serialize(writer, data._npc_killed_data)
            reached_missing_optional = data._caster_tp is None
            if not reached_missing_optional:
                writer.add_short(cast(int, data._caster_tp))
            reached_missing_optional = reached_missing_optional or data._experience is None
            if not reached_missing_optional:
                writer.add_int(cast(int, data._experience))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CastSpecServerPacket":
        """
        Deserializes an instance of `CastSpecServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CastSpecServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            spell_id = reader.get_short()
            npc_killed_data = NpcKilledData.deserialize(reader)
            caster_tp: Optional[int] = None
            if reader.remaining > 0:
                caster_tp = reader.get_short()
            experience: Optional[int] = None
            if reader.remaining > 0:
                experience = reader.get_int()
            result = CastSpecServerPacket(spell_id=spell_id, npc_killed_data=npc_killed_data, caster_tp=caster_tp, experience=experience)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CastSpecServerPacket(byte_size={repr(self._byte_size)}, spell_id={repr(self._spell_id)}, npc_killed_data={repr(self._npc_killed_data)}, caster_tp={repr(self._caster_tp)}, experience={repr(self._experience)})"
