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

class TradeRequestServerPacket(Packet):
    """
    Trade request from another player
    """
    _byte_size: int = 0
    _partner_player_id: int
    _partner_player_name: str

    def __init__(self, *, partner_player_id: int, partner_player_name: str):
        """
        Create a new instance of TradeRequestServerPacket.

        Args:
            partner_player_id (int): (Value range is 0-64008.)
            partner_player_name (str): 
        """
        self._partner_player_id = partner_player_id
        self._partner_player_name = partner_player_name

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def partner_player_id(self) -> int:
        return self._partner_player_id

    @property
    def partner_player_name(self) -> str:
        return self._partner_player_name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Trade

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
        TradeRequestServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeRequestServerPacket") -> None:
        """
        Serializes an instance of `TradeRequestServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeRequestServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_char(138)
            if data._partner_player_id is None:
                raise SerializationError("partner_player_id must be provided.")
            writer.add_short(data._partner_player_id)
            if data._partner_player_name is None:
                raise SerializationError("partner_player_name must be provided.")
            writer.add_string(data._partner_player_name)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeRequestServerPacket":
        """
        Deserializes an instance of `TradeRequestServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeRequestServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_char()
            partner_player_id = reader.get_short()
            partner_player_name = reader.get_string()
            result = TradeRequestServerPacket(partner_player_id=partner_player_id, partner_player_name=partner_player_name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeRequestServerPacket(byte_size={repr(self._byte_size)}, partner_player_id={repr(self._partner_player_id)}, partner_player_name={repr(self._partner_player_name)})"
