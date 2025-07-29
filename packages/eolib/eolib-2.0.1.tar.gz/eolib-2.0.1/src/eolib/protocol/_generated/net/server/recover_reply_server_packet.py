# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class RecoverReplyServerPacket(Packet):
    """
    Karma/experience update
    """
    _byte_size: int = 0
    _experience: int
    _karma: int
    _level_up: Optional[int]
    _stat_points: Optional[int]
    _skill_points: Optional[int]

    def __init__(self, *, experience: int, karma: int, level_up: Optional[int] = None, stat_points: Optional[int] = None, skill_points: Optional[int] = None):
        """
        Create a new instance of RecoverReplyServerPacket.

        Args:
            experience (int): (Value range is 0-4097152080.)
            karma (int): (Value range is 0-64008.)
            level_up (Optional[int]): A value greater than 0 is "new level" and indicates the player leveled up. The official client reads this if the packet is larger than 6 bytes. (Value range is 0-252.)
            stat_points (Optional[int]): The official client reads this if the player leveled up (Value range is 0-64008.)
            skill_points (Optional[int]): The official client reads this if the player leveled up (Value range is 0-64008.)
        """
        self._experience = experience
        self._karma = karma
        self._level_up = level_up
        self._stat_points = stat_points
        self._skill_points = skill_points

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def experience(self) -> int:
        return self._experience

    @property
    def karma(self) -> int:
        return self._karma

    @property
    def level_up(self) -> Optional[int]:
        """
        A value greater than 0 is "new level" and indicates the player leveled up.
        The official client reads this if the packet is larger than 6 bytes.
        """
        return self._level_up

    @property
    def stat_points(self) -> Optional[int]:
        """
        The official client reads this if the player leveled up
        """
        return self._stat_points

    @property
    def skill_points(self) -> Optional[int]:
        """
        The official client reads this if the player leveled up
        """
        return self._skill_points

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Recover

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
        RecoverReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "RecoverReplyServerPacket") -> None:
        """
        Serializes an instance of `RecoverReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (RecoverReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._experience is None:
                raise SerializationError("experience must be provided.")
            writer.add_int(data._experience)
            if data._karma is None:
                raise SerializationError("karma must be provided.")
            writer.add_short(data._karma)
            reached_missing_optional = data._level_up is None
            if not reached_missing_optional:
                writer.add_char(cast(int, data._level_up))
            reached_missing_optional = reached_missing_optional or data._stat_points is None
            if not reached_missing_optional:
                writer.add_short(cast(int, data._stat_points))
            reached_missing_optional = reached_missing_optional or data._skill_points is None
            if not reached_missing_optional:
                writer.add_short(cast(int, data._skill_points))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "RecoverReplyServerPacket":
        """
        Deserializes an instance of `RecoverReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            RecoverReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            experience = reader.get_int()
            karma = reader.get_short()
            level_up: Optional[int] = None
            if reader.remaining > 0:
                level_up = reader.get_char()
            stat_points: Optional[int] = None
            if reader.remaining > 0:
                stat_points = reader.get_short()
            skill_points: Optional[int] = None
            if reader.remaining > 0:
                skill_points = reader.get_short()
            result = RecoverReplyServerPacket(experience=experience, karma=karma, level_up=level_up, stat_points=stat_points, skill_points=skill_points)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"RecoverReplyServerPacket(byte_size={repr(self._byte_size)}, experience={repr(self._experience)}, karma={repr(self._karma)}, level_up={repr(self._level_up)}, stat_points={repr(self._stat_points)}, skill_points={repr(self._skill_points)})"
