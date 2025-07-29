# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ArenaAcceptServerPacket(Packet):
    """
    Arena win message
    """
    _byte_size: int = 0
    _winner_name: str
    _kills_count: int
    _killer_name: str
    _victim_name: str

    def __init__(self, *, winner_name: str, kills_count: int, killer_name: str, victim_name: str):
        """
        Create a new instance of ArenaAcceptServerPacket.

        Args:
            winner_name (str): 
            kills_count (int): (Value range is 0-4097152080.)
            killer_name (str): 
            victim_name (str): 
        """
        self._winner_name = winner_name
        self._kills_count = kills_count
        self._killer_name = killer_name
        self._victim_name = victim_name

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def winner_name(self) -> str:
        return self._winner_name

    @property
    def kills_count(self) -> int:
        return self._kills_count

    @property
    def killer_name(self) -> str:
        return self._killer_name

    @property
    def victim_name(self) -> str:
        return self._victim_name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Arena

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ArenaAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ArenaAcceptServerPacket") -> None:
        """
        Serializes an instance of `ArenaAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ArenaAcceptServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._winner_name is None:
                raise SerializationError("winner_name must be provided.")
            writer.add_string(data._winner_name)
            writer.add_byte(0xFF)
            if data._kills_count is None:
                raise SerializationError("kills_count must be provided.")
            writer.add_int(data._kills_count)
            writer.add_byte(0xFF)
            if data._killer_name is None:
                raise SerializationError("killer_name must be provided.")
            writer.add_string(data._killer_name)
            writer.add_byte(0xFF)
            if data._victim_name is None:
                raise SerializationError("victim_name must be provided.")
            writer.add_string(data._victim_name)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ArenaAcceptServerPacket":
        """
        Deserializes an instance of `ArenaAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ArenaAcceptServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            winner_name = reader.get_string()
            reader.next_chunk()
            kills_count = reader.get_int()
            reader.next_chunk()
            killer_name = reader.get_string()
            reader.next_chunk()
            victim_name = reader.get_string()
            reader.chunked_reading_mode = False
            result = ArenaAcceptServerPacket(winner_name=winner_name, kills_count=kills_count, killer_name=killer_name, victim_name=victim_name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ArenaAcceptServerPacket(byte_size={repr(self._byte_size)}, winner_name={repr(self._winner_name)}, kills_count={repr(self._kills_count)}, killer_name={repr(self._killer_name)}, victim_name={repr(self._victim_name)})"
