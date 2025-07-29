# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats import CharacterSecondaryStats
from .character_base_stats import CharacterBaseStats
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsReset:
    """
    Character stats data.
    Sent when resetting stats and skills at a skill master NPC.
    """
    _byte_size: int = 0
    _stat_points: int
    _skill_points: int
    _hp: int
    _max_hp: int
    _tp: int
    _max_tp: int
    _max_sp: int
    _base: CharacterBaseStats
    _secondary: CharacterSecondaryStats

    def __init__(self, *, stat_points: int, skill_points: int, hp: int, max_hp: int, tp: int, max_tp: int, max_sp: int, base: CharacterBaseStats, secondary: CharacterSecondaryStats):
        """
        Create a new instance of CharacterStatsReset.

        Args:
            stat_points (int): (Value range is 0-64008.)
            skill_points (int): (Value range is 0-64008.)
            hp (int): (Value range is 0-64008.)
            max_hp (int): (Value range is 0-64008.)
            tp (int): (Value range is 0-64008.)
            max_tp (int): (Value range is 0-64008.)
            max_sp (int): (Value range is 0-64008.)
            base (CharacterBaseStats): 
            secondary (CharacterSecondaryStats): 
        """
        self._stat_points = stat_points
        self._skill_points = skill_points
        self._hp = hp
        self._max_hp = max_hp
        self._tp = tp
        self._max_tp = max_tp
        self._max_sp = max_sp
        self._base = base
        self._secondary = secondary

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def stat_points(self) -> int:
        return self._stat_points

    @property
    def skill_points(self) -> int:
        return self._skill_points

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def tp(self) -> int:
        return self._tp

    @property
    def max_tp(self) -> int:
        return self._max_tp

    @property
    def max_sp(self) -> int:
        return self._max_sp

    @property
    def base(self) -> CharacterBaseStats:
        return self._base

    @property
    def secondary(self) -> CharacterSecondaryStats:
        return self._secondary

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsReset") -> None:
        """
        Serializes an instance of `CharacterStatsReset` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsReset): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._stat_points is None:
                raise SerializationError("stat_points must be provided.")
            writer.add_short(data._stat_points)
            if data._skill_points is None:
                raise SerializationError("skill_points must be provided.")
            writer.add_short(data._skill_points)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)
            if data._max_sp is None:
                raise SerializationError("max_sp must be provided.")
            writer.add_short(data._max_sp)
            if data._base is None:
                raise SerializationError("base must be provided.")
            CharacterBaseStats.serialize(writer, data._base)
            if data._secondary is None:
                raise SerializationError("secondary must be provided.")
            CharacterSecondaryStats.serialize(writer, data._secondary)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsReset":
        """
        Deserializes an instance of `CharacterStatsReset` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsReset: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            stat_points = reader.get_short()
            skill_points = reader.get_short()
            hp = reader.get_short()
            max_hp = reader.get_short()
            tp = reader.get_short()
            max_tp = reader.get_short()
            max_sp = reader.get_short()
            base = CharacterBaseStats.deserialize(reader)
            secondary = CharacterSecondaryStats.deserialize(reader)
            result = CharacterStatsReset(stat_points=stat_points, skill_points=skill_points, hp=hp, max_hp=max_hp, tp=tp, max_tp=max_tp, max_sp=max_sp, base=base, secondary=secondary)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsReset(byte_size={repr(self._byte_size)}, stat_points={repr(self._stat_points)}, skill_points={repr(self._skill_points)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)}, tp={repr(self._tp)}, max_tp={repr(self._max_tp)}, max_sp={repr(self._max_sp)}, base={repr(self._base)}, secondary={repr(self._secondary)})"
