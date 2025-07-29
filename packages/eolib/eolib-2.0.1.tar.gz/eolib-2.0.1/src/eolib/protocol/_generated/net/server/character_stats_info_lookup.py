# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats_info_lookup import CharacterSecondaryStatsInfoLookup
from .character_elemental_stats import CharacterElementalStats
from .character_base_stats import CharacterBaseStats
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsInfoLookup:
    """
    Character stats data.
    Sent with character info lookups.
    """
    _byte_size: int = 0
    _hp: int
    _max_hp: int
    _tp: int
    _max_tp: int
    _base_stats: CharacterBaseStats
    _secondary_stats: CharacterSecondaryStatsInfoLookup
    _elemental_stats: CharacterElementalStats

    def __init__(self, *, hp: int, max_hp: int, tp: int, max_tp: int, base_stats: CharacterBaseStats, secondary_stats: CharacterSecondaryStatsInfoLookup, elemental_stats: CharacterElementalStats):
        """
        Create a new instance of CharacterStatsInfoLookup.

        Args:
            hp (int): (Value range is 0-64008.)
            max_hp (int): (Value range is 0-64008.)
            tp (int): (Value range is 0-64008.)
            max_tp (int): (Value range is 0-64008.)
            base_stats (CharacterBaseStats): 
            secondary_stats (CharacterSecondaryStatsInfoLookup): 
            elemental_stats (CharacterElementalStats): 
        """
        self._hp = hp
        self._max_hp = max_hp
        self._tp = tp
        self._max_tp = max_tp
        self._base_stats = base_stats
        self._secondary_stats = secondary_stats
        self._elemental_stats = elemental_stats

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

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
    def base_stats(self) -> CharacterBaseStats:
        return self._base_stats

    @property
    def secondary_stats(self) -> CharacterSecondaryStatsInfoLookup:
        return self._secondary_stats

    @property
    def elemental_stats(self) -> CharacterElementalStats:
        return self._elemental_stats

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsInfoLookup") -> None:
        """
        Serializes an instance of `CharacterStatsInfoLookup` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsInfoLookup): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
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
            if data._base_stats is None:
                raise SerializationError("base_stats must be provided.")
            CharacterBaseStats.serialize(writer, data._base_stats)
            if data._secondary_stats is None:
                raise SerializationError("secondary_stats must be provided.")
            CharacterSecondaryStatsInfoLookup.serialize(writer, data._secondary_stats)
            if data._elemental_stats is None:
                raise SerializationError("elemental_stats must be provided.")
            CharacterElementalStats.serialize(writer, data._elemental_stats)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsInfoLookup":
        """
        Deserializes an instance of `CharacterStatsInfoLookup` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsInfoLookup: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            hp = reader.get_short()
            max_hp = reader.get_short()
            tp = reader.get_short()
            max_tp = reader.get_short()
            base_stats = CharacterBaseStats.deserialize(reader)
            secondary_stats = CharacterSecondaryStatsInfoLookup.deserialize(reader)
            elemental_stats = CharacterElementalStats.deserialize(reader)
            result = CharacterStatsInfoLookup(hp=hp, max_hp=max_hp, tp=tp, max_tp=max_tp, base_stats=base_stats, secondary_stats=secondary_stats, elemental_stats=elemental_stats)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsInfoLookup(byte_size={repr(self._byte_size)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)}, tp={repr(self._tp)}, max_tp={repr(self._max_tp)}, base_stats={repr(self._base_stats)}, secondary_stats={repr(self._secondary_stats)}, elemental_stats={repr(self._elemental_stats)})"
