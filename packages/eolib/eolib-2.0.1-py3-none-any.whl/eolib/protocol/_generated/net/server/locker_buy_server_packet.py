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

class LockerBuyServerPacket(Packet):
    """
    Response to buying a locker space upgrade from a banker NPC
    """
    _byte_size: int = 0
    _gold_amount: int
    _locker_upgrades: int

    def __init__(self, *, gold_amount: int, locker_upgrades: int):
        """
        Create a new instance of LockerBuyServerPacket.

        Args:
            gold_amount (int): (Value range is 0-4097152080.)
            locker_upgrades (int): (Value range is 0-252.)
        """
        self._gold_amount = gold_amount
        self._locker_upgrades = locker_upgrades

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
    def locker_upgrades(self) -> int:
        return self._locker_upgrades

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Locker

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Buy

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        LockerBuyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LockerBuyServerPacket") -> None:
        """
        Serializes an instance of `LockerBuyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LockerBuyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)
            if data._locker_upgrades is None:
                raise SerializationError("locker_upgrades must be provided.")
            writer.add_char(data._locker_upgrades)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "LockerBuyServerPacket":
        """
        Deserializes an instance of `LockerBuyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LockerBuyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            gold_amount = reader.get_int()
            locker_upgrades = reader.get_char()
            result = LockerBuyServerPacket(gold_amount=gold_amount, locker_upgrades=locker_upgrades)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LockerBuyServerPacket(byte_size={repr(self._byte_size)}, gold_amount={repr(self._gold_amount)}, locker_upgrades={repr(self._locker_upgrades)})"
