# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopTradeRecord:
    """
    Record of an item that can be bought or sold in a shop
    """
    _byte_size: int = 0
    _item_id: int
    _buy_price: int
    _sell_price: int
    _max_amount: int

    def __init__(self, *, item_id: int, buy_price: int, sell_price: int, max_amount: int):
        """
        Create a new instance of ShopTradeRecord.

        Args:
            item_id (int): (Value range is 0-64008.)
            buy_price (int): How much it costs to buy the item from the shop (Value range is 0-16194276.)
            sell_price (int): How much the shop will pay for the item (Value range is 0-16194276.)
            max_amount (int): Max amount of the item that can be bought or sold at one time (Value range is 0-252.)
        """
        self._item_id = item_id
        self._buy_price = buy_price
        self._sell_price = sell_price
        self._max_amount = max_amount

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def buy_price(self) -> int:
        """
        How much it costs to buy the item from the shop
        """
        return self._buy_price

    @property
    def sell_price(self) -> int:
        """
        How much the shop will pay for the item
        """
        return self._sell_price

    @property
    def max_amount(self) -> int:
        """
        Max amount of the item that can be bought or sold at one time
        """
        return self._max_amount

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopTradeRecord") -> None:
        """
        Serializes an instance of `ShopTradeRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopTradeRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._buy_price is None:
                raise SerializationError("buy_price must be provided.")
            writer.add_three(data._buy_price)
            if data._sell_price is None:
                raise SerializationError("sell_price must be provided.")
            writer.add_three(data._sell_price)
            if data._max_amount is None:
                raise SerializationError("max_amount must be provided.")
            writer.add_char(data._max_amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopTradeRecord":
        """
        Deserializes an instance of `ShopTradeRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopTradeRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item_id = reader.get_short()
            buy_price = reader.get_three()
            sell_price = reader.get_three()
            max_amount = reader.get_char()
            result = ShopTradeRecord(item_id=item_id, buy_price=buy_price, sell_price=sell_price, max_amount=max_amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopTradeRecord(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, buy_price={repr(self._buy_price)}, sell_price={repr(self._sell_price)}, max_amount={repr(self._max_amount)})"
