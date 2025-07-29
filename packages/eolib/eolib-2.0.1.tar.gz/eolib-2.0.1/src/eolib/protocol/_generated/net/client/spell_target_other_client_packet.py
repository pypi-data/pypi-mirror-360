# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .spell_target_type import SpellTargetType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SpellTargetOtherClientPacket(Packet):
    """
    Targeted spell cast
    """
    _byte_size: int = 0
    _target_type: SpellTargetType
    _previous_timestamp: int
    _spell_id: int
    _victim_id: int
    _timestamp: int

    def __init__(self, *, target_type: SpellTargetType, previous_timestamp: int, spell_id: int, victim_id: int, timestamp: int):
        """
        Create a new instance of SpellTargetOtherClientPacket.

        Args:
            target_type (SpellTargetType): 
            previous_timestamp (int): (Value range is 0-16194276.)
            spell_id (int): (Value range is 0-64008.)
            victim_id (int): (Value range is 0-64008.)
            timestamp (int): (Value range is 0-16194276.)
        """
        self._target_type = target_type
        self._previous_timestamp = previous_timestamp
        self._spell_id = spell_id
        self._victim_id = victim_id
        self._timestamp = timestamp

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def target_type(self) -> SpellTargetType:
        return self._target_type

    @property
    def previous_timestamp(self) -> int:
        return self._previous_timestamp

    @property
    def spell_id(self) -> int:
        return self._spell_id

    @property
    def victim_id(self) -> int:
        return self._victim_id

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Spell

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.TargetOther

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        SpellTargetOtherClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SpellTargetOtherClientPacket") -> None:
        """
        Serializes an instance of `SpellTargetOtherClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SpellTargetOtherClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._target_type is None:
                raise SerializationError("target_type must be provided.")
            writer.add_char(int(data._target_type))
            if data._previous_timestamp is None:
                raise SerializationError("previous_timestamp must be provided.")
            writer.add_three(data._previous_timestamp)
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
            if data._victim_id is None:
                raise SerializationError("victim_id must be provided.")
            writer.add_short(data._victim_id)
            if data._timestamp is None:
                raise SerializationError("timestamp must be provided.")
            writer.add_three(data._timestamp)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SpellTargetOtherClientPacket":
        """
        Deserializes an instance of `SpellTargetOtherClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SpellTargetOtherClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            target_type = SpellTargetType(reader.get_char())
            previous_timestamp = reader.get_three()
            spell_id = reader.get_short()
            victim_id = reader.get_short()
            timestamp = reader.get_three()
            result = SpellTargetOtherClientPacket(target_type=target_type, previous_timestamp=previous_timestamp, spell_id=spell_id, victim_id=victim_id, timestamp=timestamp)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SpellTargetOtherClientPacket(byte_size={repr(self._byte_size)}, target_type={repr(self._target_type)}, previous_timestamp={repr(self._previous_timestamp)}, spell_id={repr(self._spell_id)}, victim_id={repr(self._victim_id)}, timestamp={repr(self._timestamp)})"
