# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats import CharacterSecondaryStats
from .character_base_stats import CharacterBaseStats
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsEquipmentChange:
    """
    Character stats data.
    Sent when an item is equipped or unequipped.
    """
    _byte_size: int = 0
    _max_hp: int
    _max_tp: int
    _base_stats: CharacterBaseStats
    _secondary_stats: CharacterSecondaryStats

    def __init__(self, *, max_hp: int, max_tp: int, base_stats: CharacterBaseStats, secondary_stats: CharacterSecondaryStats):
        """
        Create a new instance of CharacterStatsEquipmentChange.

        Args:
            max_hp (int): (Value range is 0-64008.)
            max_tp (int): (Value range is 0-64008.)
            base_stats (CharacterBaseStats): 
            secondary_stats (CharacterSecondaryStats): 
        """
        self._max_hp = max_hp
        self._max_tp = max_tp
        self._base_stats = base_stats
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
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def max_tp(self) -> int:
        return self._max_tp

    @property
    def base_stats(self) -> CharacterBaseStats:
        return self._base_stats

    @property
    def secondary_stats(self) -> CharacterSecondaryStats:
        return self._secondary_stats

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsEquipmentChange") -> None:
        """
        Serializes an instance of `CharacterStatsEquipmentChange` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsEquipmentChange): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)
            if data._base_stats is None:
                raise SerializationError("base_stats must be provided.")
            CharacterBaseStats.serialize(writer, data._base_stats)
            if data._secondary_stats is None:
                raise SerializationError("secondary_stats must be provided.")
            CharacterSecondaryStats.serialize(writer, data._secondary_stats)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsEquipmentChange":
        """
        Deserializes an instance of `CharacterStatsEquipmentChange` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsEquipmentChange: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            max_hp = reader.get_short()
            max_tp = reader.get_short()
            base_stats = CharacterBaseStats.deserialize(reader)
            secondary_stats = CharacterSecondaryStats.deserialize(reader)
            result = CharacterStatsEquipmentChange(max_hp=max_hp, max_tp=max_tp, base_stats=base_stats, secondary_stats=secondary_stats)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsEquipmentChange(byte_size={repr(self._byte_size)}, max_hp={repr(self._max_hp)}, max_tp={repr(self._max_tp)}, base_stats={repr(self._base_stats)}, secondary_stats={repr(self._secondary_stats)})"
