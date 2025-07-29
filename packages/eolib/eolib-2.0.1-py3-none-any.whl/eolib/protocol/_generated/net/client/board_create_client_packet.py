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

class BoardCreateClientPacket(Packet):
    """
    Posting a new message to a town board
    """
    _byte_size: int = 0
    _board_id: int
    _post_subject: str
    _post_body: str

    def __init__(self, *, board_id: int, post_subject: str, post_body: str):
        """
        Create a new instance of BoardCreateClientPacket.

        Args:
            board_id (int): (Value range is 0-64008.)
            post_subject (str): 
            post_body (str): 
        """
        self._board_id = board_id
        self._post_subject = post_subject
        self._post_body = post_body

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
    def post_subject(self) -> str:
        return self._post_subject

    @property
    def post_body(self) -> str:
        return self._post_body

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
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BoardCreateClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BoardCreateClientPacket") -> None:
        """
        Serializes an instance of `BoardCreateClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BoardCreateClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._board_id is None:
                raise SerializationError("board_id must be provided.")
            writer.add_short(data._board_id)
            writer.add_byte(0xFF)
            if data._post_subject is None:
                raise SerializationError("post_subject must be provided.")
            writer.add_string(data._post_subject)
            writer.add_byte(0xFF)
            if data._post_body is None:
                raise SerializationError("post_body must be provided.")
            writer.add_string(data._post_body)
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BoardCreateClientPacket":
        """
        Deserializes an instance of `BoardCreateClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BoardCreateClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            board_id = reader.get_short()
            reader.next_chunk()
            post_subject = reader.get_string()
            reader.next_chunk()
            post_body = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            result = BoardCreateClientPacket(board_id=board_id, post_subject=post_subject, post_body=post_body)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BoardCreateClientPacket(byte_size={repr(self._byte_size)}, board_id={repr(self._board_id)}, post_subject={repr(self._post_subject)}, post_body={repr(self._post_body)})"
