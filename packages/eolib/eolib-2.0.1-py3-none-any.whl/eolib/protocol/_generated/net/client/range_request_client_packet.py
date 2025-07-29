# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class RangeRequestClientPacket(Packet):
    """
    Requesting info about nearby players and NPCs
    """
    _byte_size: int = 0
    _player_ids: tuple[int, ...]
    _npc_indexes: tuple[int, ...]

    def __init__(self, *, player_ids: Iterable[int], npc_indexes: Iterable[int]):
        """
        Create a new instance of RangeRequestClientPacket.

        Args:
            player_ids (Iterable[int]): (Element value range is 0-64008.)
            npc_indexes (Iterable[int]): (Element value range is 0-252.)
        """
        self._player_ids = tuple(player_ids)
        self._npc_indexes = tuple(npc_indexes)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_ids(self) -> tuple[int, ...]:
        return self._player_ids

    @property
    def npc_indexes(self) -> tuple[int, ...]:
        return self._npc_indexes

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Range

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        RangeRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "RangeRequestClientPacket") -> None:
        """
        Serializes an instance of `RangeRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (RangeRequestClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._player_ids is None:
                raise SerializationError("player_ids must be provided.")
            for i in range(len(data._player_ids)):
                writer.add_short(data._player_ids[i])
            writer.add_byte(0xFF)
            if data._npc_indexes is None:
                raise SerializationError("npc_indexes must be provided.")
            for i in range(len(data._npc_indexes)):
                writer.add_char(data._npc_indexes[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "RangeRequestClientPacket":
        """
        Deserializes an instance of `RangeRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            RangeRequestClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            player_ids_length = int(reader.remaining / 2)
            player_ids = []
            for i in range(player_ids_length):
                player_ids.append(reader.get_short())
            reader.next_chunk()
            npc_indexes_length = int(reader.remaining / 1)
            npc_indexes = []
            for i in range(npc_indexes_length):
                npc_indexes.append(reader.get_char())
            reader.chunked_reading_mode = False
            result = RangeRequestClientPacket(player_ids=player_ids, npc_indexes=npc_indexes)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"RangeRequestClientPacket(byte_size={repr(self._byte_size)}, player_ids={repr(self._player_ids)}, npc_indexes={repr(self._npc_indexes)})"
