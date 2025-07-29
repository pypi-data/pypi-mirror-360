# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from collections.abc import Iterable
from .character_selection_list_entry import CharacterSelectionListEntry
from .character_reply import CharacterReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterReplyServerPacket(Packet):
    """
    Reply to client Character-family packets
    """
    _byte_size: int = 0
    _reply_code: CharacterReply
    _reply_code_data: 'CharacterReplyServerPacket.ReplyCodeData'

    def __init__(self, *, reply_code: CharacterReply, reply_code_data: 'CharacterReplyServerPacket.ReplyCodeData' = None):
        """
        Create a new instance of CharacterReplyServerPacket.

        Args:
            reply_code (CharacterReply): Sometimes a CharacterReply code, sometimes a session ID for character creation
            reply_code_data (CharacterReplyServerPacket.ReplyCodeData): Data associated with the `reply_code` field.
        """
        self._reply_code = reply_code
        self._reply_code_data = reply_code_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> CharacterReply:
        """
        Sometimes a CharacterReply code, sometimes a session ID for character creation
        """
        return self._reply_code

    @property
    def reply_code_data(self) -> 'CharacterReplyServerPacket.ReplyCodeData':
        """
        CharacterReplyServerPacket.ReplyCodeData: Data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Character

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
        CharacterReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterReplyServerPacket") -> None:
        """
        Serializes an instance of `CharacterReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._reply_code is None:
                raise SerializationError("reply_code must be provided.")
            writer.add_short(int(data._reply_code))
            if data._reply_code == 0:
                if data._reply_code_data is not None:
                    raise SerializationError("Expected reply_code_data to be None for reply_code " + CharacterReply(data._reply_code).name + ".")
            elif data._reply_code == CharacterReply.Exists:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataExists):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataExists for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataExists.serialize(writer, data._reply_code_data)
            elif data._reply_code == CharacterReply.Full:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataFull):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataFull for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataFull.serialize(writer, data._reply_code_data)
            elif data._reply_code == CharacterReply.Full3:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataFull3):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataFull3 for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataFull3.serialize(writer, data._reply_code_data)
            elif data._reply_code == CharacterReply.NotApproved:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataNotApproved):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataNotApproved for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataNotApproved.serialize(writer, data._reply_code_data)
            elif data._reply_code == CharacterReply.Ok:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataOk):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataOk for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataOk.serialize(writer, data._reply_code_data)
            elif data._reply_code == CharacterReply.Deleted:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataDeleted):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataDeleted for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataDeleted.serialize(writer, data._reply_code_data)
            elif data._reply_code == 7:
                if data._reply_code_data is not None:
                    raise SerializationError("Expected reply_code_data to be None for reply_code " + CharacterReply(data._reply_code).name + ".")
            elif data._reply_code == 8:
                if data._reply_code_data is not None:
                    raise SerializationError("Expected reply_code_data to be None for reply_code " + CharacterReply(data._reply_code).name + ".")
            elif data._reply_code == 9:
                if data._reply_code_data is not None:
                    raise SerializationError("Expected reply_code_data to be None for reply_code " + CharacterReply(data._reply_code).name + ".")
            else:
                if not isinstance(data._reply_code_data, CharacterReplyServerPacket.ReplyCodeDataDefault):
                    raise SerializationError("Expected reply_code_data to be type CharacterReplyServerPacket.ReplyCodeDataDefault for reply_code " + CharacterReply(data._reply_code).name + ".")
                CharacterReplyServerPacket.ReplyCodeDataDefault.serialize(writer, data._reply_code_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterReplyServerPacket":
        """
        Deserializes an instance of `CharacterReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            reply_code = CharacterReply(reader.get_short())
            reply_code_data: CharacterReplyServerPacket.ReplyCodeData = None
            if reply_code == 0:
                reply_code_data = None
            elif reply_code == CharacterReply.Exists:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataExists.deserialize(reader)
            elif reply_code == CharacterReply.Full:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataFull.deserialize(reader)
            elif reply_code == CharacterReply.Full3:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataFull3.deserialize(reader)
            elif reply_code == CharacterReply.NotApproved:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataNotApproved.deserialize(reader)
            elif reply_code == CharacterReply.Ok:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataOk.deserialize(reader)
            elif reply_code == CharacterReply.Deleted:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataDeleted.deserialize(reader)
            elif reply_code == 7:
                reply_code_data = None
            elif reply_code == 8:
                reply_code_data = None
            elif reply_code == 9:
                reply_code_data = None
            else:
                reply_code_data = CharacterReplyServerPacket.ReplyCodeDataDefault.deserialize(reader)
            reader.chunked_reading_mode = False
            result = CharacterReplyServerPacket(reply_code=reply_code, reply_code_data=reply_code_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['CharacterReplyServerPacket.ReplyCodeDataExists', 'CharacterReplyServerPacket.ReplyCodeDataFull', 'CharacterReplyServerPacket.ReplyCodeDataFull3', 'CharacterReplyServerPacket.ReplyCodeDataNotApproved', 'CharacterReplyServerPacket.ReplyCodeDataOk', 'CharacterReplyServerPacket.ReplyCodeDataDeleted', 'CharacterReplyServerPacket.ReplyCodeDataDefault', None]
    """
    Data associated with different values of the `reply_code` field.
    """

    class ReplyCodeDataExists:
        """
        Data associated with reply_code value CharacterReply.Exists
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataExists.
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
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataExists") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataExists` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataExists): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataExists":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataExists` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataExists: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = CharacterReplyServerPacket.ReplyCodeDataExists()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataExists(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataFull:
        """
        Data associated with reply_code value CharacterReply.Full
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataFull.
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
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataFull") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataFull` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataFull): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataFull":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataFull` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataFull: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = CharacterReplyServerPacket.ReplyCodeDataFull()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataFull(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataFull3:
        """
        Data associated with reply_code value CharacterReply.Full3
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataFull3.
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
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataFull3") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataFull3` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataFull3): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataFull3":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataFull3` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataFull3: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = CharacterReplyServerPacket.ReplyCodeDataFull3()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataFull3(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataNotApproved:
        """
        Data associated with reply_code value CharacterReply.NotApproved
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataNotApproved.
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
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataNotApproved") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataNotApproved` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataNotApproved): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataNotApproved":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataNotApproved` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataNotApproved: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = CharacterReplyServerPacket.ReplyCodeDataNotApproved()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataNotApproved(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataOk:
        """
        Data associated with reply_code value CharacterReply.Ok
        """
        _byte_size: int = 0
        _characters_count: int
        _characters: tuple[CharacterSelectionListEntry, ...]

        def __init__(self, *, characters: Iterable[CharacterSelectionListEntry]):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataOk.

            Args:
                characters (Iterable[CharacterSelectionListEntry]): (Length must be 252 or less.)
            """
            self._characters = tuple(characters)
            self._characters_count = len(self._characters)

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def characters(self) -> tuple[CharacterSelectionListEntry, ...]:
            return self._characters

        @staticmethod
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataOk") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataOk` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataOk): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._characters_count is None:
                    raise SerializationError("characters_count must be provided.")
                writer.add_char(data._characters_count)
                writer.add_char(0)
                writer.add_byte(0xFF)
                if data._characters is None:
                    raise SerializationError("characters must be provided.")
                if len(data._characters) > 252:
                    raise SerializationError(f"Expected length of characters to be 252 or less, got {len(data._characters)}.")
                for i in range(data._characters_count):
                    CharacterSelectionListEntry.serialize(writer, data._characters[i])
                    writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataOk":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataOk` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataOk: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                characters_count = reader.get_char()
                reader.get_char()
                reader.next_chunk()
                characters = []
                for i in range(characters_count):
                    characters.append(CharacterSelectionListEntry.deserialize(reader))
                    reader.next_chunk()
                result = CharacterReplyServerPacket.ReplyCodeDataOk(characters=characters)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataOk(byte_size={repr(self._byte_size)}, characters={repr(self._characters)})"

    class ReplyCodeDataDeleted:
        """
        Data associated with reply_code value CharacterReply.Deleted
        """
        _byte_size: int = 0
        _characters_count: int
        _characters: tuple[CharacterSelectionListEntry, ...]

        def __init__(self, *, characters: Iterable[CharacterSelectionListEntry]):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataDeleted.

            Args:
                characters (Iterable[CharacterSelectionListEntry]): (Length must be 252 or less.)
            """
            self._characters = tuple(characters)
            self._characters_count = len(self._characters)

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def characters(self) -> tuple[CharacterSelectionListEntry, ...]:
            return self._characters

        @staticmethod
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataDeleted") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataDeleted` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataDeleted): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._characters_count is None:
                    raise SerializationError("characters_count must be provided.")
                writer.add_char(data._characters_count)
                writer.add_byte(0xFF)
                if data._characters is None:
                    raise SerializationError("characters must be provided.")
                if len(data._characters) > 252:
                    raise SerializationError(f"Expected length of characters to be 252 or less, got {len(data._characters)}.")
                for i in range(data._characters_count):
                    CharacterSelectionListEntry.serialize(writer, data._characters[i])
                    writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataDeleted":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataDeleted` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataDeleted: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                characters_count = reader.get_char()
                reader.next_chunk()
                characters = []
                for i in range(characters_count):
                    characters.append(CharacterSelectionListEntry.deserialize(reader))
                    reader.next_chunk()
                result = CharacterReplyServerPacket.ReplyCodeDataDeleted(characters=characters)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataDeleted(byte_size={repr(self._byte_size)}, characters={repr(self._characters)})"

    class ReplyCodeDataDefault:
        """
        Default data associated with reply_code

        In this case (reply_code &gt; 9), reply_code is a session ID for character creation
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of CharacterReplyServerPacket.ReplyCodeDataDefault.
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
        def serialize(writer: EoWriter, data: "CharacterReplyServerPacket.ReplyCodeDataDefault") -> None:
            """
            Serializes an instance of `CharacterReplyServerPacket.ReplyCodeDataDefault` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (CharacterReplyServerPacket.ReplyCodeDataDefault): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("OK")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "CharacterReplyServerPacket.ReplyCodeDataDefault":
            """
            Deserializes an instance of `CharacterReplyServerPacket.ReplyCodeDataDefault` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                CharacterReplyServerPacket.ReplyCodeDataDefault: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = CharacterReplyServerPacket.ReplyCodeDataDefault()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"CharacterReplyServerPacket.ReplyCodeDataDefault(byte_size={repr(self._byte_size)})"
