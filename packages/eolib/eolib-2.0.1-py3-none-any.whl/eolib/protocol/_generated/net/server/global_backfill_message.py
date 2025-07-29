# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GlobalBackfillMessage:
    """
    A backfilled global chat message
    """
    _byte_size: int = 0
    _player_name: str
    _message: str

    def __init__(self, *, player_name: str, message: str):
        """
        Create a new instance of GlobalBackfillMessage.

        Args:
            player_name (str): 
            message (str): 
        """
        self._player_name = player_name
        self._message = message

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_name(self) -> str:
        return self._player_name

    @property
    def message(self) -> str:
        return self._message

    @staticmethod
    def serialize(writer: EoWriter, data: "GlobalBackfillMessage") -> None:
        """
        Serializes an instance of `GlobalBackfillMessage` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GlobalBackfillMessage): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._player_name is None:
                raise SerializationError("player_name must be provided.")
            writer.add_string(data._player_name)
            writer.add_byte(0xFF)
            if data._message is None:
                raise SerializationError("message must be provided.")
            writer.add_string(data._message)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GlobalBackfillMessage":
        """
        Deserializes an instance of `GlobalBackfillMessage` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GlobalBackfillMessage: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            player_name = reader.get_string()
            reader.next_chunk()
            message = reader.get_string()
            reader.chunked_reading_mode = False
            result = GlobalBackfillMessage(player_name=player_name, message=message)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GlobalBackfillMessage(byte_size={repr(self._byte_size)}, player_name={repr(self._player_name)}, message={repr(self._message)})"
