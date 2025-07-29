# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ServerSettings:
    """
    Settings sent with WELCOME_REPLY packet
    """
    _byte_size: int = 0
    _jail_map: int
    _rescue_map: int
    _rescue_coords: Coords
    _spy_and_light_guide_flood_rate: int
    _guardian_flood_rate: int
    _game_master_flood_rate: int
    _high_game_master_flood_rate: int

    def __init__(self, *, jail_map: int, rescue_map: int, rescue_coords: Coords, spy_and_light_guide_flood_rate: int, guardian_flood_rate: int, game_master_flood_rate: int, high_game_master_flood_rate: int):
        """
        Create a new instance of ServerSettings.

        Args:
            jail_map (int): (Value range is 0-64008.)
            rescue_map (int): (Value range is 0-64008.)
            rescue_coords (Coords): 
            spy_and_light_guide_flood_rate (int): (Value range is 0-64008.)
            guardian_flood_rate (int): (Value range is 0-64008.)
            game_master_flood_rate (int): (Value range is 0-64008.)
            high_game_master_flood_rate (int): (Value range is 0-64008.)
        """
        self._jail_map = jail_map
        self._rescue_map = rescue_map
        self._rescue_coords = rescue_coords
        self._spy_and_light_guide_flood_rate = spy_and_light_guide_flood_rate
        self._guardian_flood_rate = guardian_flood_rate
        self._game_master_flood_rate = game_master_flood_rate
        self._high_game_master_flood_rate = high_game_master_flood_rate

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def jail_map(self) -> int:
        return self._jail_map

    @property
    def rescue_map(self) -> int:
        return self._rescue_map

    @property
    def rescue_coords(self) -> Coords:
        return self._rescue_coords

    @property
    def spy_and_light_guide_flood_rate(self) -> int:
        return self._spy_and_light_guide_flood_rate

    @property
    def guardian_flood_rate(self) -> int:
        return self._guardian_flood_rate

    @property
    def game_master_flood_rate(self) -> int:
        return self._game_master_flood_rate

    @property
    def high_game_master_flood_rate(self) -> int:
        return self._high_game_master_flood_rate

    @staticmethod
    def serialize(writer: EoWriter, data: "ServerSettings") -> None:
        """
        Serializes an instance of `ServerSettings` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ServerSettings): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._jail_map is None:
                raise SerializationError("jail_map must be provided.")
            writer.add_short(data._jail_map)
            if data._rescue_map is None:
                raise SerializationError("rescue_map must be provided.")
            writer.add_short(data._rescue_map)
            if data._rescue_coords is None:
                raise SerializationError("rescue_coords must be provided.")
            Coords.serialize(writer, data._rescue_coords)
            if data._spy_and_light_guide_flood_rate is None:
                raise SerializationError("spy_and_light_guide_flood_rate must be provided.")
            writer.add_short(data._spy_and_light_guide_flood_rate)
            if data._guardian_flood_rate is None:
                raise SerializationError("guardian_flood_rate must be provided.")
            writer.add_short(data._guardian_flood_rate)
            if data._game_master_flood_rate is None:
                raise SerializationError("game_master_flood_rate must be provided.")
            writer.add_short(data._game_master_flood_rate)
            if data._high_game_master_flood_rate is None:
                raise SerializationError("high_game_master_flood_rate must be provided.")
            writer.add_short(data._high_game_master_flood_rate)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ServerSettings":
        """
        Deserializes an instance of `ServerSettings` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ServerSettings: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            jail_map = reader.get_short()
            rescue_map = reader.get_short()
            rescue_coords = Coords.deserialize(reader)
            spy_and_light_guide_flood_rate = reader.get_short()
            guardian_flood_rate = reader.get_short()
            game_master_flood_rate = reader.get_short()
            high_game_master_flood_rate = reader.get_short()
            result = ServerSettings(jail_map=jail_map, rescue_map=rescue_map, rescue_coords=rescue_coords, spy_and_light_guide_flood_rate=spy_and_light_guide_flood_rate, guardian_flood_rate=guardian_flood_rate, game_master_flood_rate=game_master_flood_rate, high_game_master_flood_rate=high_game_master_flood_rate)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ServerSettings(byte_size={repr(self._byte_size)}, jail_map={repr(self._jail_map)}, rescue_map={repr(self._rescue_map)}, rescue_coords={repr(self._rescue_coords)}, spy_and_light_guide_flood_rate={repr(self._spy_and_light_guide_flood_rate)}, guardian_flood_rate={repr(self._guardian_flood_rate)}, game_master_flood_rate={repr(self._game_master_flood_rate)}, high_game_master_flood_rate={repr(self._high_game_master_flood_rate)})"
