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

class CitizenAcceptServerPacket(Packet):
    """
    Sleeping at an inn
    """
    _byte_size: int = 0
    _gold_amount: int

    def __init__(self, *, gold_amount: int):
        """
        Create a new instance of CitizenAcceptServerPacket.

        Args:
            gold_amount (int): (Value range is 0-4097152080.)
        """
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
    def gold_amount(self) -> int:
        return self._gold_amount

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Citizen

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
        CitizenAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenAcceptServerPacket") -> None:
        """
        Serializes an instance of `CitizenAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenAcceptServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenAcceptServerPacket":
        """
        Deserializes an instance of `CitizenAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenAcceptServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            gold_amount = reader.get_int()
            result = CitizenAcceptServerPacket(gold_amount=gold_amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenAcceptServerPacket(byte_size={repr(self._byte_size)}, gold_amount={repr(self._gold_amount)})"
