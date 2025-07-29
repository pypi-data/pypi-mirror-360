# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyMember:
    """
    A member of the player's party
    """
    _byte_size: int = 0
    _player_id: int
    _leader: bool
    _level: int
    _hp_percentage: int
    _name: str

    def __init__(self, *, player_id: int, leader: bool, level: int, hp_percentage: int, name: str):
        """
        Create a new instance of PartyMember.

        Args:
            player_id (int): (Value range is 0-64008.)
            leader (bool): 
            level (int): (Value range is 0-252.)
            hp_percentage (int): (Value range is 0-252.)
            name (str): 
        """
        self._player_id = player_id
        self._leader = leader
        self._level = level
        self._hp_percentage = hp_percentage
        self._name = name

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
    def leader(self) -> bool:
        return self._leader

    @property
    def level(self) -> int:
        return self._level

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @property
    def name(self) -> str:
        return self._name

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyMember") -> None:
        """
        Serializes an instance of `PartyMember` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyMember): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._leader is None:
                raise SerializationError("leader must be provided.")
            writer.add_char(1 if data._leader else 0)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyMember":
        """
        Deserializes an instance of `PartyMember` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyMember: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            leader = reader.get_char() != 0
            level = reader.get_char()
            hp_percentage = reader.get_char()
            name = reader.get_string()
            result = PartyMember(player_id=player_id, leader=leader, level=level, hp_percentage=hp_percentage, name=name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyMember(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, leader={repr(self._leader)}, level={repr(self._level)}, hp_percentage={repr(self._hp_percentage)}, name={repr(self._name)})"
