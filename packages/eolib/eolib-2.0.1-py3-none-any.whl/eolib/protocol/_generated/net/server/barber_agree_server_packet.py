# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .avatar_change import AvatarChange
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class BarberAgreeServerPacket(Packet):
    """
    Purchasing a new hair style
    """
    _byte_size: int = 0
    _gold_amount: int
    _change: AvatarChange

    def __init__(self, *, gold_amount: int, change: AvatarChange):
        """
        Create a new instance of BarberAgreeServerPacket.

        Args:
            gold_amount (int): (Value range is 0-4097152080.)
            change (AvatarChange): 
        """
        self._gold_amount = gold_amount
        self._change = change

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

    @property
    def change(self) -> AvatarChange:
        return self._change

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
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BarberAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BarberAgreeServerPacket") -> None:
        """
        Serializes an instance of `BarberAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BarberAgreeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)
            if data._change is None:
                raise SerializationError("change must be provided.")
            AvatarChange.serialize(writer, data._change)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BarberAgreeServerPacket":
        """
        Deserializes an instance of `BarberAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BarberAgreeServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            gold_amount = reader.get_int()
            change = AvatarChange.deserialize(reader)
            result = BarberAgreeServerPacket(gold_amount=gold_amount, change=change)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BarberAgreeServerPacket(byte_size={repr(self._byte_size)}, gold_amount={repr(self._gold_amount)}, change={repr(self._change)})"
