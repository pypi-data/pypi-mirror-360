# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .map_graphic_row import MapGraphicRow
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapGraphicLayer:
    """
    A layer of map graphics
    """
    _byte_size: int = 0
    _graphic_rows_count: int
    _graphic_rows: tuple[MapGraphicRow, ...]

    def __init__(self, *, graphic_rows: Iterable[MapGraphicRow]):
        """
        Create a new instance of MapGraphicLayer.

        Args:
            graphic_rows (Iterable[MapGraphicRow]): (Length must be 252 or less.)
        """
        self._graphic_rows = tuple(graphic_rows)
        self._graphic_rows_count = len(self._graphic_rows)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def graphic_rows(self) -> tuple[MapGraphicRow, ...]:
        return self._graphic_rows

    @staticmethod
    def serialize(writer: EoWriter, data: "MapGraphicLayer") -> None:
        """
        Serializes an instance of `MapGraphicLayer` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapGraphicLayer): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._graphic_rows_count is None:
                raise SerializationError("graphic_rows_count must be provided.")
            writer.add_char(data._graphic_rows_count)
            if data._graphic_rows is None:
                raise SerializationError("graphic_rows must be provided.")
            if len(data._graphic_rows) > 252:
                raise SerializationError(f"Expected length of graphic_rows to be 252 or less, got {len(data._graphic_rows)}.")
            for i in range(data._graphic_rows_count):
                MapGraphicRow.serialize(writer, data._graphic_rows[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapGraphicLayer":
        """
        Deserializes an instance of `MapGraphicLayer` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapGraphicLayer: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            graphic_rows_count = reader.get_char()
            graphic_rows = []
            for i in range(graphic_rows_count):
                graphic_rows.append(MapGraphicRow.deserialize(reader))
            result = MapGraphicLayer(graphic_rows=graphic_rows)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapGraphicLayer(byte_size={repr(self._byte_size)}, graphic_rows={repr(self._graphic_rows)})"
