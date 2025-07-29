# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildMember:
    """
    Information about a guild member
    """
    _byte_size: int = 0
    _rank: int
    _name: str
    _rank_name: str

    def __init__(self, *, rank: int, name: str, rank_name: str):
        """
        Create a new instance of GuildMember.

        Args:
            rank (int): (Value range is 0-252.)
            name (str): 
            rank_name (str): 
        """
        self._rank = rank
        self._name = name
        self._rank_name = rank_name

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank_name(self) -> str:
        return self._rank_name

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildMember") -> None:
        """
        Serializes an instance of `GuildMember` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildMember): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._rank is None:
                raise SerializationError("rank must be provided.")
            writer.add_char(data._rank)
            writer.add_byte(0xFF)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._rank_name is None:
                raise SerializationError("rank_name must be provided.")
            writer.add_string(data._rank_name)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildMember":
        """
        Deserializes an instance of `GuildMember` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildMember: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            rank = reader.get_char()
            reader.next_chunk()
            name = reader.get_string()
            reader.next_chunk()
            rank_name = reader.get_string()
            reader.chunked_reading_mode = False
            result = GuildMember(rank=rank, name=name, rank_name=rank_name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildMember(byte_size={repr(self._byte_size)}, rank={repr(self._rank)}, name={repr(self._name)}, rank_name={repr(self._rank_name)})"
