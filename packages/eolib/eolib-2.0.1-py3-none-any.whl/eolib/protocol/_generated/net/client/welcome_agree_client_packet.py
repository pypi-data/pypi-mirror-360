# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .file_type import FileType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WelcomeAgreeClientPacket(Packet):
    """
    Requesting a file
    """
    _byte_size: int = 0
    _file_type: FileType
    _session_id: int
    _file_type_data: 'WelcomeAgreeClientPacket.FileTypeData'

    def __init__(self, *, file_type: FileType, session_id: int, file_type_data: 'WelcomeAgreeClientPacket.FileTypeData' = None):
        """
        Create a new instance of WelcomeAgreeClientPacket.

        Args:
            file_type (FileType): 
            session_id (int): (Value range is 0-64008.)
            file_type_data (WelcomeAgreeClientPacket.FileTypeData): Data associated with the `file_type` field.
        """
        self._file_type = file_type
        self._session_id = session_id
        self._file_type_data = file_type_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def file_type(self) -> FileType:
        return self._file_type

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def file_type_data(self) -> 'WelcomeAgreeClientPacket.FileTypeData':
        """
        WelcomeAgreeClientPacket.FileTypeData: Data associated with the `file_type` field.
        """
        return self._file_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Welcome

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WelcomeAgreeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WelcomeAgreeClientPacket") -> None:
        """
        Serializes an instance of `WelcomeAgreeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WelcomeAgreeClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._file_type is None:
                raise SerializationError("file_type must be provided.")
            writer.add_char(int(data._file_type))
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._file_type == FileType.Emf:
                if not isinstance(data._file_type_data, WelcomeAgreeClientPacket.FileTypeDataEmf):
                    raise SerializationError("Expected file_type_data to be type WelcomeAgreeClientPacket.FileTypeDataEmf for file_type " + FileType(data._file_type).name + ".")
                WelcomeAgreeClientPacket.FileTypeDataEmf.serialize(writer, data._file_type_data)
            elif data._file_type == FileType.Eif:
                if not isinstance(data._file_type_data, WelcomeAgreeClientPacket.FileTypeDataEif):
                    raise SerializationError("Expected file_type_data to be type WelcomeAgreeClientPacket.FileTypeDataEif for file_type " + FileType(data._file_type).name + ".")
                WelcomeAgreeClientPacket.FileTypeDataEif.serialize(writer, data._file_type_data)
            elif data._file_type == FileType.Enf:
                if not isinstance(data._file_type_data, WelcomeAgreeClientPacket.FileTypeDataEnf):
                    raise SerializationError("Expected file_type_data to be type WelcomeAgreeClientPacket.FileTypeDataEnf for file_type " + FileType(data._file_type).name + ".")
                WelcomeAgreeClientPacket.FileTypeDataEnf.serialize(writer, data._file_type_data)
            elif data._file_type == FileType.Esf:
                if not isinstance(data._file_type_data, WelcomeAgreeClientPacket.FileTypeDataEsf):
                    raise SerializationError("Expected file_type_data to be type WelcomeAgreeClientPacket.FileTypeDataEsf for file_type " + FileType(data._file_type).name + ".")
                WelcomeAgreeClientPacket.FileTypeDataEsf.serialize(writer, data._file_type_data)
            elif data._file_type == FileType.Ecf:
                if not isinstance(data._file_type_data, WelcomeAgreeClientPacket.FileTypeDataEcf):
                    raise SerializationError("Expected file_type_data to be type WelcomeAgreeClientPacket.FileTypeDataEcf for file_type " + FileType(data._file_type).name + ".")
                WelcomeAgreeClientPacket.FileTypeDataEcf.serialize(writer, data._file_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WelcomeAgreeClientPacket":
        """
        Deserializes an instance of `WelcomeAgreeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WelcomeAgreeClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            file_type = FileType(reader.get_char())
            session_id = reader.get_short()
            file_type_data: WelcomeAgreeClientPacket.FileTypeData = None
            if file_type == FileType.Emf:
                file_type_data = WelcomeAgreeClientPacket.FileTypeDataEmf.deserialize(reader)
            elif file_type == FileType.Eif:
                file_type_data = WelcomeAgreeClientPacket.FileTypeDataEif.deserialize(reader)
            elif file_type == FileType.Enf:
                file_type_data = WelcomeAgreeClientPacket.FileTypeDataEnf.deserialize(reader)
            elif file_type == FileType.Esf:
                file_type_data = WelcomeAgreeClientPacket.FileTypeDataEsf.deserialize(reader)
            elif file_type == FileType.Ecf:
                file_type_data = WelcomeAgreeClientPacket.FileTypeDataEcf.deserialize(reader)
            result = WelcomeAgreeClientPacket(file_type=file_type, session_id=session_id, file_type_data=file_type_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WelcomeAgreeClientPacket(byte_size={repr(self._byte_size)}, file_type={repr(self._file_type)}, session_id={repr(self._session_id)}, file_type_data={repr(self._file_type_data)})"

    FileTypeData = Union['WelcomeAgreeClientPacket.FileTypeDataEmf', 'WelcomeAgreeClientPacket.FileTypeDataEif', 'WelcomeAgreeClientPacket.FileTypeDataEnf', 'WelcomeAgreeClientPacket.FileTypeDataEsf', 'WelcomeAgreeClientPacket.FileTypeDataEcf', None]
    """
    Data associated with different values of the `file_type` field.
    """

    class FileTypeDataEmf:
        """
        Data associated with file_type value FileType.Emf
        """
        _byte_size: int = 0
        _file_id: int

        def __init__(self, *, file_id: int):
            """
            Create a new instance of WelcomeAgreeClientPacket.FileTypeDataEmf.

            Args:
                file_id (int): (Value range is 0-64008.)
            """
            self._file_id = file_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def file_id(self) -> int:
            return self._file_id

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeAgreeClientPacket.FileTypeDataEmf") -> None:
            """
            Serializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEmf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeAgreeClientPacket.FileTypeDataEmf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._file_id is None:
                    raise SerializationError("file_id must be provided.")
                writer.add_short(data._file_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeAgreeClientPacket.FileTypeDataEmf":
            """
            Deserializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEmf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeAgreeClientPacket.FileTypeDataEmf: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                file_id = reader.get_short()
                result = WelcomeAgreeClientPacket.FileTypeDataEmf(file_id=file_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeAgreeClientPacket.FileTypeDataEmf(byte_size={repr(self._byte_size)}, file_id={repr(self._file_id)})"

    class FileTypeDataEif:
        """
        Data associated with file_type value FileType.Eif
        """
        _byte_size: int = 0
        _file_id: int

        def __init__(self, *, file_id: int):
            """
            Create a new instance of WelcomeAgreeClientPacket.FileTypeDataEif.

            Args:
                file_id (int): (Value range is 0-252.)
            """
            self._file_id = file_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def file_id(self) -> int:
            return self._file_id

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeAgreeClientPacket.FileTypeDataEif") -> None:
            """
            Serializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEif` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeAgreeClientPacket.FileTypeDataEif): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._file_id is None:
                    raise SerializationError("file_id must be provided.")
                writer.add_char(data._file_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeAgreeClientPacket.FileTypeDataEif":
            """
            Deserializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEif` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeAgreeClientPacket.FileTypeDataEif: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                file_id = reader.get_char()
                result = WelcomeAgreeClientPacket.FileTypeDataEif(file_id=file_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeAgreeClientPacket.FileTypeDataEif(byte_size={repr(self._byte_size)}, file_id={repr(self._file_id)})"

    class FileTypeDataEnf:
        """
        Data associated with file_type value FileType.Enf
        """
        _byte_size: int = 0
        _file_id: int

        def __init__(self, *, file_id: int):
            """
            Create a new instance of WelcomeAgreeClientPacket.FileTypeDataEnf.

            Args:
                file_id (int): (Value range is 0-252.)
            """
            self._file_id = file_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def file_id(self) -> int:
            return self._file_id

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeAgreeClientPacket.FileTypeDataEnf") -> None:
            """
            Serializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEnf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeAgreeClientPacket.FileTypeDataEnf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._file_id is None:
                    raise SerializationError("file_id must be provided.")
                writer.add_char(data._file_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeAgreeClientPacket.FileTypeDataEnf":
            """
            Deserializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEnf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeAgreeClientPacket.FileTypeDataEnf: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                file_id = reader.get_char()
                result = WelcomeAgreeClientPacket.FileTypeDataEnf(file_id=file_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeAgreeClientPacket.FileTypeDataEnf(byte_size={repr(self._byte_size)}, file_id={repr(self._file_id)})"

    class FileTypeDataEsf:
        """
        Data associated with file_type value FileType.Esf
        """
        _byte_size: int = 0
        _file_id: int

        def __init__(self, *, file_id: int):
            """
            Create a new instance of WelcomeAgreeClientPacket.FileTypeDataEsf.

            Args:
                file_id (int): (Value range is 0-252.)
            """
            self._file_id = file_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def file_id(self) -> int:
            return self._file_id

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeAgreeClientPacket.FileTypeDataEsf") -> None:
            """
            Serializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEsf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeAgreeClientPacket.FileTypeDataEsf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._file_id is None:
                    raise SerializationError("file_id must be provided.")
                writer.add_char(data._file_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeAgreeClientPacket.FileTypeDataEsf":
            """
            Deserializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEsf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeAgreeClientPacket.FileTypeDataEsf: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                file_id = reader.get_char()
                result = WelcomeAgreeClientPacket.FileTypeDataEsf(file_id=file_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeAgreeClientPacket.FileTypeDataEsf(byte_size={repr(self._byte_size)}, file_id={repr(self._file_id)})"

    class FileTypeDataEcf:
        """
        Data associated with file_type value FileType.Ecf
        """
        _byte_size: int = 0
        _file_id: int

        def __init__(self, *, file_id: int):
            """
            Create a new instance of WelcomeAgreeClientPacket.FileTypeDataEcf.

            Args:
                file_id (int): (Value range is 0-252.)
            """
            self._file_id = file_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def file_id(self) -> int:
            return self._file_id

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeAgreeClientPacket.FileTypeDataEcf") -> None:
            """
            Serializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEcf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeAgreeClientPacket.FileTypeDataEcf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._file_id is None:
                    raise SerializationError("file_id must be provided.")
                writer.add_char(data._file_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeAgreeClientPacket.FileTypeDataEcf":
            """
            Deserializes an instance of `WelcomeAgreeClientPacket.FileTypeDataEcf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeAgreeClientPacket.FileTypeDataEcf: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                file_id = reader.get_char()
                result = WelcomeAgreeClientPacket.FileTypeDataEcf(file_id=file_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeAgreeClientPacket.FileTypeDataEcf(byte_size={repr(self._byte_size)}, file_id={repr(self._file_id)})"
