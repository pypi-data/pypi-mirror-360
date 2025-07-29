# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from collections.abc import Iterable
from .guild_info_type import GuildInfoType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildAgreeClientPacket(Packet):
    """
    Update the guild description or rank list
    """
    _byte_size: int = 0
    _session_id: int
    _info_type: GuildInfoType
    _info_type_data: 'GuildAgreeClientPacket.InfoTypeData'

    def __init__(self, *, session_id: int, info_type: GuildInfoType, info_type_data: 'GuildAgreeClientPacket.InfoTypeData' = None):
        """
        Create a new instance of GuildAgreeClientPacket.

        Args:
            session_id (int): (Value range is 0-4097152080.)
            info_type (GuildInfoType): 
            info_type_data (GuildAgreeClientPacket.InfoTypeData): Data associated with the `info_type` field.
        """
        self._session_id = session_id
        self._info_type = info_type
        self._info_type_data = info_type_data

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
    def info_type(self) -> GuildInfoType:
        return self._info_type

    @property
    def info_type_data(self) -> 'GuildAgreeClientPacket.InfoTypeData':
        """
        GuildAgreeClientPacket.InfoTypeData: Data associated with the `info_type` field.
        """
        return self._info_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

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
        GuildAgreeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildAgreeClientPacket") -> None:
        """
        Serializes an instance of `GuildAgreeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildAgreeClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_int(data._session_id)
            if data._info_type is None:
                raise SerializationError("info_type must be provided.")
            writer.add_short(int(data._info_type))
            if data._info_type == GuildInfoType.Description:
                if not isinstance(data._info_type_data, GuildAgreeClientPacket.InfoTypeDataDescription):
                    raise SerializationError("Expected info_type_data to be type GuildAgreeClientPacket.InfoTypeDataDescription for info_type " + GuildInfoType(data._info_type).name + ".")
                GuildAgreeClientPacket.InfoTypeDataDescription.serialize(writer, data._info_type_data)
            elif data._info_type == GuildInfoType.Ranks:
                if not isinstance(data._info_type_data, GuildAgreeClientPacket.InfoTypeDataRanks):
                    raise SerializationError("Expected info_type_data to be type GuildAgreeClientPacket.InfoTypeDataRanks for info_type " + GuildInfoType(data._info_type).name + ".")
                GuildAgreeClientPacket.InfoTypeDataRanks.serialize(writer, data._info_type_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildAgreeClientPacket":
        """
        Deserializes an instance of `GuildAgreeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildAgreeClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            session_id = reader.get_int()
            info_type = GuildInfoType(reader.get_short())
            info_type_data: GuildAgreeClientPacket.InfoTypeData = None
            if info_type == GuildInfoType.Description:
                info_type_data = GuildAgreeClientPacket.InfoTypeDataDescription.deserialize(reader)
            elif info_type == GuildInfoType.Ranks:
                info_type_data = GuildAgreeClientPacket.InfoTypeDataRanks.deserialize(reader)
            reader.chunked_reading_mode = False
            result = GuildAgreeClientPacket(session_id=session_id, info_type=info_type, info_type_data=info_type_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildAgreeClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, info_type={repr(self._info_type)}, info_type_data={repr(self._info_type_data)})"

    InfoTypeData = Union['GuildAgreeClientPacket.InfoTypeDataDescription', 'GuildAgreeClientPacket.InfoTypeDataRanks', None]
    """
    Data associated with different values of the `info_type` field.
    """

    class InfoTypeDataDescription:
        """
        Data associated with info_type value GuildInfoType.Description
        """
        _byte_size: int = 0
        _description: str

        def __init__(self, *, description: str):
            """
            Create a new instance of GuildAgreeClientPacket.InfoTypeDataDescription.

            Args:
                description (str): 
            """
            self._description = description

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def description(self) -> str:
            return self._description

        @staticmethod
        def serialize(writer: EoWriter, data: "GuildAgreeClientPacket.InfoTypeDataDescription") -> None:
            """
            Serializes an instance of `GuildAgreeClientPacket.InfoTypeDataDescription` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (GuildAgreeClientPacket.InfoTypeDataDescription): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._description is None:
                    raise SerializationError("description must be provided.")
                writer.add_string(data._description)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "GuildAgreeClientPacket.InfoTypeDataDescription":
            """
            Deserializes an instance of `GuildAgreeClientPacket.InfoTypeDataDescription` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                GuildAgreeClientPacket.InfoTypeDataDescription: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                description = reader.get_string()
                result = GuildAgreeClientPacket.InfoTypeDataDescription(description=description)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"GuildAgreeClientPacket.InfoTypeDataDescription(byte_size={repr(self._byte_size)}, description={repr(self._description)})"

    class InfoTypeDataRanks:
        """
        Data associated with info_type value GuildInfoType.Ranks
        """
        _byte_size: int = 0
        _ranks: tuple[str, ...]

        def __init__(self, *, ranks: Iterable[str]):
            """
            Create a new instance of GuildAgreeClientPacket.InfoTypeDataRanks.

            Args:
                ranks (Iterable[str]): (Length must be `9`.)
            """
            self._ranks = tuple(ranks)

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def ranks(self) -> tuple[str, ...]:
            return self._ranks

        @staticmethod
        def serialize(writer: EoWriter, data: "GuildAgreeClientPacket.InfoTypeDataRanks") -> None:
            """
            Serializes an instance of `GuildAgreeClientPacket.InfoTypeDataRanks` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (GuildAgreeClientPacket.InfoTypeDataRanks): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._ranks is None:
                    raise SerializationError("ranks must be provided.")
                if len(data._ranks) != 9:
                    raise SerializationError(f"Expected length of ranks to be exactly 9, got {len(data._ranks)}.")
                for i in range(9):
                    writer.add_string(data._ranks[i])
                    writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "GuildAgreeClientPacket.InfoTypeDataRanks":
            """
            Deserializes an instance of `GuildAgreeClientPacket.InfoTypeDataRanks` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                GuildAgreeClientPacket.InfoTypeDataRanks: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                ranks = []
                for i in range(9):
                    ranks.append(reader.get_string())
                    reader.next_chunk()
                result = GuildAgreeClientPacket.InfoTypeDataRanks(ranks=ranks)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"GuildAgreeClientPacket.InfoTypeDataRanks(byte_size={repr(self._byte_size)}, ranks={repr(self._ranks)})"
