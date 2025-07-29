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

class PriestRequestClientPacket(Packet):
    """
    Requesting marriage at a priest
    """
    _byte_size: int = 0
    _session_id: int
    _name: str

    def __init__(self, *, session_id: int, name: str):
        """
        Create a new instance of PriestRequestClientPacket.

        Args:
            session_id (int): (Value range is 0-4097152080.)
            name (str): 
        """
        self._session_id = session_id
        self._name = name

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
    def name(self) -> str:
        return self._name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Priest

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
        PriestRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PriestRequestClientPacket") -> None:
        """
        Serializes an instance of `PriestRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PriestRequestClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_int(data._session_id)
            writer.add_byte(0xFF)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PriestRequestClientPacket":
        """
        Deserializes an instance of `PriestRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PriestRequestClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            session_id = reader.get_int()
            reader.next_chunk()
            name = reader.get_string()
            reader.chunked_reading_mode = False
            result = PriestRequestClientPacket(session_id=session_id, name=name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PriestRequestClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, name={repr(self._name)})"
