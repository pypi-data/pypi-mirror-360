# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .trade_item_data import TradeItemData
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TradeUseServerPacket(Packet):
    """
    Trade completed
    """
    _byte_size: int = 0
    _trade_data: tuple[TradeItemData, ...]

    def __init__(self, *, trade_data: Iterable[TradeItemData]):
        """
        Create a new instance of TradeUseServerPacket.

        Args:
            trade_data (Iterable[TradeItemData]): (Length must be `2`.)
        """
        self._trade_data = tuple(trade_data)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def trade_data(self) -> tuple[TradeItemData, ...]:
        return self._trade_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Trade

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Use

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TradeUseServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeUseServerPacket") -> None:
        """
        Serializes an instance of `TradeUseServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeUseServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._trade_data is None:
                raise SerializationError("trade_data must be provided.")
            if len(data._trade_data) != 2:
                raise SerializationError(f"Expected length of trade_data to be exactly 2, got {len(data._trade_data)}.")
            for i in range(2):
                TradeItemData.serialize(writer, data._trade_data[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeUseServerPacket":
        """
        Deserializes an instance of `TradeUseServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeUseServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            trade_data = []
            for i in range(2):
                trade_data.append(TradeItemData.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            result = TradeUseServerPacket(trade_data=trade_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeUseServerPacket(byte_size={repr(self._byte_size)}, trade_data={repr(self._trade_data)})"
