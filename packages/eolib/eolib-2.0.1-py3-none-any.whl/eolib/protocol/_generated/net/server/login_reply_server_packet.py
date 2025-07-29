# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from collections.abc import Iterable
from .login_reply import LoginReply
from .character_selection_list_entry import CharacterSelectionListEntry
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class LoginReplyServerPacket(Packet):
    """
    Login reply
    """
    _byte_size: int = 0
    _reply_code: LoginReply
    _reply_code_data: 'LoginReplyServerPacket.ReplyCodeData'

    def __init__(self, *, reply_code: LoginReply, reply_code_data: 'LoginReplyServerPacket.ReplyCodeData' = None):
        """
        Create a new instance of LoginReplyServerPacket.

        Args:
            reply_code (LoginReply): 
            reply_code_data (LoginReplyServerPacket.ReplyCodeData): Data associated with the `reply_code` field.
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
    def reply_code(self) -> LoginReply:
        return self._reply_code

    @property
    def reply_code_data(self) -> 'LoginReplyServerPacket.ReplyCodeData':
        """
        LoginReplyServerPacket.ReplyCodeData: Data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Login

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
        LoginReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LoginReplyServerPacket") -> None:
        """
        Serializes an instance of `LoginReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LoginReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._reply_code is None:
                raise SerializationError("reply_code must be provided.")
            writer.add_short(int(data._reply_code))
            if data._reply_code == LoginReply.WrongUser:
                if not isinstance(data._reply_code_data, LoginReplyServerPacket.ReplyCodeDataWrongUser):
                    raise SerializationError("Expected reply_code_data to be type LoginReplyServerPacket.ReplyCodeDataWrongUser for reply_code " + LoginReply(data._reply_code).name + ".")
                LoginReplyServerPacket.ReplyCodeDataWrongUser.serialize(writer, data._reply_code_data)
            elif data._reply_code == LoginReply.WrongUserPassword:
                if not isinstance(data._reply_code_data, LoginReplyServerPacket.ReplyCodeDataWrongUserPassword):
                    raise SerializationError("Expected reply_code_data to be type LoginReplyServerPacket.ReplyCodeDataWrongUserPassword for reply_code " + LoginReply(data._reply_code).name + ".")
                LoginReplyServerPacket.ReplyCodeDataWrongUserPassword.serialize(writer, data._reply_code_data)
            elif data._reply_code == LoginReply.Ok:
                if not isinstance(data._reply_code_data, LoginReplyServerPacket.ReplyCodeDataOk):
                    raise SerializationError("Expected reply_code_data to be type LoginReplyServerPacket.ReplyCodeDataOk for reply_code " + LoginReply(data._reply_code).name + ".")
                LoginReplyServerPacket.ReplyCodeDataOk.serialize(writer, data._reply_code_data)
            elif data._reply_code == LoginReply.Banned:
                if not isinstance(data._reply_code_data, LoginReplyServerPacket.ReplyCodeDataBanned):
                    raise SerializationError("Expected reply_code_data to be type LoginReplyServerPacket.ReplyCodeDataBanned for reply_code " + LoginReply(data._reply_code).name + ".")
                LoginReplyServerPacket.ReplyCodeDataBanned.serialize(writer, data._reply_code_data)
            elif data._reply_code == LoginReply.LoggedIn:
                if not isinstance(data._reply_code_data, LoginReplyServerPacket.ReplyCodeDataLoggedIn):
                    raise SerializationError("Expected reply_code_data to be type LoginReplyServerPacket.ReplyCodeDataLoggedIn for reply_code " + LoginReply(data._reply_code).name + ".")
                LoginReplyServerPacket.ReplyCodeDataLoggedIn.serialize(writer, data._reply_code_data)
            elif data._reply_code == LoginReply.Busy:
                if not isinstance(data._reply_code_data, LoginReplyServerPacket.ReplyCodeDataBusy):
                    raise SerializationError("Expected reply_code_data to be type LoginReplyServerPacket.ReplyCodeDataBusy for reply_code " + LoginReply(data._reply_code).name + ".")
                LoginReplyServerPacket.ReplyCodeDataBusy.serialize(writer, data._reply_code_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "LoginReplyServerPacket":
        """
        Deserializes an instance of `LoginReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LoginReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            reply_code = LoginReply(reader.get_short())
            reply_code_data: LoginReplyServerPacket.ReplyCodeData = None
            if reply_code == LoginReply.WrongUser:
                reply_code_data = LoginReplyServerPacket.ReplyCodeDataWrongUser.deserialize(reader)
            elif reply_code == LoginReply.WrongUserPassword:
                reply_code_data = LoginReplyServerPacket.ReplyCodeDataWrongUserPassword.deserialize(reader)
            elif reply_code == LoginReply.Ok:
                reply_code_data = LoginReplyServerPacket.ReplyCodeDataOk.deserialize(reader)
            elif reply_code == LoginReply.Banned:
                reply_code_data = LoginReplyServerPacket.ReplyCodeDataBanned.deserialize(reader)
            elif reply_code == LoginReply.LoggedIn:
                reply_code_data = LoginReplyServerPacket.ReplyCodeDataLoggedIn.deserialize(reader)
            elif reply_code == LoginReply.Busy:
                reply_code_data = LoginReplyServerPacket.ReplyCodeDataBusy.deserialize(reader)
            reader.chunked_reading_mode = False
            result = LoginReplyServerPacket(reply_code=reply_code, reply_code_data=reply_code_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LoginReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['LoginReplyServerPacket.ReplyCodeDataWrongUser', 'LoginReplyServerPacket.ReplyCodeDataWrongUserPassword', 'LoginReplyServerPacket.ReplyCodeDataOk', 'LoginReplyServerPacket.ReplyCodeDataBanned', 'LoginReplyServerPacket.ReplyCodeDataLoggedIn', 'LoginReplyServerPacket.ReplyCodeDataBusy', None]
    """
    Data associated with different values of the `reply_code` field.
    """

    class ReplyCodeDataWrongUser:
        """
        Data associated with reply_code value LoginReply.WrongUser
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of LoginReplyServerPacket.ReplyCodeDataWrongUser.
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
        def serialize(writer: EoWriter, data: "LoginReplyServerPacket.ReplyCodeDataWrongUser") -> None:
            """
            Serializes an instance of `LoginReplyServerPacket.ReplyCodeDataWrongUser` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (LoginReplyServerPacket.ReplyCodeDataWrongUser): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "LoginReplyServerPacket.ReplyCodeDataWrongUser":
            """
            Deserializes an instance of `LoginReplyServerPacket.ReplyCodeDataWrongUser` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                LoginReplyServerPacket.ReplyCodeDataWrongUser: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = LoginReplyServerPacket.ReplyCodeDataWrongUser()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"LoginReplyServerPacket.ReplyCodeDataWrongUser(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataWrongUserPassword:
        """
        Data associated with reply_code value LoginReply.WrongUserPassword
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of LoginReplyServerPacket.ReplyCodeDataWrongUserPassword.
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
        def serialize(writer: EoWriter, data: "LoginReplyServerPacket.ReplyCodeDataWrongUserPassword") -> None:
            """
            Serializes an instance of `LoginReplyServerPacket.ReplyCodeDataWrongUserPassword` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (LoginReplyServerPacket.ReplyCodeDataWrongUserPassword): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "LoginReplyServerPacket.ReplyCodeDataWrongUserPassword":
            """
            Deserializes an instance of `LoginReplyServerPacket.ReplyCodeDataWrongUserPassword` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                LoginReplyServerPacket.ReplyCodeDataWrongUserPassword: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = LoginReplyServerPacket.ReplyCodeDataWrongUserPassword()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"LoginReplyServerPacket.ReplyCodeDataWrongUserPassword(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataOk:
        """
        Data associated with reply_code value LoginReply.Ok
        """
        _byte_size: int = 0
        _characters_count: int
        _characters: tuple[CharacterSelectionListEntry, ...]

        def __init__(self, *, characters: Iterable[CharacterSelectionListEntry]):
            """
            Create a new instance of LoginReplyServerPacket.ReplyCodeDataOk.

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
        def serialize(writer: EoWriter, data: "LoginReplyServerPacket.ReplyCodeDataOk") -> None:
            """
            Serializes an instance of `LoginReplyServerPacket.ReplyCodeDataOk` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (LoginReplyServerPacket.ReplyCodeDataOk): The data to serialize.
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
        def deserialize(reader: EoReader) -> "LoginReplyServerPacket.ReplyCodeDataOk":
            """
            Deserializes an instance of `LoginReplyServerPacket.ReplyCodeDataOk` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                LoginReplyServerPacket.ReplyCodeDataOk: The data to serialize.
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
                result = LoginReplyServerPacket.ReplyCodeDataOk(characters=characters)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"LoginReplyServerPacket.ReplyCodeDataOk(byte_size={repr(self._byte_size)}, characters={repr(self._characters)})"

    class ReplyCodeDataBanned:
        """
        Data associated with reply_code value LoginReply.Banned
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of LoginReplyServerPacket.ReplyCodeDataBanned.
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
        def serialize(writer: EoWriter, data: "LoginReplyServerPacket.ReplyCodeDataBanned") -> None:
            """
            Serializes an instance of `LoginReplyServerPacket.ReplyCodeDataBanned` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (LoginReplyServerPacket.ReplyCodeDataBanned): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "LoginReplyServerPacket.ReplyCodeDataBanned":
            """
            Deserializes an instance of `LoginReplyServerPacket.ReplyCodeDataBanned` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                LoginReplyServerPacket.ReplyCodeDataBanned: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = LoginReplyServerPacket.ReplyCodeDataBanned()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"LoginReplyServerPacket.ReplyCodeDataBanned(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataLoggedIn:
        """
        Data associated with reply_code value LoginReply.LoggedIn
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of LoginReplyServerPacket.ReplyCodeDataLoggedIn.
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
        def serialize(writer: EoWriter, data: "LoginReplyServerPacket.ReplyCodeDataLoggedIn") -> None:
            """
            Serializes an instance of `LoginReplyServerPacket.ReplyCodeDataLoggedIn` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (LoginReplyServerPacket.ReplyCodeDataLoggedIn): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "LoginReplyServerPacket.ReplyCodeDataLoggedIn":
            """
            Deserializes an instance of `LoginReplyServerPacket.ReplyCodeDataLoggedIn` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                LoginReplyServerPacket.ReplyCodeDataLoggedIn: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = LoginReplyServerPacket.ReplyCodeDataLoggedIn()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"LoginReplyServerPacket.ReplyCodeDataLoggedIn(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataBusy:
        """
        Data associated with reply_code value LoginReply.Busy
        """
        _byte_size: int = 0

        def __init__(self):
            """
            Create a new instance of LoginReplyServerPacket.ReplyCodeDataBusy.
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
        def serialize(writer: EoWriter, data: "LoginReplyServerPacket.ReplyCodeDataBusy") -> None:
            """
            Serializes an instance of `LoginReplyServerPacket.ReplyCodeDataBusy` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (LoginReplyServerPacket.ReplyCodeDataBusy): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_string("NO")
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "LoginReplyServerPacket.ReplyCodeDataBusy":
            """
            Deserializes an instance of `LoginReplyServerPacket.ReplyCodeDataBusy` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                LoginReplyServerPacket.ReplyCodeDataBusy: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                result = LoginReplyServerPacket.ReplyCodeDataBusy()
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"LoginReplyServerPacket.ReplyCodeDataBusy(byte_size={repr(self._byte_size)})"
