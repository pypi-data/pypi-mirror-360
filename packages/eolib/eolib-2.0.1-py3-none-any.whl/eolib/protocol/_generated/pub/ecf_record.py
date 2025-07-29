# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EcfRecord:
    """
    Record of Class data in an Endless Class File
    """
    _byte_size: int = 0
    _name_length: int
    _name: str
    _parent_type: int
    _stat_group: int
    _str: int
    _intl: int
    _wis: int
    _agi: int
    _con: int
    _cha: int

    def __init__(self, *, name: str, parent_type: int, stat_group: int, str: int, intl: int, wis: int, agi: int, con: int, cha: int):
        """
        Create a new instance of EcfRecord.

        Args:
            name (str): (Length must be 252 or less.)
            parent_type (int): (Value range is 0-252.)
            stat_group (int): (Value range is 0-252.)
            str (int): (Value range is 0-64008.)
            intl (int): (Value range is 0-64008.)
            wis (int): (Value range is 0-64008.)
            agi (int): (Value range is 0-64008.)
            con (int): (Value range is 0-64008.)
            cha (int): (Value range is 0-64008.)
        """
        self._name = name
        self._name_length = len(self._name)
        self._parent_type = parent_type
        self._stat_group = stat_group
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
    def name(self) -> str:
        return self._name

    @property
    def parent_type(self) -> int:
        return self._parent_type

    @property
    def stat_group(self) -> int:
        return self._stat_group

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
    def serialize(writer: EoWriter, data: "EcfRecord") -> None:
        """
        Serializes an instance of `EcfRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EcfRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._parent_type is None:
                raise SerializationError("parent_type must be provided.")
            writer.add_char(data._parent_type)
            if data._stat_group is None:
                raise SerializationError("stat_group must be provided.")
            writer.add_char(data._stat_group)
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
    def deserialize(reader: EoReader) -> "EcfRecord":
        """
        Deserializes an instance of `EcfRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EcfRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            name_length = reader.get_char()
            name = reader.get_fixed_string(name_length, False)
            parent_type = reader.get_char()
            stat_group = reader.get_char()
            str = reader.get_short()
            intl = reader.get_short()
            wis = reader.get_short()
            agi = reader.get_short()
            con = reader.get_short()
            cha = reader.get_short()
            result = EcfRecord(name=name, parent_type=parent_type, stat_group=stat_group, str=str, intl=intl, wis=wis, agi=agi, con=con, cha=cha)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EcfRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, parent_type={repr(self._parent_type)}, stat_group={repr(self._stat_group)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)})"
