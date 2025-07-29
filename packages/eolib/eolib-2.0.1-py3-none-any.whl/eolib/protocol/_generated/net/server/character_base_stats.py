# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterBaseStats:
    """
    The 6 base character stats
    """
    _byte_size: int = 0
    _str: int
    _intl: int
    _wis: int
    _agi: int
    _con: int
    _cha: int

    def __init__(self, *, str: int, intl: int, wis: int, agi: int, con: int, cha: int):
        """
        Create a new instance of CharacterBaseStats.

        Args:
            str (int): (Value range is 0-64008.)
            intl (int): (Value range is 0-64008.)
            wis (int): (Value range is 0-64008.)
            agi (int): (Value range is 0-64008.)
            con (int): (Value range is 0-64008.)
            cha (int): (Value range is 0-64008.)
        """
        self._str = str
        self._intl = intl
        self._wis = wis
        self._agi = agi
        self._con = con
        self._cha = cha

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def str(self) -> int:
        return self._str

    @property
    def intl(self) -> int:
        return self._intl

    @property
    def wis(self) -> int:
        return self._wis

    @property
    def agi(self) -> int:
        return self._agi

    @property
    def con(self) -> int:
        return self._con

    @property
    def cha(self) -> int:
        return self._cha

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterBaseStats") -> None:
        """
        Serializes an instance of `CharacterBaseStats` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterBaseStats): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._str is None:
                raise SerializationError("str must be provided.")
            writer.add_short(data._str)
            if data._intl is None:
                raise SerializationError("intl must be provided.")
            writer.add_short(data._intl)
            if data._wis is None:
                raise SerializationError("wis must be provided.")
            writer.add_short(data._wis)
            if data._agi is None:
                raise SerializationError("agi must be provided.")
            writer.add_short(data._agi)
            if data._con is None:
                raise SerializationError("con must be provided.")
            writer.add_short(data._con)
            if data._cha is None:
                raise SerializationError("cha must be provided.")
            writer.add_short(data._cha)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterBaseStats":
        """
        Deserializes an instance of `CharacterBaseStats` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterBaseStats: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            str = reader.get_short()
            intl = reader.get_short()
            wis = reader.get_short()
            agi = reader.get_short()
            con = reader.get_short()
            cha = reader.get_short()
            result = CharacterBaseStats(str=str, intl=intl, wis=wis, agi=agi, con=con, cha=cha)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterBaseStats(byte_size={repr(self._byte_size)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)})"
