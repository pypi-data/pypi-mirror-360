# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .talk_message_record import TalkMessageRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TalkRecord:
    """
    Record of Talk data in an Endless Talk File
    """
    _byte_size: int = 0
    _npc_id: int
    _rate: int
    _messages_count: int
    _messages: tuple[TalkMessageRecord, ...]

    def __init__(self, *, npc_id: int, rate: int, messages: Iterable[TalkMessageRecord]):
        """
        Create a new instance of TalkRecord.

        Args:
            npc_id (int): ID of the NPC that will talk (Value range is 0-64008.)
            rate (int): Chance that the NPC will talk (0-100) (Value range is 0-252.)
            messages (Iterable[TalkMessageRecord]): (Length must be 252 or less.)
        """
        self._npc_id = npc_id
        self._rate = rate
        self._messages = tuple(messages)
        self._messages_count = len(self._messages)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_id(self) -> int:
        """
        ID of the NPC that will talk
        """
        return self._npc_id

    @property
    def rate(self) -> int:
        """
        Chance that the NPC will talk (0-100)
        """
        return self._rate

    @property
    def messages(self) -> tuple[TalkMessageRecord, ...]:
        return self._messages

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkRecord") -> None:
        """
        Serializes an instance of `TalkRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_id is None:
                raise SerializationError("npc_id must be provided.")
            writer.add_short(data._npc_id)
            if data._rate is None:
                raise SerializationError("rate must be provided.")
            writer.add_char(data._rate)
            if data._messages_count is None:
                raise SerializationError("messages_count must be provided.")
            writer.add_char(data._messages_count)
            if data._messages is None:
                raise SerializationError("messages must be provided.")
            if len(data._messages) > 252:
                raise SerializationError(f"Expected length of messages to be 252 or less, got {len(data._messages)}.")
            for i in range(data._messages_count):
                TalkMessageRecord.serialize(writer, data._messages[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkRecord":
        """
        Deserializes an instance of `TalkRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_id = reader.get_short()
            rate = reader.get_char()
            messages_count = reader.get_char()
            messages = []
            for i in range(messages_count):
                messages.append(TalkMessageRecord.deserialize(reader))
            result = TalkRecord(npc_id=npc_id, rate=rate, messages=messages)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkRecord(byte_size={repr(self._byte_size)}, npc_id={repr(self._npc_id)}, rate={repr(self._rate)}, messages={repr(self._messages)})"
