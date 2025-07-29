# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from collections.abc import Iterable
from .quest_progress_entry import QuestProgressEntry
from ..quest_page import QuestPage
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestListServerPacket(Packet):
    """
    Quest history / progress reply
    """
    _byte_size: int = 0
    _page: QuestPage
    _quests_count: int
    _page_data: 'QuestListServerPacket.PageData'

    def __init__(self, *, page: QuestPage, quests_count: int, page_data: 'QuestListServerPacket.PageData' = None):
        """
        Create a new instance of QuestListServerPacket.

        Args:
            page (QuestPage): 
            quests_count (int): (Value range is 0-64008.)
            page_data (QuestListServerPacket.PageData): Data associated with the `page` field.
        """
        self._page = page
        self._quests_count = quests_count
        self._page_data = page_data

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

    @property
    def quests_count(self) -> int:
        return self._quests_count

    @property
    def page_data(self) -> 'QuestListServerPacket.PageData':
        """
        QuestListServerPacket.PageData: Data associated with the `page` field.
        """
        return self._page_data

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
        QuestListServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestListServerPacket") -> None:
        """
        Serializes an instance of `QuestListServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestListServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._page is None:
                raise SerializationError("page must be provided.")
            writer.add_char(int(data._page))
            if data._quests_count is None:
                raise SerializationError("quests_count must be provided.")
            writer.add_short(data._quests_count)
            if data._page == QuestPage.Progress:
                if not isinstance(data._page_data, QuestListServerPacket.PageDataProgress):
                    raise SerializationError("Expected page_data to be type QuestListServerPacket.PageDataProgress for page " + QuestPage(data._page).name + ".")
                QuestListServerPacket.PageDataProgress.serialize(writer, data._page_data)
            elif data._page == QuestPage.History:
                if not isinstance(data._page_data, QuestListServerPacket.PageDataHistory):
                    raise SerializationError("Expected page_data to be type QuestListServerPacket.PageDataHistory for page " + QuestPage(data._page).name + ".")
                QuestListServerPacket.PageDataHistory.serialize(writer, data._page_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestListServerPacket":
        """
        Deserializes an instance of `QuestListServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestListServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            page = QuestPage(reader.get_char())
            quests_count = reader.get_short()
            page_data: QuestListServerPacket.PageData = None
            if page == QuestPage.Progress:
                page_data = QuestListServerPacket.PageDataProgress.deserialize(reader)
            elif page == QuestPage.History:
                page_data = QuestListServerPacket.PageDataHistory.deserialize(reader)
            reader.chunked_reading_mode = False
            result = QuestListServerPacket(page=page, quests_count=quests_count, page_data=page_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestListServerPacket(byte_size={repr(self._byte_size)}, page={repr(self._page)}, quests_count={repr(self._quests_count)}, page_data={repr(self._page_data)})"

    PageData = Union['QuestListServerPacket.PageDataProgress', 'QuestListServerPacket.PageDataHistory', None]
    """
    Data associated with different values of the `page` field.
    """

    class PageDataProgress:
        """
        Data associated with page value QuestPage.Progress
        """
        _byte_size: int = 0
        _quest_progress_entries: tuple[QuestProgressEntry, ...]

        def __init__(self, *, quest_progress_entries: Iterable[QuestProgressEntry]):
            """
            Create a new instance of QuestListServerPacket.PageDataProgress.

            Args:
                quest_progress_entries (Iterable[QuestProgressEntry]): 
            """
            self._quest_progress_entries = tuple(quest_progress_entries)

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def quest_progress_entries(self) -> tuple[QuestProgressEntry, ...]:
            return self._quest_progress_entries

        @staticmethod
        def serialize(writer: EoWriter, data: "QuestListServerPacket.PageDataProgress") -> None:
            """
            Serializes an instance of `QuestListServerPacket.PageDataProgress` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (QuestListServerPacket.PageDataProgress): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._quest_progress_entries is None:
                    raise SerializationError("quest_progress_entries must be provided.")
                for i in range(len(data._quest_progress_entries)):
                    QuestProgressEntry.serialize(writer, data._quest_progress_entries[i])
                    writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "QuestListServerPacket.PageDataProgress":
            """
            Deserializes an instance of `QuestListServerPacket.PageDataProgress` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                QuestListServerPacket.PageDataProgress: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                quest_progress_entries = []
                while reader.remaining > 0:
                    quest_progress_entries.append(QuestProgressEntry.deserialize(reader))
                    reader.next_chunk()
                result = QuestListServerPacket.PageDataProgress(quest_progress_entries=quest_progress_entries)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"QuestListServerPacket.PageDataProgress(byte_size={repr(self._byte_size)}, quest_progress_entries={repr(self._quest_progress_entries)})"

    class PageDataHistory:
        """
        Data associated with page value QuestPage.History
        """
        _byte_size: int = 0
        _completed_quests: tuple[str, ...]

        def __init__(self, *, completed_quests: Iterable[str]):
            """
            Create a new instance of QuestListServerPacket.PageDataHistory.

            Args:
                completed_quests (Iterable[str]): 
            """
            self._completed_quests = tuple(completed_quests)

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def completed_quests(self) -> tuple[str, ...]:
            return self._completed_quests

        @staticmethod
        def serialize(writer: EoWriter, data: "QuestListServerPacket.PageDataHistory") -> None:
            """
            Serializes an instance of `QuestListServerPacket.PageDataHistory` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (QuestListServerPacket.PageDataHistory): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._completed_quests is None:
                    raise SerializationError("completed_quests must be provided.")
                for i in range(len(data._completed_quests)):
                    writer.add_string(data._completed_quests[i])
                    writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "QuestListServerPacket.PageDataHistory":
            """
            Deserializes an instance of `QuestListServerPacket.PageDataHistory` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                QuestListServerPacket.PageDataHistory: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                completed_quests = []
                while reader.remaining > 0:
                    completed_quests.append(reader.get_string())
                    reader.next_chunk()
                result = QuestListServerPacket.PageDataHistory(completed_quests=completed_quests)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"QuestListServerPacket.PageDataHistory(byte_size={repr(self._byte_size)}, completed_quests={repr(self._completed_quests)})"
