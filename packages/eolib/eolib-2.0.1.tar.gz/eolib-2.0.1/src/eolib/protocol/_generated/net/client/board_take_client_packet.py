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

class BoardTakeClientPacket(Packet):
    """
    Reading a post on a town board
    """
    _byte_size: int = 0
    _board_id: int
    _post_id: int

    def __init__(self, *, board_id: int, post_id: int):
        """
        Create a new instance of BoardTakeClientPacket.

        Args:
            board_id (int): (Value range is 0-64008.)
            post_id (int): (Value range is 0-64008.)
        """
        self._board_id = board_id
        self._post_id = post_id

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def board_id(self) -> int:
        return self._board_id

    @property
    def post_id(self) -> int:
        return self._post_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Board

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Take

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BoardTakeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BoardTakeClientPacket") -> None:
        """
        Serializes an instance of `BoardTakeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BoardTakeClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._board_id is None:
                raise SerializationError("board_id must be provided.")
            writer.add_short(data._board_id)
            if data._post_id is None:
                raise SerializationError("post_id must be provided.")
            writer.add_short(data._post_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BoardTakeClientPacket":
        """
        Deserializes an instance of `BoardTakeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BoardTakeClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            board_id = reader.get_short()
            post_id = reader.get_short()
            result = BoardTakeClientPacket(board_id=board_id, post_id=post_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BoardTakeClientPacket(byte_size={repr(self._byte_size)}, board_id={repr(self._board_id)}, post_id={repr(self._post_id)})"
