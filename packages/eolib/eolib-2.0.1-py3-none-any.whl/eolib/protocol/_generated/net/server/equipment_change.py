# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EquipmentChange:
    """
    Player equipment data.
    Sent when a player's visible equipment changes.
    Note that these values are graphic IDs.
    """
    _byte_size: int = 0
    _boots: int
    _armor: int
    _hat: int
    _weapon: int
    _shield: int

    def __init__(self, *, boots: int, armor: int, hat: int, weapon: int, shield: int):
        """
        Create a new instance of EquipmentChange.

        Args:
            boots (int): (Value range is 0-64008.)
            armor (int): (Value range is 0-64008.)
            hat (int): (Value range is 0-64008.)
            weapon (int): (Value range is 0-64008.)
            shield (int): (Value range is 0-64008.)
        """
        self._boots = boots
        self._armor = armor
        self._hat = hat
        self._weapon = weapon
        self._shield = shield

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def boots(self) -> int:
        return self._boots

    @property
    def armor(self) -> int:
        return self._armor

    @property
    def hat(self) -> int:
        return self._hat

    @property
    def weapon(self) -> int:
        return self._weapon

    @property
    def shield(self) -> int:
        return self._shield

    @staticmethod
    def serialize(writer: EoWriter, data: "EquipmentChange") -> None:
        """
        Serializes an instance of `EquipmentChange` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EquipmentChange): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._boots is None:
                raise SerializationError("boots must be provided.")
            writer.add_short(data._boots)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
            if data._hat is None:
                raise SerializationError("hat must be provided.")
            writer.add_short(data._hat)
            if data._weapon is None:
                raise SerializationError("weapon must be provided.")
            writer.add_short(data._weapon)
            if data._shield is None:
                raise SerializationError("shield must be provided.")
            writer.add_short(data._shield)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EquipmentChange":
        """
        Deserializes an instance of `EquipmentChange` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EquipmentChange: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            boots = reader.get_short()
            armor = reader.get_short()
            hat = reader.get_short()
            weapon = reader.get_short()
            shield = reader.get_short()
            result = EquipmentChange(boots=boots, armor=armor, hat=hat, weapon=weapon, shield=shield)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EquipmentChange(byte_size={repr(self._byte_size)}, boots={repr(self._boots)}, armor={repr(self._armor)}, hat={repr(self._hat)}, weapon={repr(self._weapon)}, shield={repr(self._shield)})"
