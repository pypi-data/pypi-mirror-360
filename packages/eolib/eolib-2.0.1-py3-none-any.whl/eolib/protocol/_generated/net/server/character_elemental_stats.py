# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterElementalStats:
    """
    The 6 elemental character stats
    """
    _byte_size: int = 0
    _light: int
    _dark: int
    _fire: int
    _water: int
    _earth: int
    _wind: int

    def __init__(self, *, light: int, dark: int, fire: int, water: int, earth: int, wind: int):
        """
        Create a new instance of CharacterElementalStats.

        Args:
            light (int): (Value range is 0-64008.)
            dark (int): (Value range is 0-64008.)
            fire (int): (Value range is 0-64008.)
            water (int): (Value range is 0-64008.)
            earth (int): (Value range is 0-64008.)
            wind (int): (Value range is 0-64008.)
        """
        self._light = light
        self._dark = dark
        self._fire = fire
        self._water = water
        self._earth = earth
        self._wind = wind

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def light(self) -> int:
        return self._light

    @property
    def dark(self) -> int:
        return self._dark

    @property
    def fire(self) -> int:
        return self._fire

    @property
    def water(self) -> int:
        return self._water

    @property
    def earth(self) -> int:
        return self._earth

    @property
    def wind(self) -> int:
        return self._wind

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterElementalStats") -> None:
        """
        Serializes an instance of `CharacterElementalStats` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterElementalStats): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._light is None:
                raise SerializationError("light must be provided.")
            writer.add_short(data._light)
            if data._dark is None:
                raise SerializationError("dark must be provided.")
            writer.add_short(data._dark)
            if data._fire is None:
                raise SerializationError("fire must be provided.")
            writer.add_short(data._fire)
            if data._water is None:
                raise SerializationError("water must be provided.")
            writer.add_short(data._water)
            if data._earth is None:
                raise SerializationError("earth must be provided.")
            writer.add_short(data._earth)
            if data._wind is None:
                raise SerializationError("wind must be provided.")
            writer.add_short(data._wind)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterElementalStats":
        """
        Deserializes an instance of `CharacterElementalStats` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterElementalStats: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            light = reader.get_short()
            dark = reader.get_short()
            fire = reader.get_short()
            water = reader.get_short()
            earth = reader.get_short()
            wind = reader.get_short()
            result = CharacterElementalStats(light=light, dark=dark, fire=fire, water=water, earth=earth, wind=wind)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterElementalStats(byte_size={repr(self._byte_size)}, light={repr(self._light)}, dark={repr(self._dark)}, fire={repr(self._fire)}, water={repr(self._water)}, earth={repr(self._earth)}, wind={repr(self._wind)})"
