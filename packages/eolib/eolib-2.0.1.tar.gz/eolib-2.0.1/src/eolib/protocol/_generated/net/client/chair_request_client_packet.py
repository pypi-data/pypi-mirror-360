# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .sit_action import SitAction
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChairRequestClientPacket(Packet):
    """
    Sitting on a chair
    """
    _byte_size: int = 0
    _sit_action: SitAction
    _sit_action_data: 'ChairRequestClientPacket.SitActionData'

    def __init__(self, *, sit_action: SitAction, sit_action_data: 'ChairRequestClientPacket.SitActionData' = None):
        """
        Create a new instance of ChairRequestClientPacket.

        Args:
            sit_action (SitAction): 
            sit_action_data (ChairRequestClientPacket.SitActionData): Data associated with the `sit_action` field.
        """
        self._sit_action = sit_action
        self._sit_action_data = sit_action_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def sit_action(self) -> SitAction:
        return self._sit_action

    @property
    def sit_action_data(self) -> 'ChairRequestClientPacket.SitActionData':
        """
        ChairRequestClientPacket.SitActionData: Data associated with the `sit_action` field.
        """
        return self._sit_action_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Chair

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
        ChairRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChairRequestClientPacket") -> None:
        """
        Serializes an instance of `ChairRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChairRequestClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._sit_action is None:
                raise SerializationError("sit_action must be provided.")
            writer.add_char(int(data._sit_action))
            if data._sit_action == SitAction.Sit:
                if not isinstance(data._sit_action_data, ChairRequestClientPacket.SitActionDataSit):
                    raise SerializationError("Expected sit_action_data to be type ChairRequestClientPacket.SitActionDataSit for sit_action " + SitAction(data._sit_action).name + ".")
                ChairRequestClientPacket.SitActionDataSit.serialize(writer, data._sit_action_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ChairRequestClientPacket":
        """
        Deserializes an instance of `ChairRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChairRequestClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            sit_action = SitAction(reader.get_char())
            sit_action_data: ChairRequestClientPacket.SitActionData = None
            if sit_action == SitAction.Sit:
                sit_action_data = ChairRequestClientPacket.SitActionDataSit.deserialize(reader)
            result = ChairRequestClientPacket(sit_action=sit_action, sit_action_data=sit_action_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChairRequestClientPacket(byte_size={repr(self._byte_size)}, sit_action={repr(self._sit_action)}, sit_action_data={repr(self._sit_action_data)})"

    SitActionData = Union['ChairRequestClientPacket.SitActionDataSit', None]
    """
    Data associated with different values of the `sit_action` field.
    """

    class SitActionDataSit:
        """
        Data associated with sit_action value SitAction.Sit
        """
        _byte_size: int = 0
        _coords: Coords

        def __init__(self, *, coords: Coords):
            """
            Create a new instance of ChairRequestClientPacket.SitActionDataSit.

            Args:
                coords (Coords): 
            """
            self._coords = coords

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def coords(self) -> Coords:
            return self._coords

        @staticmethod
        def serialize(writer: EoWriter, data: "ChairRequestClientPacket.SitActionDataSit") -> None:
            """
            Serializes an instance of `ChairRequestClientPacket.SitActionDataSit` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (ChairRequestClientPacket.SitActionDataSit): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._coords is None:
                    raise SerializationError("coords must be provided.")
                Coords.serialize(writer, data._coords)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "ChairRequestClientPacket.SitActionDataSit":
            """
            Deserializes an instance of `ChairRequestClientPacket.SitActionDataSit` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                ChairRequestClientPacket.SitActionDataSit: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                coords = Coords.deserialize(reader)
                result = ChairRequestClientPacket.SitActionDataSit(coords=coords)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"ChairRequestClientPacket.SitActionDataSit(byte_size={repr(self._byte_size)}, coords={repr(self._coords)})"
