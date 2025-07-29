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

class BankOpenServerPacket(Packet):
    """
    Open banker NPC interface
    """
    _byte_size: int = 0
    _gold_bank: int
    _session_id: int
    _locker_upgrades: int

    def __init__(self, *, gold_bank: int, session_id: int, locker_upgrades: int):
        """
        Create a new instance of BankOpenServerPacket.

        Args:
            gold_bank (int): (Value range is 0-4097152080.)
            session_id (int): (Value range is 0-16194276.)
            locker_upgrades (int): (Value range is 0-252.)
        """
        self._gold_bank = gold_bank
        self._session_id = session_id
        self._locker_upgrades = locker_upgrades

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def gold_bank(self) -> int:
        return self._gold_bank

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def locker_upgrades(self) -> int:
        return self._locker_upgrades

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Bank

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BankOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BankOpenServerPacket") -> None:
        """
        Serializes an instance of `BankOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BankOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._gold_bank is None:
                raise SerializationError("gold_bank must be provided.")
            writer.add_int(data._gold_bank)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_three(data._session_id)
            if data._locker_upgrades is None:
                raise SerializationError("locker_upgrades must be provided.")
            writer.add_char(data._locker_upgrades)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BankOpenServerPacket":
        """
        Deserializes an instance of `BankOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BankOpenServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            gold_bank = reader.get_int()
            session_id = reader.get_three()
            locker_upgrades = reader.get_char()
            result = BankOpenServerPacket(gold_bank=gold_bank, session_id=session_id, locker_upgrades=locker_upgrades)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BankOpenServerPacket(byte_size={repr(self._byte_size)}, gold_bank={repr(self._gold_bank)}, session_id={repr(self._session_id)}, locker_upgrades={repr(self._locker_upgrades)})"
