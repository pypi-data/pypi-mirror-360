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

class CitizenReplyClientPacket(Packet):
    """
    Subscribing to a town
    """
    _byte_size: int = 0
    _session_id: int
    _behavior_id: int
    _answers: tuple[str, ...]

    def __init__(self, *, session_id: int, behavior_id: int, answers: Iterable[str]):
        """
        Create a new instance of CitizenReplyClientPacket.

        Args:
            session_id (int): (Value range is 0-64008.)
            behavior_id (int): (Value range is 0-64008.)
            answers (Iterable[str]): (Length must be `3`.)
        """
        self._session_id = session_id
        self._behavior_id = behavior_id
        self._answers = tuple(answers)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def behavior_id(self) -> int:
        return self._behavior_id

    @property
    def answers(self) -> tuple[str, ...]:
        return self._answers

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
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CitizenReplyClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenReplyClientPacket") -> None:
        """
        Serializes an instance of `CitizenReplyClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenReplyClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            writer.add_byte(0xFF)
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            writer.add_byte(0xFF)
            if data._answers is None:
                raise SerializationError("answers must be provided.")
            if len(data._answers) != 3:
                raise SerializationError(f"Expected length of answers to be exactly 3, got {len(data._answers)}.")
            for i in range(3):
                if i > 0:
                    writer.add_byte(0xFF)
                writer.add_string(data._answers[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenReplyClientPacket":
        """
        Deserializes an instance of `CitizenReplyClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenReplyClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            session_id = reader.get_short()
            reader.next_chunk()
            behavior_id = reader.get_short()
            reader.next_chunk()
            answers = []
            for i in range(3):
                answers.append(reader.get_string())
                if i + 1 < 3:
                    reader.next_chunk()
            reader.chunked_reading_mode = False
            result = CitizenReplyClientPacket(session_id=session_id, behavior_id=behavior_id, answers=answers)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenReplyClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, behavior_id={repr(self._behavior_id)}, answers={repr(self._answers)})"
