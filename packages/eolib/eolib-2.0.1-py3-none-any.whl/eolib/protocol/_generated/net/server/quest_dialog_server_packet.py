# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .dialog_quest_entry import DialogQuestEntry
from .dialog_entry import DialogEntry
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestDialogServerPacket(Packet):
    """
    Quest selection dialog
    """
    _byte_size: int = 0
    _quest_count: int
    _behavior_id: int
    _quest_id: int
    _session_id: int
    _dialog_id: int
    _quest_entries: tuple[DialogQuestEntry, ...]
    _dialog_entries: tuple[DialogEntry, ...]

    def __init__(self, *, behavior_id: int, quest_id: int, session_id: int, dialog_id: int, quest_entries: Iterable[DialogQuestEntry], dialog_entries: Iterable[DialogEntry]):
        """
        Create a new instance of QuestDialogServerPacket.

        Args:
            behavior_id (int): (Value range is 0-64008.)
            quest_id (int): (Value range is 0-64008.)
            session_id (int): (Value range is 0-64008.)
            dialog_id (int): (Value range is 0-64008.)
            quest_entries (Iterable[DialogQuestEntry]): (Length must be 252 or less.)
            dialog_entries (Iterable[DialogEntry]): 
        """
        self._behavior_id = behavior_id
        self._quest_id = quest_id
        self._session_id = session_id
        self._dialog_id = dialog_id
        self._quest_entries = tuple(quest_entries)
        self._quest_count = len(self._quest_entries)
        self._dialog_entries = tuple(dialog_entries)

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
    def quest_id(self) -> int:
        return self._quest_id

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def dialog_id(self) -> int:
        return self._dialog_id

    @property
    def quest_entries(self) -> tuple[DialogQuestEntry, ...]:
        return self._quest_entries

    @property
    def dialog_entries(self) -> tuple[DialogEntry, ...]:
        return self._dialog_entries

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
        return PacketAction.Dialog

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestDialogServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestDialogServerPacket") -> None:
        """
        Serializes an instance of `QuestDialogServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestDialogServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._quest_count is None:
                raise SerializationError("quest_count must be provided.")
            writer.add_char(data._quest_count)
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._quest_id is None:
                raise SerializationError("quest_id must be provided.")
            writer.add_short(data._quest_id)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._dialog_id is None:
                raise SerializationError("dialog_id must be provided.")
            writer.add_short(data._dialog_id)
            writer.add_byte(0xFF)
            if data._quest_entries is None:
                raise SerializationError("quest_entries must be provided.")
            if len(data._quest_entries) > 252:
                raise SerializationError(f"Expected length of quest_entries to be 252 or less, got {len(data._quest_entries)}.")
            for i in range(data._quest_count):
                DialogQuestEntry.serialize(writer, data._quest_entries[i])
                writer.add_byte(0xFF)
            if data._dialog_entries is None:
                raise SerializationError("dialog_entries must be provided.")
            for i in range(len(data._dialog_entries)):
                DialogEntry.serialize(writer, data._dialog_entries[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestDialogServerPacket":
        """
        Deserializes an instance of `QuestDialogServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestDialogServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            quest_count = reader.get_char()
            behavior_id = reader.get_short()
            quest_id = reader.get_short()
            session_id = reader.get_short()
            dialog_id = reader.get_short()
            reader.next_chunk()
            quest_entries = []
            for i in range(quest_count):
                quest_entries.append(DialogQuestEntry.deserialize(reader))
                reader.next_chunk()
            dialog_entries = []
            while reader.remaining > 0:
                dialog_entries.append(DialogEntry.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            result = QuestDialogServerPacket(behavior_id=behavior_id, quest_id=quest_id, session_id=session_id, dialog_id=dialog_id, quest_entries=quest_entries, dialog_entries=dialog_entries)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestDialogServerPacket(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, quest_id={repr(self._quest_id)}, session_id={repr(self._session_id)}, dialog_id={repr(self._dialog_id)}, quest_entries={repr(self._quest_entries)}, dialog_entries={repr(self._dialog_entries)})"
