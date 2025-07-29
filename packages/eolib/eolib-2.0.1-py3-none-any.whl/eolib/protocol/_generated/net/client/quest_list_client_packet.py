# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..quest_page import QuestPage
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestListClientPacket(Packet):
    """
    Quest history / progress request
    """
    _byte_size: int = 0
    _page: QuestPage

    def __init__(self, *, page: QuestPage):
        """
        Create a new instance of QuestListClientPacket.

        Args:
            page (QuestPage): 
        """
        self._page = page

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def page(self) -> QuestPage:
        return self._page

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Quest

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.List

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestListClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestListClientPacket") -> None:
        """
        Serializes an instance of `QuestListClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestListClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._page is None:
                raise SerializationError("page must be provided.")
            writer.add_char(int(data._page))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestListClientPacket":
        """
        Deserializes an instance of `QuestListClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestListClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            page = QuestPage(reader.get_char())
            result = QuestListClientPacket(page=page)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestListClientPacket(byte_size={repr(self._byte_size)}, page={repr(self._page)})"
