# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .dialog_reply import DialogReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestAcceptClientPacket(Packet):
    """
    Response to a quest NPC dialog
    """
    _byte_size: int = 0
    _session_id: int
    _dialog_id: int
    _quest_id: int
    _npc_index: int
    _reply_type: DialogReply
    _reply_type_data: 'QuestAcceptClientPacket.ReplyTypeData'

    def __init__(self, *, session_id: int, dialog_id: int, quest_id: int, npc_index: int, reply_type: DialogReply, reply_type_data: 'QuestAcceptClientPacket.ReplyTypeData' = None):
        """
        Create a new instance of QuestAcceptClientPacket.

        Args:
            session_id (int): (Value range is 0-64008.)
            dialog_id (int): (Value range is 0-64008.)
            quest_id (int): (Value range is 0-64008.)
            npc_index (int): (Value range is 0-64008.)
            reply_type (DialogReply): 
            reply_type_data (QuestAcceptClientPacket.ReplyTypeData): Data associated with the `reply_type` field.
        """
        self._session_id = session_id
        self._dialog_id = dialog_id
        self._quest_id = quest_id
        self._npc_index = npc_index
        self._reply_type = reply_type
        self._reply_type_data = reply_type_data

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
    def dialog_id(self) -> int:
        return self._dialog_id

    @property
    def quest_id(self) -> int:
        return self._quest_id

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def reply_type(self) -> DialogReply:
        return self._reply_type

    @property
    def reply_type_data(self) -> 'QuestAcceptClientPacket.ReplyTypeData':
        """
        QuestAcceptClientPacket.ReplyTypeData: Data associated with the `reply_type` field.
        """
        return self._reply_type_data

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
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestAcceptClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestAcceptClientPacket") -> None:
        """
        Serializes an instance of `QuestAcceptClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestAcceptClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._dialog_id is None:
                raise SerializationError("dialog_id must be provided.")
            writer.add_short(data._dialog_id)
            if data._quest_id is None:
                raise SerializationError("quest_id must be provided.")
            writer.add_short(data._quest_id)
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            if data._reply_type is None:
                raise SerializationError("reply_type must be provided.")
            writer.add_char(int(data._reply_type))
            if data._reply_type == DialogReply.Ok:
                if not isinstance(data._reply_type_data, QuestAcceptClientPacket.ReplyTypeDataOk):
                    raise SerializationError("Expected reply_type_data to be type QuestAcceptClientPacket.ReplyTypeDataOk for reply_type " + DialogReply(data._reply_type).name + ".")
                QuestAcceptClientPacket.ReplyTypeDataOk.serialize(writer, data._reply_type_data)
            elif data._reply_type == DialogReply.Link:
                if not isinstance(data._reply_type_data, QuestAcceptClientPacket.ReplyTypeDataLink):
                    raise SerializationError("Expected reply_type_data to be type QuestAcceptClientPacket.ReplyTypeDataLink for reply_type " + DialogReply(data._reply_type).name + ".")
                QuestAcceptClientPacket.ReplyTypeDataLink.serialize(writer, data._reply_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestAcceptClientPacket":
        """
        Deserializes an instance of `QuestAcceptClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestAcceptClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            session_id = reader.get_short()
            dialog_id = reader.get_short()
            quest_id = reader.get_short()
            npc_index = reader.get_short()
            reply_type = DialogReply(reader.get_char())
            reply_type_data: QuestAcceptClientPacket.ReplyTypeData = None
            if reply_type == DialogReply.Ok:
                reply_type_data = QuestAcceptClientPacket.ReplyTypeDataOk.deserialize(reader)
            elif reply_type == DialogReply.Link:
                reply_type_data = QuestAcceptClientPacket.ReplyTypeDataLink.deserialize(reader)
            result = QuestAcceptClientPacket(session_id=session_id, dialog_id=dialog_id, quest_id=quest_id, npc_index=npc_index, reply_type=reply_type, reply_type_data=reply_type_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestAcceptClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, dialog_id={repr(self._dialog_id)}, quest_id={repr(self._quest_id)}, npc_index={repr(self._npc_index)}, reply_type={repr(self._reply_type)}, reply_type_data={repr(self._reply_type_data)})"

    ReplyTypeData = Union['QuestAcceptClientPacket.ReplyTypeDataOk', 'QuestAcceptClientPacket.ReplyTypeDataLink', None]
    """
    Data associated with different values of the `reply_type` field.
    """

    class ReplyTypeDataOk:
        """
        Data associated with reply_type value DialogReply.Ok
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of QuestAcceptClientPacket.ReplyTypeDataOk.
            """

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "QuestAcceptClientPacket.ReplyTypeDataOk") -> None:
            """
            Serializes an instance of `QuestAcceptClientPacket.ReplyTypeDataOk` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (QuestAcceptClientPacket.ReplyTypeDataOk): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_char(0)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "QuestAcceptClientPacket.ReplyTypeDataOk":
            """
            Deserializes an instance of `QuestAcceptClientPacket.ReplyTypeDataOk` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                QuestAcceptClientPacket.ReplyTypeDataOk: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_char()
                result = QuestAcceptClientPacket.ReplyTypeDataOk()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"QuestAcceptClientPacket.ReplyTypeDataOk(byte_size={repr(self._byte_size)})"

    class ReplyTypeDataLink:
        """
        Data associated with reply_type value DialogReply.Link
        """
        _byte_size: int = 0
        _action: int

        def __init__(self, *, action: int):
            """
            Create a new instance of QuestAcceptClientPacket.ReplyTypeDataLink.

            Args:
                action (int): (Value range is 0-252.)
            """
            self._action = action

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def action(self) -> int:
            return self._action

        @staticmethod
        def serialize(writer: EoWriter, data: "QuestAcceptClientPacket.ReplyTypeDataLink") -> None:
            """
            Serializes an instance of `QuestAcceptClientPacket.ReplyTypeDataLink` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (QuestAcceptClientPacket.ReplyTypeDataLink): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._action is None:
                    raise SerializationError("action must be provided.")
                writer.add_char(data._action)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "QuestAcceptClientPacket.ReplyTypeDataLink":
            """
            Deserializes an instance of `QuestAcceptClientPacket.ReplyTypeDataLink` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                QuestAcceptClientPacket.ReplyTypeDataLink: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                action = reader.get_char()
                result = QuestAcceptClientPacket.ReplyTypeDataLink(action=action)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"QuestAcceptClientPacket.ReplyTypeDataLink(byte_size={repr(self._byte_size)}, action={repr(self._action)})"
