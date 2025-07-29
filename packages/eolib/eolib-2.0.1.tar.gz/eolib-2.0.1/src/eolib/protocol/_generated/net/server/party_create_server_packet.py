# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .party_member import PartyMember
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyCreateServerPacket(Packet):
    """
    Member list received when party is first joined
    """
    _byte_size: int = 0
    _members: tuple[PartyMember, ...]

    def __init__(self, *, members: Iterable[PartyMember]):
        """
        Create a new instance of PartyCreateServerPacket.

        Args:
            members (Iterable[PartyMember]): 
        """
        self._members = tuple(members)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def members(self) -> tuple[PartyMember, ...]:
        return self._members

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Party

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PartyCreateServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyCreateServerPacket") -> None:
        """
        Serializes an instance of `PartyCreateServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyCreateServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._members is None:
                raise SerializationError("members must be provided.")
            for i in range(len(data._members)):
                PartyMember.serialize(writer, data._members[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyCreateServerPacket":
        """
        Deserializes an instance of `PartyCreateServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyCreateServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            members = []
            while reader.remaining > 0:
                members.append(PartyMember.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            result = PartyCreateServerPacket(members=members)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyCreateServerPacket(byte_size={repr(self._byte_size)}, members={repr(self._members)})"
