# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopCraftIngredientRecord:
    """
    Record of an ingredient for crafting an item in a shop
    """
    _byte_size: int = 0
    _item_id: int
    _amount: int

    def __init__(self, *, item_id: int, amount: int):
        """
        Create a new instance of ShopCraftIngredientRecord.

        Args:
            item_id (int): Item ID of the craft ingredient, or 0 if the ingredient is not present (Value range is 0-64008.)
            amount (int): (Value range is 0-252.)
        """
        self._item_id = item_id
        self._amount = amount

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
        """
        Item ID of the craft ingredient, or 0 if the ingredient is not present
        """
        return self._item_id

    @property
    def amount(self) -> int:
        return self._amount

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopCraftIngredientRecord") -> None:
        """
        Serializes an instance of `ShopCraftIngredientRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopCraftIngredientRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_char(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopCraftIngredientRecord":
        """
        Deserializes an instance of `ShopCraftIngredientRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopCraftIngredientRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item_id = reader.get_short()
            amount = reader.get_char()
            result = ShopCraftIngredientRecord(item_id=item_id, amount=amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopCraftIngredientRecord(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, amount={repr(self._amount)})"
