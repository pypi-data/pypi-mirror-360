# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .equipment_change import EquipmentChange
from .avatar_change_type import AvatarChangeType
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AvatarChange:
    """
    Information about a nearby player's appearance changing
    """
    _byte_size: int = 0
    _player_id: int
    _change_type: AvatarChangeType
    _sound: bool
    _change_type_data: 'AvatarChange.ChangeTypeData'

    def __init__(self, *, player_id: int, change_type: AvatarChangeType, sound: bool, change_type_data: 'AvatarChange.ChangeTypeData' = None):
        """
        Create a new instance of AvatarChange.

        Args:
            player_id (int): (Value range is 0-64008.)
            change_type (AvatarChangeType): 
            sound (bool): 
            change_type_data (AvatarChange.ChangeTypeData): Data associated with the `change_type` field.
        """
        self._player_id = player_id
        self._change_type = change_type
        self._sound = sound
        self._change_type_data = change_type_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def change_type(self) -> AvatarChangeType:
        return self._change_type

    @property
    def sound(self) -> bool:
        return self._sound

    @property
    def change_type_data(self) -> 'AvatarChange.ChangeTypeData':
        """
        AvatarChange.ChangeTypeData: Data associated with the `change_type` field.
        """
        return self._change_type_data

    @staticmethod
    def serialize(writer: EoWriter, data: "AvatarChange") -> None:
        """
        Serializes an instance of `AvatarChange` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AvatarChange): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._change_type is None:
                raise SerializationError("change_type must be provided.")
            writer.add_char(int(data._change_type))
            if data._sound is None:
                raise SerializationError("sound must be provided.")
            writer.add_char(1 if data._sound else 0)
            if data._change_type == AvatarChangeType.Equipment:
                if not isinstance(data._change_type_data, AvatarChange.ChangeTypeDataEquipment):
                    raise SerializationError("Expected change_type_data to be type AvatarChange.ChangeTypeDataEquipment for change_type " + AvatarChangeType(data._change_type).name + ".")
                AvatarChange.ChangeTypeDataEquipment.serialize(writer, data._change_type_data)
            elif data._change_type == AvatarChangeType.Hair:
                if not isinstance(data._change_type_data, AvatarChange.ChangeTypeDataHair):
                    raise SerializationError("Expected change_type_data to be type AvatarChange.ChangeTypeDataHair for change_type " + AvatarChangeType(data._change_type).name + ".")
                AvatarChange.ChangeTypeDataHair.serialize(writer, data._change_type_data)
            elif data._change_type == AvatarChangeType.HairColor:
                if not isinstance(data._change_type_data, AvatarChange.ChangeTypeDataHairColor):
                    raise SerializationError("Expected change_type_data to be type AvatarChange.ChangeTypeDataHairColor for change_type " + AvatarChangeType(data._change_type).name + ".")
                AvatarChange.ChangeTypeDataHairColor.serialize(writer, data._change_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AvatarChange":
        """
        Deserializes an instance of `AvatarChange` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AvatarChange: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            change_type = AvatarChangeType(reader.get_char())
            sound = reader.get_char() != 0
            change_type_data: AvatarChange.ChangeTypeData = None
            if change_type == AvatarChangeType.Equipment:
                change_type_data = AvatarChange.ChangeTypeDataEquipment.deserialize(reader)
            elif change_type == AvatarChangeType.Hair:
                change_type_data = AvatarChange.ChangeTypeDataHair.deserialize(reader)
            elif change_type == AvatarChangeType.HairColor:
                change_type_data = AvatarChange.ChangeTypeDataHairColor.deserialize(reader)
            result = AvatarChange(player_id=player_id, change_type=change_type, sound=sound, change_type_data=change_type_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AvatarChange(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, change_type={repr(self._change_type)}, sound={repr(self._sound)}, change_type_data={repr(self._change_type_data)})"

    ChangeTypeData = Union['AvatarChange.ChangeTypeDataEquipment', 'AvatarChange.ChangeTypeDataHair', 'AvatarChange.ChangeTypeDataHairColor', None]
    """
    Data associated with different values of the `change_type` field.
    """

    class ChangeTypeDataEquipment:
        """
        Data associated with change_type value AvatarChangeType.Equipment
        """
        _byte_size: int = 0
        _equipment: EquipmentChange

        def __init__(self, *, equipment: EquipmentChange):
            """
            Create a new instance of AvatarChange.ChangeTypeDataEquipment.

            Args:
                equipment (EquipmentChange): 
            """
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
        def equipment(self) -> EquipmentChange:
            return self._equipment

        @staticmethod
        def serialize(writer: EoWriter, data: "AvatarChange.ChangeTypeDataEquipment") -> None:
            """
            Serializes an instance of `AvatarChange.ChangeTypeDataEquipment` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AvatarChange.ChangeTypeDataEquipment): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._equipment is None:
                    raise SerializationError("equipment must be provided.")
                EquipmentChange.serialize(writer, data._equipment)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "AvatarChange.ChangeTypeDataEquipment":
            """
            Deserializes an instance of `AvatarChange.ChangeTypeDataEquipment` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AvatarChange.ChangeTypeDataEquipment: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                equipment = EquipmentChange.deserialize(reader)
                result = AvatarChange.ChangeTypeDataEquipment(equipment=equipment)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AvatarChange.ChangeTypeDataEquipment(byte_size={repr(self._byte_size)}, equipment={repr(self._equipment)})"

    class ChangeTypeDataHair:
        """
        Data associated with change_type value AvatarChangeType.Hair
        """
        _byte_size: int = 0
        _hair_style: int
        _hair_color: int

        def __init__(self, *, hair_style: int, hair_color: int):
            """
            Create a new instance of AvatarChange.ChangeTypeDataHair.

            Args:
                hair_style (int): (Value range is 0-252.)
                hair_color (int): (Value range is 0-252.)
            """
            self._hair_style = hair_style
            self._hair_color = hair_color

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def hair_style(self) -> int:
            return self._hair_style

        @property
        def hair_color(self) -> int:
            return self._hair_color

        @staticmethod
        def serialize(writer: EoWriter, data: "AvatarChange.ChangeTypeDataHair") -> None:
            """
            Serializes an instance of `AvatarChange.ChangeTypeDataHair` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AvatarChange.ChangeTypeDataHair): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._hair_style is None:
                    raise SerializationError("hair_style must be provided.")
                writer.add_char(data._hair_style)
                if data._hair_color is None:
                    raise SerializationError("hair_color must be provided.")
                writer.add_char(data._hair_color)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "AvatarChange.ChangeTypeDataHair":
            """
            Deserializes an instance of `AvatarChange.ChangeTypeDataHair` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AvatarChange.ChangeTypeDataHair: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                hair_style = reader.get_char()
                hair_color = reader.get_char()
                result = AvatarChange.ChangeTypeDataHair(hair_style=hair_style, hair_color=hair_color)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AvatarChange.ChangeTypeDataHair(byte_size={repr(self._byte_size)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)})"

    class ChangeTypeDataHairColor:
        """
        Data associated with change_type value AvatarChangeType.HairColor
        """
        _byte_size: int = 0
        _hair_color: int

        def __init__(self, *, hair_color: int):
            """
            Create a new instance of AvatarChange.ChangeTypeDataHairColor.

            Args:
                hair_color (int): (Value range is 0-252.)
            """
            self._hair_color = hair_color

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def hair_color(self) -> int:
            return self._hair_color

        @staticmethod
        def serialize(writer: EoWriter, data: "AvatarChange.ChangeTypeDataHairColor") -> None:
            """
            Serializes an instance of `AvatarChange.ChangeTypeDataHairColor` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AvatarChange.ChangeTypeDataHairColor): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._hair_color is None:
                    raise SerializationError("hair_color must be provided.")
                writer.add_char(data._hair_color)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "AvatarChange.ChangeTypeDataHairColor":
            """
            Deserializes an instance of `AvatarChange.ChangeTypeDataHairColor` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AvatarChange.ChangeTypeDataHairColor: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                hair_color = reader.get_char()
                result = AvatarChange.ChangeTypeDataHairColor(hair_color=hair_color)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AvatarChange.ChangeTypeDataHairColor(byte_size={repr(self._byte_size)}, hair_color={repr(self._hair_color)})"
