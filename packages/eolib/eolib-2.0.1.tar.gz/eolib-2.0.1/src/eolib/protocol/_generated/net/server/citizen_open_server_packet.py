# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CitizenOpenServerPacket(Packet):
    """
    Response from talking to a citizenship NPC
    """
    _byte_size: int = 0
    _behavior_id: int
    _current_home_id: int
    _session_id: int
    _questions: tuple[str, ...]

    def __init__(self, *, behavior_id: int, current_home_id: int, session_id: int, questions: Iterable[str]):
        """
        Create a new instance of CitizenOpenServerPacket.

        Args:
            behavior_id (int): (Value range is 0-16194276.)
            current_home_id (int): (Value range is 0-252.)
            session_id (int): (Value range is 0-64008.)
            questions (Iterable[str]): (Length must be `3`.)
        """
        self._behavior_id = behavior_id
        self._current_home_id = current_home_id
        self._session_id = session_id
        self._questions = tuple(questions)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        return self._behavior_id

    @property
    def current_home_id(self) -> int:
        return self._current_home_id

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def questions(self) -> tuple[str, ...]:
        return self._questions

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Citizen

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CitizenOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenOpenServerPacket") -> None:
        """
        Serializes an instance of `CitizenOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_three(data._behavior_id)
            if data._current_home_id is None:
                raise SerializationError("current_home_id must be provided.")
            writer.add_char(data._current_home_id)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            writer.add_byte(0xFF)
            if data._questions is None:
                raise SerializationError("questions must be provided.")
            if len(data._questions) != 3:
                raise SerializationError(f"Expected length of questions to be exactly 3, got {len(data._questions)}.")
            for i in range(3):
                if i > 0:
                    writer.add_byte(0xFF)
                writer.add_string(data._questions[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenOpenServerPacket":
        """
        Deserializes an instance of `CitizenOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenOpenServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            behavior_id = reader.get_three()
            current_home_id = reader.get_char()
            session_id = reader.get_short()
            reader.next_chunk()
            questions = []
            for i in range(3):
                questions.append(reader.get_string())
                if i + 1 < 3:
                    reader.next_chunk()
            reader.chunked_reading_mode = False
            result = CitizenOpenServerPacket(behavior_id=behavior_id, current_home_id=current_home_id, session_id=session_id, questions=questions)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenOpenServerPacket(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, current_home_id={repr(self._current_home_id)}, session_id={repr(self._session_id)}, questions={repr(self._questions)})"
