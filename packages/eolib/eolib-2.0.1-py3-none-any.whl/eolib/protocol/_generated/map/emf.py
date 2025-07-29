# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .map_warp_row import MapWarpRow
from .map_type import MapType
from .map_timed_effect import MapTimedEffect
from .map_tile_spec_row import MapTileSpecRow
from .map_sign import MapSign
from .map_npc import MapNpc
from .map_music_control import MapMusicControl
from .map_legacy_door_key import MapLegacyDoorKey
from .map_item import MapItem
from .map_graphic_layer import MapGraphicLayer
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Emf:
    """
    Endless Map File
    """
    _byte_size: int = 0
    _rid: tuple[int, ...]
    _name: str
    _type: MapType
    _timed_effect: MapTimedEffect
    _music_id: int
    _music_control: MapMusicControl
    _ambient_sound_id: int
    _width: int
    _height: int
    _fill_tile: int
    _map_available: bool
    _can_scroll: bool
    _relog_x: int
    _relog_y: int
    _npcs_count: int
    _npcs: tuple[MapNpc, ...]
    _legacy_door_keys_count: int
    _legacy_door_keys: tuple[MapLegacyDoorKey, ...]
    _items_count: int
    _items: tuple[MapItem, ...]
    _tile_spec_rows_count: int
    _tile_spec_rows: tuple[MapTileSpecRow, ...]
    _warp_rows_count: int
    _warp_rows: tuple[MapWarpRow, ...]
    _graphic_layers: tuple[MapGraphicLayer, ...]
    _signs_count: int
    _signs: tuple[MapSign, ...]

    def __init__(self, *, rid: Iterable[int], name: str, type: MapType, timed_effect: MapTimedEffect, music_id: int, music_control: MapMusicControl, ambient_sound_id: int, width: int, height: int, fill_tile: int, map_available: bool, can_scroll: bool, relog_x: int, relog_y: int, npcs: Iterable[MapNpc], legacy_door_keys: Iterable[MapLegacyDoorKey], items: Iterable[MapItem], tile_spec_rows: Iterable[MapTileSpecRow], warp_rows: Iterable[MapWarpRow], graphic_layers: Iterable[MapGraphicLayer], signs: Iterable[MapSign]):
        """
        Create a new instance of Emf.

        Args:
            rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
            name (str): (Length must be `24` or less.)
            type (MapType): 
            timed_effect (MapTimedEffect): 
            music_id (int): (Value range is 0-252.)
            music_control (MapMusicControl): 
            ambient_sound_id (int): (Value range is 0-64008.)
            width (int): (Value range is 0-252.)
            height (int): (Value range is 0-252.)
            fill_tile (int): (Value range is 0-64008.)
            map_available (bool): 
            can_scroll (bool): 
            relog_x (int): (Value range is 0-252.)
            relog_y (int): (Value range is 0-252.)
            npcs (Iterable[MapNpc]): (Length must be 252 or less.)
            legacy_door_keys (Iterable[MapLegacyDoorKey]): (Length must be 252 or less.)
            items (Iterable[MapItem]): (Length must be 252 or less.)
            tile_spec_rows (Iterable[MapTileSpecRow]): (Length must be 252 or less.)
            warp_rows (Iterable[MapWarpRow]): (Length must be 252 or less.)
            graphic_layers (Iterable[MapGraphicLayer]): The 9 layers of map graphics. Order is [Ground, Object, Overlay, Down Wall, Right Wall, Roof, Top, Shadow, Overlay2] (Length must be `9`.)
            signs (Iterable[MapSign]): (Length must be 252 or less.)
        """
        self._rid = tuple(rid)
        self._name = name
        self._type = type
        self._timed_effect = timed_effect
        self._music_id = music_id
        self._music_control = music_control
        self._ambient_sound_id = ambient_sound_id
        self._width = width
        self._height = height
        self._fill_tile = fill_tile
        self._map_available = map_available
        self._can_scroll = can_scroll
        self._relog_x = relog_x
        self._relog_y = relog_y
        self._npcs = tuple(npcs)
        self._npcs_count = len(self._npcs)
        self._legacy_door_keys = tuple(legacy_door_keys)
        self._legacy_door_keys_count = len(self._legacy_door_keys)
        self._items = tuple(items)
        self._items_count = len(self._items)
        self._tile_spec_rows = tuple(tile_spec_rows)
        self._tile_spec_rows_count = len(self._tile_spec_rows)
        self._warp_rows = tuple(warp_rows)
        self._warp_rows_count = len(self._warp_rows)
        self._graphic_layers = tuple(graphic_layers)
        self._signs = tuple(signs)
        self._signs_count = len(self._signs)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rid(self) -> tuple[int, ...]:
        return self._rid

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> MapType:
        return self._type

    @property
    def timed_effect(self) -> MapTimedEffect:
        return self._timed_effect

    @property
    def music_id(self) -> int:
        return self._music_id

    @property
    def music_control(self) -> MapMusicControl:
        return self._music_control

    @property
    def ambient_sound_id(self) -> int:
        return self._ambient_sound_id

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def fill_tile(self) -> int:
        return self._fill_tile

    @property
    def map_available(self) -> bool:
        return self._map_available

    @property
    def can_scroll(self) -> bool:
        return self._can_scroll

    @property
    def relog_x(self) -> int:
        return self._relog_x

    @property
    def relog_y(self) -> int:
        return self._relog_y

    @property
    def npcs(self) -> tuple[MapNpc, ...]:
        return self._npcs

    @property
    def legacy_door_keys(self) -> tuple[MapLegacyDoorKey, ...]:
        return self._legacy_door_keys

    @property
    def items(self) -> tuple[MapItem, ...]:
        return self._items

    @property
    def tile_spec_rows(self) -> tuple[MapTileSpecRow, ...]:
        return self._tile_spec_rows

    @property
    def warp_rows(self) -> tuple[MapWarpRow, ...]:
        return self._warp_rows

    @property
    def graphic_layers(self) -> tuple[MapGraphicLayer, ...]:
        """
        The 9 layers of map graphics.
        Order is [Ground, Object, Overlay, Down Wall, Right Wall, Roof, Top, Shadow, Overlay2]
        """
        return self._graphic_layers

    @property
    def signs(self) -> tuple[MapSign, ...]:
        return self._signs

    @staticmethod
    def serialize(writer: EoWriter, data: "Emf") -> None:
        """
        Serializes an instance of `Emf` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Emf): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("EMF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 24:
                raise SerializationError(f"Expected length of name to be 24 or less, got {len(data._name)}.")
            writer.add_fixed_encoded_string(data._name, 24, True)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_char(int(data._type))
            if data._timed_effect is None:
                raise SerializationError("timed_effect must be provided.")
            writer.add_char(int(data._timed_effect))
            if data._music_id is None:
                raise SerializationError("music_id must be provided.")
            writer.add_char(data._music_id)
            if data._music_control is None:
                raise SerializationError("music_control must be provided.")
            writer.add_char(int(data._music_control))
            if data._ambient_sound_id is None:
                raise SerializationError("ambient_sound_id must be provided.")
            writer.add_short(data._ambient_sound_id)
            if data._width is None:
                raise SerializationError("width must be provided.")
            writer.add_char(data._width)
            if data._height is None:
                raise SerializationError("height must be provided.")
            writer.add_char(data._height)
            if data._fill_tile is None:
                raise SerializationError("fill_tile must be provided.")
            writer.add_short(data._fill_tile)
            if data._map_available is None:
                raise SerializationError("map_available must be provided.")
            writer.add_char(1 if data._map_available else 0)
            if data._can_scroll is None:
                raise SerializationError("can_scroll must be provided.")
            writer.add_char(1 if data._can_scroll else 0)
            if data._relog_x is None:
                raise SerializationError("relog_x must be provided.")
            writer.add_char(data._relog_x)
            if data._relog_y is None:
                raise SerializationError("relog_y must be provided.")
            writer.add_char(data._relog_y)
            writer.add_char(0)
            if data._npcs_count is None:
                raise SerializationError("npcs_count must be provided.")
            writer.add_char(data._npcs_count)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            if len(data._npcs) > 252:
                raise SerializationError(f"Expected length of npcs to be 252 or less, got {len(data._npcs)}.")
            for i in range(data._npcs_count):
                MapNpc.serialize(writer, data._npcs[i])
            if data._legacy_door_keys_count is None:
                raise SerializationError("legacy_door_keys_count must be provided.")
            writer.add_char(data._legacy_door_keys_count)
            if data._legacy_door_keys is None:
                raise SerializationError("legacy_door_keys must be provided.")
            if len(data._legacy_door_keys) > 252:
                raise SerializationError(f"Expected length of legacy_door_keys to be 252 or less, got {len(data._legacy_door_keys)}.")
            for i in range(data._legacy_door_keys_count):
                MapLegacyDoorKey.serialize(writer, data._legacy_door_keys[i])
            if data._items_count is None:
                raise SerializationError("items_count must be provided.")
            writer.add_char(data._items_count)
            if data._items is None:
                raise SerializationError("items must be provided.")
            if len(data._items) > 252:
                raise SerializationError(f"Expected length of items to be 252 or less, got {len(data._items)}.")
            for i in range(data._items_count):
                MapItem.serialize(writer, data._items[i])
            if data._tile_spec_rows_count is None:
                raise SerializationError("tile_spec_rows_count must be provided.")
            writer.add_char(data._tile_spec_rows_count)
            if data._tile_spec_rows is None:
                raise SerializationError("tile_spec_rows must be provided.")
            if len(data._tile_spec_rows) > 252:
                raise SerializationError(f"Expected length of tile_spec_rows to be 252 or less, got {len(data._tile_spec_rows)}.")
            for i in range(data._tile_spec_rows_count):
                MapTileSpecRow.serialize(writer, data._tile_spec_rows[i])
            if data._warp_rows_count is None:
                raise SerializationError("warp_rows_count must be provided.")
            writer.add_char(data._warp_rows_count)
            if data._warp_rows is None:
                raise SerializationError("warp_rows must be provided.")
            if len(data._warp_rows) > 252:
                raise SerializationError(f"Expected length of warp_rows to be 252 or less, got {len(data._warp_rows)}.")
            for i in range(data._warp_rows_count):
                MapWarpRow.serialize(writer, data._warp_rows[i])
            if data._graphic_layers is None:
                raise SerializationError("graphic_layers must be provided.")
            if len(data._graphic_layers) != 9:
                raise SerializationError(f"Expected length of graphic_layers to be exactly 9, got {len(data._graphic_layers)}.")
            for i in range(9):
                MapGraphicLayer.serialize(writer, data._graphic_layers[i])
            if data._signs_count is None:
                raise SerializationError("signs_count must be provided.")
            writer.add_char(data._signs_count)
            if data._signs is None:
                raise SerializationError("signs must be provided.")
            if len(data._signs) > 252:
                raise SerializationError(f"Expected length of signs to be 252 or less, got {len(data._signs)}.")
            for i in range(data._signs_count):
                MapSign.serialize(writer, data._signs[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Emf":
        """
        Deserializes an instance of `Emf` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Emf: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            rid = []
            for i in range(2):
                rid.append(reader.get_short())
            name = reader.get_fixed_encoded_string(24, True)
            type = MapType(reader.get_char())
            timed_effect = MapTimedEffect(reader.get_char())
            music_id = reader.get_char()
            music_control = MapMusicControl(reader.get_char())
            ambient_sound_id = reader.get_short()
            width = reader.get_char()
            height = reader.get_char()
            fill_tile = reader.get_short()
            map_available = reader.get_char() != 0
            can_scroll = reader.get_char() != 0
            relog_x = reader.get_char()
            relog_y = reader.get_char()
            reader.get_char()
            npcs_count = reader.get_char()
            npcs = []
            for i in range(npcs_count):
                npcs.append(MapNpc.deserialize(reader))
            legacy_door_keys_count = reader.get_char()
            legacy_door_keys = []
            for i in range(legacy_door_keys_count):
                legacy_door_keys.append(MapLegacyDoorKey.deserialize(reader))
            items_count = reader.get_char()
            items = []
            for i in range(items_count):
                items.append(MapItem.deserialize(reader))
            tile_spec_rows_count = reader.get_char()
            tile_spec_rows = []
            for i in range(tile_spec_rows_count):
                tile_spec_rows.append(MapTileSpecRow.deserialize(reader))
            warp_rows_count = reader.get_char()
            warp_rows = []
            for i in range(warp_rows_count):
                warp_rows.append(MapWarpRow.deserialize(reader))
            graphic_layers = []
            for i in range(9):
                graphic_layers.append(MapGraphicLayer.deserialize(reader))
            signs_count = reader.get_char()
            signs = []
            for i in range(signs_count):
                signs.append(MapSign.deserialize(reader))
            result = Emf(rid=rid, name=name, type=type, timed_effect=timed_effect, music_id=music_id, music_control=music_control, ambient_sound_id=ambient_sound_id, width=width, height=height, fill_tile=fill_tile, map_available=map_available, can_scroll=can_scroll, relog_x=relog_x, relog_y=relog_y, npcs=npcs, legacy_door_keys=legacy_door_keys, items=items, tile_spec_rows=tile_spec_rows, warp_rows=warp_rows, graphic_layers=graphic_layers, signs=signs)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Emf(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, name={repr(self._name)}, type={repr(self._type)}, timed_effect={repr(self._timed_effect)}, music_id={repr(self._music_id)}, music_control={repr(self._music_control)}, ambient_sound_id={repr(self._ambient_sound_id)}, width={repr(self._width)}, height={repr(self._height)}, fill_tile={repr(self._fill_tile)}, map_available={repr(self._map_available)}, can_scroll={repr(self._can_scroll)}, relog_x={repr(self._relog_x)}, relog_y={repr(self._relog_y)}, npcs={repr(self._npcs)}, legacy_door_keys={repr(self._legacy_door_keys)}, items={repr(self._items)}, tile_spec_rows={repr(self._tile_spec_rows)}, warp_rows={repr(self._warp_rows)}, graphic_layers={repr(self._graphic_layers)}, signs={repr(self._signs)})"
