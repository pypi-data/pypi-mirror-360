# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .shop_sold_item import ShopSoldItem
from ..weight import Weight
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopSellServerPacket(Packet):
    """
    Response to selling an item to a shop
    """
    _byte_size: int = 0
    _sold_item: ShopSoldItem
    _gold_amount: int
    _weight: Weight

    def __init__(self, *, sold_item: ShopSoldItem, gold_amount: int, weight: Weight):
        """
        Create a new instance of ShopSellServerPacket.

        Args:
            sold_item (ShopSoldItem): 
            gold_amount (int): (Value range is 0-4097152080.)
            weight (Weight): 
        """
        self._sold_item = sold_item
        self._gold_amount = gold_amount
        self._weight = weight

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def sold_item(self) -> ShopSoldItem:
        return self._sold_item

    @property
    def gold_amount(self) -> int:
        return self._gold_amount

    @property
    def weight(self) -> Weight:
        return self._weight

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Shop

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Sell

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ShopSellServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopSellServerPacket") -> None:
        """
        Serializes an instance of `ShopSellServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopSellServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._sold_item is None:
                raise SerializationError("sold_item must be provided.")
            ShopSoldItem.serialize(writer, data._sold_item)
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopSellServerPacket":
        """
        Deserializes an instance of `ShopSellServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopSellServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            sold_item = ShopSoldItem.deserialize(reader)
            gold_amount = reader.get_int()
            weight = Weight.deserialize(reader)
            result = ShopSellServerPacket(sold_item=sold_item, gold_amount=gold_amount, weight=weight)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopSellServerPacket(byte_size={repr(self._byte_size)}, sold_item={repr(self._sold_item)}, gold_amount={repr(self._gold_amount)}, weight={repr(self._weight)})"
