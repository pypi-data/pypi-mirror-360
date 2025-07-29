# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from .warp_effect import WarpEffect
from .sit_state import SitState
from .equipment_map_info import EquipmentMapInfo
from .big_coords import BigCoords
from ...gender import Gender
from ...direction import Direction
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterMapInfo:
    """
    Information about a nearby character.
    The official client skips these if they're under 42 bytes in length.
    """
    _byte_size: int = 0
    _name: str
    _player_id: int
    _map_id: int
    _coords: BigCoords
    _direction: Direction
    _class_id: int
    _guild_tag: str
    _level: int
    _gender: Gender
    _hair_style: int
    _hair_color: int
    _skin: int
    _max_hp: int
    _hp: int
    _max_tp: int
    _tp: int
    _equipment: EquipmentMapInfo
    _sit_state: SitState
    _invisible: bool
    _warp_effect: Optional[WarpEffect]

    def __init__(self, *, name: str, player_id: int, map_id: int, coords: BigCoords, direction: Direction, class_id: int, guild_tag: str, level: int, gender: Gender, hair_style: int, hair_color: int, skin: int, max_hp: int, hp: int, max_tp: int, tp: int, equipment: EquipmentMapInfo, sit_state: SitState, invisible: bool, warp_effect: Optional[WarpEffect] = None):
        """
        Create a new instance of CharacterMapInfo.

        Args:
            name (str): 
            player_id (int): (Value range is 0-64008.)
            map_id (int): (Value range is 0-64008.)
            coords (BigCoords): 
            direction (Direction): 
            class_id (int): (Value range is 0-252.)
            guild_tag (str): (Length must be `3`.)
            level (int): (Value range is 0-252.)
            gender (Gender): 
            hair_style (int): (Value range is 0-252.)
            hair_color (int): (Value range is 0-252.)
            skin (int): (Value range is 0-252.)
            max_hp (int): (Value range is 0-64008.)
            hp (int): (Value range is 0-64008.)
            max_tp (int): (Value range is 0-64008.)
            tp (int): (Value range is 0-64008.)
            equipment (EquipmentMapInfo): 
            sit_state (SitState): 
            invisible (bool): 
            warp_effect (Optional[WarpEffect]): 
        """
        self._name = name
        self._player_id = player_id
        self._map_id = map_id
        self._coords = coords
        self._direction = direction
        self._class_id = class_id
        self._guild_tag = guild_tag
        self._level = level
        self._gender = gender
        self._hair_style = hair_style
        self._hair_color = hair_color
        self._skin = skin
        self._max_hp = max_hp
        self._hp = hp
        self._max_tp = max_tp
        self._tp = tp
        self._equipment = equipment
        self._sit_state = sit_state
        self._invisible = invisible
        self._warp_effect = warp_effect

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def map_id(self) -> int:
        return self._map_id

    @property
    def coords(self) -> BigCoords:
        return self._coords

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def class_id(self) -> int:
        return self._class_id

    @property
    def guild_tag(self) -> str:
        return self._guild_tag

    @property
    def level(self) -> int:
        return self._level

    @property
    def gender(self) -> Gender:
        return self._gender

    @property
    def hair_style(self) -> int:
        return self._hair_style

    @property
    def hair_color(self) -> int:
        return self._hair_color

    @property
    def skin(self) -> int:
        return self._skin

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def max_tp(self) -> int:
        return self._max_tp

    @property
    def tp(self) -> int:
        return self._tp

    @property
    def equipment(self) -> EquipmentMapInfo:
        return self._equipment

    @property
    def sit_state(self) -> SitState:
        return self._sit_state

    @property
    def invisible(self) -> bool:
        return self._invisible

    @property
    def warp_effect(self) -> Optional[WarpEffect]:
        return self._warp_effect

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterMapInfo") -> None:
        """
        Serializes an instance of `CharacterMapInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterMapInfo): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._map_id is None:
                raise SerializationError("map_id must be provided.")
            writer.add_short(data._map_id)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            BigCoords.serialize(writer, data._coords)
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
            if data._class_id is None:
                raise SerializationError("class_id must be provided.")
            writer.add_char(data._class_id)
            if data._guild_tag is None:
                raise SerializationError("guild_tag must be provided.")
            if len(data._guild_tag) != 3:
                raise SerializationError(f"Expected length of guild_tag to be exactly 3, got {len(data._guild_tag)}.")
            writer.add_fixed_string(data._guild_tag, 3, False)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._gender is None:
                raise SerializationError("gender must be provided.")
            writer.add_char(int(data._gender))
            if data._hair_style is None:
                raise SerializationError("hair_style must be provided.")
            writer.add_char(data._hair_style)
            if data._hair_color is None:
                raise SerializationError("hair_color must be provided.")
            writer.add_char(data._hair_color)
            if data._skin is None:
                raise SerializationError("skin must be provided.")
            writer.add_char(data._skin)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
            if data._equipment is None:
                raise SerializationError("equipment must be provided.")
            EquipmentMapInfo.serialize(writer, data._equipment)
            if data._sit_state is None:
                raise SerializationError("sit_state must be provided.")
            writer.add_char(int(data._sit_state))
            if data._invisible is None:
                raise SerializationError("invisible must be provided.")
            writer.add_char(1 if data._invisible else 0)
            reached_missing_optional = data._warp_effect is None
            if not reached_missing_optional:
                writer.add_char(int(cast(WarpEffect, data._warp_effect)))
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterMapInfo":
        """
        Deserializes an instance of `CharacterMapInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterMapInfo: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            name = reader.get_string()
            reader.next_chunk()
            player_id = reader.get_short()
            map_id = reader.get_short()
            coords = BigCoords.deserialize(reader)
            direction = Direction(reader.get_char())
            class_id = reader.get_char()
            guild_tag = reader.get_fixed_string(3, False)
            level = reader.get_char()
            gender = Gender(reader.get_char())
            hair_style = reader.get_char()
            hair_color = reader.get_char()
            skin = reader.get_char()
            max_hp = reader.get_short()
            hp = reader.get_short()
            max_tp = reader.get_short()
            tp = reader.get_short()
            equipment = EquipmentMapInfo.deserialize(reader)
            sit_state = SitState(reader.get_char())
            invisible = reader.get_char() != 0
            warp_effect: Optional[WarpEffect] = None
            if reader.remaining > 0:
                warp_effect = WarpEffect(reader.get_char())
            reader.chunked_reading_mode = False
            result = CharacterMapInfo(name=name, player_id=player_id, map_id=map_id, coords=coords, direction=direction, class_id=class_id, guild_tag=guild_tag, level=level, gender=gender, hair_style=hair_style, hair_color=hair_color, skin=skin, max_hp=max_hp, hp=hp, max_tp=max_tp, tp=tp, equipment=equipment, sit_state=sit_state, invisible=invisible, warp_effect=warp_effect)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterMapInfo(byte_size={repr(self._byte_size)}, name={repr(self._name)}, player_id={repr(self._player_id)}, map_id={repr(self._map_id)}, coords={repr(self._coords)}, direction={repr(self._direction)}, class_id={repr(self._class_id)}, guild_tag={repr(self._guild_tag)}, level={repr(self._level)}, gender={repr(self._gender)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, skin={repr(self._skin)}, max_hp={repr(self._max_hp)}, hp={repr(self._hp)}, max_tp={repr(self._max_tp)}, tp={repr(self._tp)}, equipment={repr(self._equipment)}, sit_state={repr(self._sit_state)}, invisible={repr(self._invisible)}, warp_effect={repr(self._warp_effect)})"
