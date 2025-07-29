# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class BarberBuyClientPacket(Packet):
    """
    Purchasing a hair-style
    """
    _byte_size: int = 0
    _hair_style: int
    _hair_color: int
    _session_id: int

    def __init__(self, *, hair_style: int, hair_color: int, session_id: int):
        """
        Create a new instance of BarberBuyClientPacket.

        Args:
            hair_style (int): (Value range is 0-252.)
            hair_color (int): (Value range is 0-252.)
            session_id (int): (Value range is 0-4097152080.)
        """
        self._hair_style = hair_style
        self._hair_color = hair_color
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
    def hair_style(self) -> int:
        return self._hair_style

    @property
    def hair_color(self) -> int:
        return self._hair_color

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
        return PacketFamily.Barber

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Buy

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BarberBuyClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BarberBuyClientPacket") -> None:
        """
        Serializes an instance of `BarberBuyClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BarberBuyClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._hair_style is None:
                raise SerializationError("hair_style must be provided.")
            writer.add_char(data._hair_style)
            if data._hair_color is None:
                raise SerializationError("hair_color must be provided.")
            writer.add_char(data._hair_color)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_int(data._session_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BarberBuyClientPacket":
        """
        Deserializes an instance of `BarberBuyClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BarberBuyClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            hair_style = reader.get_char()
            hair_color = reader.get_char()
            session_id = reader.get_int()
            result = BarberBuyClientPacket(hair_style=hair_style, hair_color=hair_color, session_id=session_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BarberBuyClientPacket(byte_size={repr(self._byte_size)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, session_id={repr(self._session_id)})"
