# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats import CharacterSecondaryStats
from .character_base_stats import CharacterBaseStats
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsUpdate:
    """
    Character stats data.
    Sent when stats are updated.
    """
    _byte_size: int = 0
    _base_stats: CharacterBaseStats
    _max_hp: int
    _max_tp: int
    _max_sp: int
    _max_weight: int
    _secondary_stats: CharacterSecondaryStats

    def __init__(self, *, base_stats: CharacterBaseStats, max_hp: int, max_tp: int, max_sp: int, max_weight: int, secondary_stats: CharacterSecondaryStats):
        """
        Create a new instance of CharacterStatsUpdate.

        Args:
            base_stats (CharacterBaseStats): 
            max_hp (int): (Value range is 0-64008.)
            max_tp (int): (Value range is 0-64008.)
            max_sp (int): (Value range is 0-64008.)
            max_weight (int): (Value range is 0-64008.)
            secondary_stats (CharacterSecondaryStats): 
        """
        self._base_stats = base_stats
        self._max_hp = max_hp
        self._max_tp = max_tp
        self._max_sp = max_sp
        self._max_weight = max_weight
        self._secondary_stats = secondary_stats

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def base_stats(self) -> CharacterBaseStats:
        return self._base_stats

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def max_tp(self) -> int:
        return self._max_tp

    @property
    def max_sp(self) -> int:
        return self._max_sp

    @property
    def max_weight(self) -> int:
        return self._max_weight

    @property
    def secondary_stats(self) -> CharacterSecondaryStats:
        return self._secondary_stats

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsUpdate") -> None:
        """
        Serializes an instance of `CharacterStatsUpdate` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsUpdate): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._base_stats is None:
                raise SerializationError("base_stats must be provided.")
            CharacterBaseStats.serialize(writer, data._base_stats)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)
            if data._max_sp is None:
                raise SerializationError("max_sp must be provided.")
            writer.add_short(data._max_sp)
            if data._max_weight is None:
                raise SerializationError("max_weight must be provided.")
            writer.add_short(data._max_weight)
            if data._secondary_stats is None:
                raise SerializationError("secondary_stats must be provided.")
            CharacterSecondaryStats.serialize(writer, data._secondary_stats)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsUpdate":
        """
        Deserializes an instance of `CharacterStatsUpdate` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsUpdate: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            base_stats = CharacterBaseStats.deserialize(reader)
            max_hp = reader.get_short()
            max_tp = reader.get_short()
            max_sp = reader.get_short()
            max_weight = reader.get_short()
            secondary_stats = CharacterSecondaryStats.deserialize(reader)
            result = CharacterStatsUpdate(base_stats=base_stats, max_hp=max_hp, max_tp=max_tp, max_sp=max_sp, max_weight=max_weight, secondary_stats=secondary_stats)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsUpdate(byte_size={repr(self._byte_size)}, base_stats={repr(self._base_stats)}, max_hp={repr(self._max_hp)}, max_tp={repr(self._max_tp)}, max_sp={repr(self._max_sp)}, max_weight={repr(self._max_weight)}, secondary_stats={repr(self._secondary_stats)})"
