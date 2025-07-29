# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .shop_craft_ingredient_record import ShopCraftIngredientRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopCraftRecord:
    """
    Record of an item that can be crafted in a shop
    """
    _byte_size: int = 0
    _item_id: int
    _ingredients: tuple[ShopCraftIngredientRecord, ...]

    def __init__(self, *, item_id: int, ingredients: Iterable[ShopCraftIngredientRecord]):
        """
        Create a new instance of ShopCraftRecord.

        Args:
            item_id (int): (Value range is 0-64008.)
            ingredients (Iterable[ShopCraftIngredientRecord]): (Length must be `4`.)
        """
        self._item_id = item_id
        self._ingredients = tuple(ingredients)

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
    def ingredients(self) -> tuple[ShopCraftIngredientRecord, ...]:
        return self._ingredients

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopCraftRecord") -> None:
        """
        Serializes an instance of `ShopCraftRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopCraftRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._ingredients is None:
                raise SerializationError("ingredients must be provided.")
            if len(data._ingredients) != 4:
                raise SerializationError(f"Expected length of ingredients to be exactly 4, got {len(data._ingredients)}.")
            for i in range(4):
                ShopCraftIngredientRecord.serialize(writer, data._ingredients[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopCraftRecord":
        """
        Deserializes an instance of `ShopCraftRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopCraftRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item_id = reader.get_short()
            ingredients = []
            for i in range(4):
                ingredients.append(ShopCraftIngredientRecord.deserialize(reader))
            result = ShopCraftRecord(item_id=item_id, ingredients=ingredients)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopCraftRecord(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, ingredients={repr(self._ingredients)})"
