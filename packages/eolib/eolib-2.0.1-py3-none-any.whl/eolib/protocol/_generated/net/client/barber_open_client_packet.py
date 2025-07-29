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

class BarberOpenClientPacket(Packet):
    """
    Talking to a barber NPC
    """
    _byte_size: int = 0
    _npc_index: int

    def __init__(self, *, npc_index: int):
        """
        Create a new instance of BarberOpenClientPacket.

        Args:
            npc_index (int): (Value range is 0-64008.)
        """
        self._npc_index = npc_index

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Barber

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
        BarberOpenClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BarberOpenClientPacket") -> None:
        """
        Serializes an instance of `BarberOpenClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BarberOpenClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BarberOpenClientPacket":
        """
        Deserializes an instance of `BarberOpenClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BarberOpenClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_index = reader.get_short()
            result = BarberOpenClientPacket(npc_index=npc_index)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BarberOpenClientPacket(byte_size={repr(self._byte_size)}, npc_index={repr(self._npc_index)})"
