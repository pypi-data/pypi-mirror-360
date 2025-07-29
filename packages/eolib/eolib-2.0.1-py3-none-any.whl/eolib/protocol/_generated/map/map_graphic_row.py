# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .map_graphic_row_tile import MapGraphicRowTile
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapGraphicRow:
    """
    A row in a layer of map graphics
    """
    _byte_size: int = 0
    _y: int
    _tiles_count: int
    _tiles: tuple[MapGraphicRowTile, ...]

    def __init__(self, *, y: int, tiles: Iterable[MapGraphicRowTile]):
        """
        Create a new instance of MapGraphicRow.

        Args:
            y (int): (Value range is 0-252.)
            tiles (Iterable[MapGraphicRowTile]): (Length must be 252 or less.)
        """
        self._y = y
        self._tiles = tuple(tiles)
        self._tiles_count = len(self._tiles)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def y(self) -> int:
        return self._y

    @property
    def tiles(self) -> tuple[MapGraphicRowTile, ...]:
        return self._tiles

    @staticmethod
    def serialize(writer: EoWriter, data: "MapGraphicRow") -> None:
        """
        Serializes an instance of `MapGraphicRow` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapGraphicRow): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._y is None:
                raise SerializationError("y must be provided.")
            writer.add_char(data._y)
            if data._tiles_count is None:
                raise SerializationError("tiles_count must be provided.")
            writer.add_char(data._tiles_count)
            if data._tiles is None:
                raise SerializationError("tiles must be provided.")
            if len(data._tiles) > 252:
                raise SerializationError(f"Expected length of tiles to be 252 or less, got {len(data._tiles)}.")
            for i in range(data._tiles_count):
                MapGraphicRowTile.serialize(writer, data._tiles[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapGraphicRow":
        """
        Deserializes an instance of `MapGraphicRow` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapGraphicRow: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            y = reader.get_char()
            tiles_count = reader.get_char()
            tiles = []
            for i in range(tiles_count):
                tiles.append(MapGraphicRowTile.deserialize(reader))
            result = MapGraphicRow(y=y, tiles=tiles)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapGraphicRow(byte_size={repr(self._byte_size)}, y={repr(self._y)}, tiles={repr(self._tiles)})"
