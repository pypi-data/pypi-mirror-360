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

class QuestUseClientPacket(Packet):
    """
    Talking to a quest NPC
    """
    _byte_size: int = 0
    _npc_index: int
    _quest_id: int

    def __init__(self, *, npc_index: int, quest_id: int):
        """
        Create a new instance of QuestUseClientPacket.

        Args:
            npc_index (int): (Value range is 0-64008.)
            quest_id (int): Quest ID is 0 unless the player explicitly selects a quest from the quest switcher (Value range is 0-64008.)
        """
        self._npc_index = npc_index
        self._quest_id = quest_id

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def quest_id(self) -> int:
        """
        Quest ID is 0 unless the player explicitly selects a quest from the quest switcher
        """
        return self._quest_id

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
        return PacketAction.Use

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestUseClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestUseClientPacket") -> None:
        """
        Serializes an instance of `QuestUseClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestUseClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            if data._quest_id is None:
                raise SerializationError("quest_id must be provided.")
            writer.add_short(data._quest_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestUseClientPacket":
        """
        Deserializes an instance of `QuestUseClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestUseClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_index = reader.get_short()
            quest_id = reader.get_short()
            result = QuestUseClientPacket(npc_index=npc_index, quest_id=quest_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestUseClientPacket(byte_size={repr(self._byte_size)}, npc_index={repr(self._npc_index)}, quest_id={repr(self._quest_id)})"
