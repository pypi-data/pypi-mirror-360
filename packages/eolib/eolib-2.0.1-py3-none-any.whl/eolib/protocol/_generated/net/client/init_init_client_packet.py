# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..version import Version
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class InitInitClientPacket(Packet):
    """
    Connection initialization request.
    This packet is unencrypted.
    """
    _byte_size: int = 0
    _challenge: int
    _version: Version
    _hdid_length: int
    _hdid: str

    def __init__(self, *, challenge: int, version: Version, hdid: str):
        """
        Create a new instance of InitInitClientPacket.

        Args:
            challenge (int): (Value range is 0-16194276.)
            version (Version): 
            hdid (str): (Length must be 252 or less.)
        """
        self._challenge = challenge
        self._version = version
        self._hdid = hdid
        self._hdid_length = len(self._hdid)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def challenge(self) -> int:
        return self._challenge

    @property
    def version(self) -> Version:
        return self._version

    @property
    def hdid(self) -> str:
        return self._hdid

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Init

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Init

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        InitInitClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "InitInitClientPacket") -> None:
        """
        Serializes an instance of `InitInitClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (InitInitClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._challenge is None:
                raise SerializationError("challenge must be provided.")
            writer.add_three(data._challenge)
            if data._version is None:
                raise SerializationError("version must be provided.")
            Version.serialize(writer, data._version)
            writer.add_char(112)
            if data._hdid_length is None:
                raise SerializationError("hdid_length must be provided.")
            writer.add_char(data._hdid_length)
            if data._hdid is None:
                raise SerializationError("hdid must be provided.")
            if len(data._hdid) > 252:
                raise SerializationError(f"Expected length of hdid to be 252 or less, got {len(data._hdid)}.")
            writer.add_fixed_string(data._hdid, data._hdid_length, False)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "InitInitClientPacket":
        """
        Deserializes an instance of `InitInitClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            InitInitClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            challenge = reader.get_three()
            version = Version.deserialize(reader)
            reader.get_char()
            hdid_length = reader.get_char()
            hdid = reader.get_fixed_string(hdid_length, False)
            result = InitInitClientPacket(challenge=challenge, version=version, hdid=hdid)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"InitInitClientPacket(byte_size={repr(self._byte_size)}, challenge={repr(self._challenge)}, version={repr(self._version)}, hdid={repr(self._hdid)})"
