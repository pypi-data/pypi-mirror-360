# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from collections.abc import Iterable
from .warp_type import WarpType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WarpRequestServerPacket(Packet):
    """
    Warp request from server
    """
    _byte_size: int = 0
    _warp_type: WarpType
    _map_id: int
    _warp_type_data: 'WarpRequestServerPacket.WarpTypeData'
    _session_id: int

    def __init__(self, *, warp_type: WarpType, map_id: int, warp_type_data: 'WarpRequestServerPacket.WarpTypeData' = None, session_id: int):
        """
        Create a new instance of WarpRequestServerPacket.

        Args:
            warp_type (WarpType): 
            map_id (int): (Value range is 0-64008.)
            warp_type_data (WarpRequestServerPacket.WarpTypeData): Data associated with the `warp_type` field.
            session_id (int): (Value range is 0-64008.)
        """
        self._warp_type = warp_type
        self._map_id = map_id
        self._warp_type_data = warp_type_data
        self._session_id = session_id

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def warp_type(self) -> WarpType:
        return self._warp_type

    @property
    def map_id(self) -> int:
        return self._map_id

    @property
    def warp_type_data(self) -> 'WarpRequestServerPacket.WarpTypeData':
        """
        WarpRequestServerPacket.WarpTypeData: Data associated with the `warp_type` field.
        """
        return self._warp_type_data

    @property
    def session_id(self) -> int:
        return self._session_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Warp

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WarpRequestServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WarpRequestServerPacket") -> None:
        """
        Serializes an instance of `WarpRequestServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WarpRequestServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._warp_type is None:
                raise SerializationError("warp_type must be provided.")
            writer.add_char(int(data._warp_type))
            if data._map_id is None:
                raise SerializationError("map_id must be provided.")
            writer.add_short(data._map_id)
            if data._warp_type == WarpType.MapSwitch:
                if not isinstance(data._warp_type_data, WarpRequestServerPacket.WarpTypeDataMapSwitch):
                    raise SerializationError("Expected warp_type_data to be type WarpRequestServerPacket.WarpTypeDataMapSwitch for warp_type " + WarpType(data._warp_type).name + ".")
                WarpRequestServerPacket.WarpTypeDataMapSwitch.serialize(writer, data._warp_type_data)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WarpRequestServerPacket":
        """
        Deserializes an instance of `WarpRequestServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WarpRequestServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            warp_type = WarpType(reader.get_char())
            map_id = reader.get_short()
            warp_type_data: WarpRequestServerPacket.WarpTypeData = None
            if warp_type == WarpType.MapSwitch:
                warp_type_data = WarpRequestServerPacket.WarpTypeDataMapSwitch.deserialize(reader)
            session_id = reader.get_short()
            result = WarpRequestServerPacket(warp_type=warp_type, map_id=map_id, warp_type_data=warp_type_data, session_id=session_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WarpRequestServerPacket(byte_size={repr(self._byte_size)}, warp_type={repr(self._warp_type)}, map_id={repr(self._map_id)}, warp_type_data={repr(self._warp_type_data)}, session_id={repr(self._session_id)})"

    WarpTypeData = Union['WarpRequestServerPacket.WarpTypeDataMapSwitch', None]
    """
    Data associated with different values of the `warp_type` field.
    """

    class WarpTypeDataMapSwitch:
        """
        Data associated with warp_type value WarpType.MapSwitch
        """
        _byte_size: int = 0
        _map_rid: tuple[int, ...]
        _map_file_size: int

        def __init__(self, *, map_rid: Iterable[int], map_file_size: int):
            """
            Create a new instance of WarpRequestServerPacket.WarpTypeDataMapSwitch.

            Args:
                map_rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
                map_file_size (int): (Value range is 0-16194276.)
            """
            self._map_rid = tuple(map_rid)
            self._map_file_size = map_file_size

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def map_rid(self) -> tuple[int, ...]:
            return self._map_rid

        @property
        def map_file_size(self) -> int:
            return self._map_file_size

        @staticmethod
        def serialize(writer: EoWriter, data: "WarpRequestServerPacket.WarpTypeDataMapSwitch") -> None:
            """
            Serializes an instance of `WarpRequestServerPacket.WarpTypeDataMapSwitch` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WarpRequestServerPacket.WarpTypeDataMapSwitch): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._map_rid is None:
                    raise SerializationError("map_rid must be provided.")
                if len(data._map_rid) != 2:
                    raise SerializationError(f"Expected length of map_rid to be exactly 2, got {len(data._map_rid)}.")
                for i in range(2):
                    writer.add_short(data._map_rid[i])
                if data._map_file_size is None:
                    raise SerializationError("map_file_size must be provided.")
                writer.add_three(data._map_file_size)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WarpRequestServerPacket.WarpTypeDataMapSwitch":
            """
            Deserializes an instance of `WarpRequestServerPacket.WarpTypeDataMapSwitch` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WarpRequestServerPacket.WarpTypeDataMapSwitch: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                map_rid = []
                for i in range(2):
                    map_rid.append(reader.get_short())
                map_file_size = reader.get_three()
                result = WarpRequestServerPacket.WarpTypeDataMapSwitch(map_rid=map_rid, map_file_size=map_file_size)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WarpRequestServerPacket.WarpTypeDataMapSwitch(byte_size={repr(self._byte_size)}, map_rid={repr(self._map_rid)}, map_file_size={repr(self._map_file_size)})"
