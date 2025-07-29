# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .npc_map_info import NpcMapInfo
from .item_map_info import ItemMapInfo
from .character_map_info import CharacterMapInfo
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NearbyInfo:
    """
    Information about nearby entities
    """
    _byte_size: int = 0
    _characters_count: int
    _characters: tuple[CharacterMapInfo, ...]
    _npcs: tuple[NpcMapInfo, ...]
    _items: tuple[ItemMapInfo, ...]

    def __init__(self, *, characters: Iterable[CharacterMapInfo], npcs: Iterable[NpcMapInfo], items: Iterable[ItemMapInfo]):
        """
        Create a new instance of NearbyInfo.

        Args:
            characters (Iterable[CharacterMapInfo]): (Length must be 252 or less.)
            npcs (Iterable[NpcMapInfo]): 
            items (Iterable[ItemMapInfo]): 
        """
        self._characters = tuple(characters)
        self._characters_count = len(self._characters)
        self._npcs = tuple(npcs)
        self._items = tuple(items)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def characters(self) -> tuple[CharacterMapInfo, ...]:
        return self._characters

    @property
    def npcs(self) -> tuple[NpcMapInfo, ...]:
        return self._npcs

    @property
    def items(self) -> tuple[ItemMapInfo, ...]:
        return self._items

    @staticmethod
    def serialize(writer: EoWriter, data: "NearbyInfo") -> None:
        """
        Serializes an instance of `NearbyInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NearbyInfo): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._characters_count is None:
                raise SerializationError("characters_count must be provided.")
            writer.add_char(data._characters_count)
            writer.string_sanitization_mode = True
            writer.add_byte(0xFF)
            if data._characters is None:
                raise SerializationError("characters must be provided.")
            if len(data._characters) > 252:
                raise SerializationError(f"Expected length of characters to be 252 or less, got {len(data._characters)}.")
            for i in range(data._characters_count):
                CharacterMapInfo.serialize(writer, data._characters[i])
                writer.add_byte(0xFF)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            for i in range(len(data._npcs)):
                NpcMapInfo.serialize(writer, data._npcs[i])
            writer.add_byte(0xFF)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                ItemMapInfo.serialize(writer, data._items[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NearbyInfo":
        """
        Deserializes an instance of `NearbyInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NearbyInfo: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            characters_count = reader.get_char()
            reader.chunked_reading_mode = True
            reader.next_chunk()
            characters = []
            for i in range(characters_count):
                characters.append(CharacterMapInfo.deserialize(reader))
                reader.next_chunk()
            npcs_length = int(reader.remaining / 6)
            npcs = []
            for i in range(npcs_length):
                npcs.append(NpcMapInfo.deserialize(reader))
            reader.next_chunk()
            items_length = int(reader.remaining / 9)
            items = []
            for i in range(items_length):
                items.append(ItemMapInfo.deserialize(reader))
            reader.chunked_reading_mode = False
            result = NearbyInfo(characters=characters, npcs=npcs, items=items)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NearbyInfo(byte_size={repr(self._byte_size)}, characters={repr(self._characters)}, npcs={repr(self._npcs)}, items={repr(self._items)})"
