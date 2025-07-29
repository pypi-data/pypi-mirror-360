# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TalkMessageRecord:
    """
    Record of a message that an NPC can say
    """
    _byte_size: int = 0
    _message_length: int
    _message: str

    def __init__(self, *, message: str):
        """
        Create a new instance of TalkMessageRecord.

        Args:
            message (str): (Length must be 252 or less.)
        """
        self._message = message
        self._message_length = len(self._message)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def message(self) -> str:
        return self._message

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkMessageRecord") -> None:
        """
        Serializes an instance of `TalkMessageRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkMessageRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._message_length is None:
                raise SerializationError("message_length must be provided.")
            writer.add_char(data._message_length)
            if data._message is None:
                raise SerializationError("message must be provided.")
            if len(data._message) > 252:
                raise SerializationError(f"Expected length of message to be 252 or less, got {len(data._message)}.")
            writer.add_fixed_string(data._message, data._message_length, False)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkMessageRecord":
        """
        Deserializes an instance of `TalkMessageRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkMessageRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            message_length = reader.get_char()
            message = reader.get_fixed_string(message_length, False)
            result = TalkMessageRecord(message=message)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkMessageRecord(byte_size={repr(self._byte_size)}, message={repr(self._message)})"
