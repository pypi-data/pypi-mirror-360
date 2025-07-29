# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .equipment_character_select import EquipmentCharacterSelect
from ...gender import Gender
from ...admin_level import AdminLevel
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterSelectionListEntry:
    """
    Character selection screen character
    """
    _byte_size: int = 0
    _name: str
    _id: int
    _level: int
    _gender: Gender
    _hair_style: int
    _hair_color: int
    _skin: int
    _admin: AdminLevel
    _equipment: EquipmentCharacterSelect

    def __init__(self, *, name: str, id: int, level: int, gender: Gender, hair_style: int, hair_color: int, skin: int, admin: AdminLevel, equipment: EquipmentCharacterSelect):
        """
        Create a new instance of CharacterSelectionListEntry.

        Args:
            name (str): 
            id (int): (Value range is 0-4097152080.)
            level (int): (Value range is 0-252.)
            gender (Gender): 
            hair_style (int): (Value range is 0-252.)
            hair_color (int): (Value range is 0-252.)
            skin (int): (Value range is 0-252.)
            admin (AdminLevel): 
            equipment (EquipmentCharacterSelect): 
        """
        self._name = name
        self._id = id
        self._level = level
        self._gender = gender
        self._hair_style = hair_style
        self._hair_color = hair_color
        self._skin = skin
        self._admin = admin
        self._equipment = equipment

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
    def id(self) -> int:
        return self._id

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
    def admin(self) -> AdminLevel:
        return self._admin

    @property
    def equipment(self) -> EquipmentCharacterSelect:
        return self._equipment

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterSelectionListEntry") -> None:
        """
        Serializes an instance of `CharacterSelectionListEntry` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterSelectionListEntry): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_int(data._id)
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
            if data._admin is None:
                raise SerializationError("admin must be provided.")
            writer.add_char(int(data._admin))
            if data._equipment is None:
                raise SerializationError("equipment must be provided.")
            EquipmentCharacterSelect.serialize(writer, data._equipment)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterSelectionListEntry":
        """
        Deserializes an instance of `CharacterSelectionListEntry` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterSelectionListEntry: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            name = reader.get_string()
            reader.next_chunk()
            id = reader.get_int()
            level = reader.get_char()
            gender = Gender(reader.get_char())
            hair_style = reader.get_char()
            hair_color = reader.get_char()
            skin = reader.get_char()
            admin = AdminLevel(reader.get_char())
            equipment = EquipmentCharacterSelect.deserialize(reader)
            reader.chunked_reading_mode = False
            result = CharacterSelectionListEntry(name=name, id=id, level=level, gender=gender, hair_style=hair_style, hair_color=hair_color, skin=skin, admin=admin, equipment=equipment)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterSelectionListEntry(byte_size={repr(self._byte_size)}, name={repr(self._name)}, id={repr(self._id)}, level={repr(self._level)}, gender={repr(self._gender)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, skin={repr(self._skin)}, admin={repr(self._admin)}, equipment={repr(self._equipment)})"
