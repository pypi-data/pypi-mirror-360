# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .warp_type import WarpType
from .warp_effect import WarpEffect
from .nearby_info import NearbyInfo
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WarpAgreeServerPacket(Packet):
    """
    Reply after accepting a warp
    """
    _byte_size: int = 0
    _warp_type: WarpType
    _warp_type_data: 'WarpAgreeServerPacket.WarpTypeData'
    _nearby: NearbyInfo

    def __init__(self, *, warp_type: WarpType, warp_type_data: 'WarpAgreeServerPacket.WarpTypeData' = None, nearby: NearbyInfo):
        """
        Create a new instance of WarpAgreeServerPacket.

        Args:
            warp_type (WarpType): 
            warp_type_data (WarpAgreeServerPacket.WarpTypeData): Data associated with the `warp_type` field.
            nearby (NearbyInfo): 
        """
        self._warp_type = warp_type
        self._warp_type_data = warp_type_data
        self._nearby = nearby

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
    def warp_type_data(self) -> 'WarpAgreeServerPacket.WarpTypeData':
        """
        WarpAgreeServerPacket.WarpTypeData: Data associated with the `warp_type` field.
        """
        return self._warp_type_data

    @property
    def nearby(self) -> NearbyInfo:
        return self._nearby

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
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WarpAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WarpAgreeServerPacket") -> None:
        """
        Serializes an instance of `WarpAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WarpAgreeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._warp_type is None:
                raise SerializationError("warp_type must be provided.")
            writer.add_char(int(data._warp_type))
            if data._warp_type == WarpType.MapSwitch:
                if not isinstance(data._warp_type_data, WarpAgreeServerPacket.WarpTypeDataMapSwitch):
                    raise SerializationError("Expected warp_type_data to be type WarpAgreeServerPacket.WarpTypeDataMapSwitch for warp_type " + WarpType(data._warp_type).name + ".")
                WarpAgreeServerPacket.WarpTypeDataMapSwitch.serialize(writer, data._warp_type_data)
            if data._nearby is None:
                raise SerializationError("nearby must be provided.")
            NearbyInfo.serialize(writer, data._nearby)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WarpAgreeServerPacket":
        """
        Deserializes an instance of `WarpAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WarpAgreeServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            warp_type = WarpType(reader.get_char())
            warp_type_data: WarpAgreeServerPacket.WarpTypeData = None
            if warp_type == WarpType.MapSwitch:
                warp_type_data = WarpAgreeServerPacket.WarpTypeDataMapSwitch.deserialize(reader)
            nearby = NearbyInfo.deserialize(reader)
            reader.chunked_reading_mode = False
            result = WarpAgreeServerPacket(warp_type=warp_type, warp_type_data=warp_type_data, nearby=nearby)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WarpAgreeServerPacket(byte_size={repr(self._byte_size)}, warp_type={repr(self._warp_type)}, warp_type_data={repr(self._warp_type_data)}, nearby={repr(self._nearby)})"

    WarpTypeData = Union['WarpAgreeServerPacket.WarpTypeDataMapSwitch', None]
    """
    Data associated with different values of the `warp_type` field.
    """

    class WarpTypeDataMapSwitch:
        """
        Data associated with warp_type value WarpType.MapSwitch
        """
        _byte_size: int = 0
        _map_id: int
        _warp_effect: WarpEffect

        def __init__(self, *, map_id: int, warp_effect: WarpEffect):
            """
            Create a new instance of WarpAgreeServerPacket.WarpTypeDataMapSwitch.

            Args:
                map_id (int): (Value range is 0-64008.)
                warp_effect (WarpEffect): 
            """
            self._map_id = map_id
            self._warp_effect = warp_effect

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def map_id(self) -> int:
            return self._map_id

        @property
        def warp_effect(self) -> WarpEffect:
            return self._warp_effect

        @staticmethod
        def serialize(writer: EoWriter, data: "WarpAgreeServerPacket.WarpTypeDataMapSwitch") -> None:
            """
            Serializes an instance of `WarpAgreeServerPacket.WarpTypeDataMapSwitch` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WarpAgreeServerPacket.WarpTypeDataMapSwitch): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._map_id is None:
                    raise SerializationError("map_id must be provided.")
                writer.add_short(data._map_id)
                if data._warp_effect is None:
                    raise SerializationError("warp_effect must be provided.")
                writer.add_char(int(data._warp_effect))
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WarpAgreeServerPacket.WarpTypeDataMapSwitch":
            """
            Deserializes an instance of `WarpAgreeServerPacket.WarpTypeDataMapSwitch` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WarpAgreeServerPacket.WarpTypeDataMapSwitch: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                map_id = reader.get_short()
                warp_effect = WarpEffect(reader.get_char())
                result = WarpAgreeServerPacket.WarpTypeDataMapSwitch(map_id=map_id, warp_effect=warp_effect)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WarpAgreeServerPacket.WarpTypeDataMapSwitch(byte_size={repr(self._byte_size)}, map_id={repr(self._map_id)}, warp_effect={repr(self._warp_effect)})"
