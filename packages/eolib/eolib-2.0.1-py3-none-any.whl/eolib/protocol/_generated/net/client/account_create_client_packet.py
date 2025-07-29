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

class AccountCreateClientPacket(Packet):
    """
    Confirm creating an account
    """
    _byte_size: int = 0
    _session_id: int
    _username: str
    _password: str
    _full_name: str
    _location: str
    _email: str
    _computer: str
    _hdid: str

    def __init__(self, *, session_id: int, username: str, password: str, full_name: str, location: str, email: str, computer: str, hdid: str):
        """
        Create a new instance of AccountCreateClientPacket.

        Args:
            session_id (int): (Value range is 0-64008.)
            username (str): 
            password (str): 
            full_name (str): 
            location (str): 
            email (str): 
            computer (str): 
            hdid (str): 
        """
        self._session_id = session_id
        self._username = username
        self._password = password
        self._full_name = full_name
        self._location = location
        self._email = email
        self._computer = computer
        self._hdid = hdid

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
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def location(self) -> str:
        return self._location

    @property
    def email(self) -> str:
        return self._email

    @property
    def computer(self) -> str:
        return self._computer

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
        return PacketFamily.Account

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AccountCreateClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AccountCreateClientPacket") -> None:
        """
        Serializes an instance of `AccountCreateClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AccountCreateClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            writer.add_byte(0xFF)
            if data._username is None:
                raise SerializationError("username must be provided.")
            writer.add_string(data._username)
            writer.add_byte(0xFF)
            if data._password is None:
                raise SerializationError("password must be provided.")
            writer.add_string(data._password)
            writer.add_byte(0xFF)
            if data._full_name is None:
                raise SerializationError("full_name must be provided.")
            writer.add_string(data._full_name)
            writer.add_byte(0xFF)
            if data._location is None:
                raise SerializationError("location must be provided.")
            writer.add_string(data._location)
            writer.add_byte(0xFF)
            if data._email is None:
                raise SerializationError("email must be provided.")
            writer.add_string(data._email)
            writer.add_byte(0xFF)
            if data._computer is None:
                raise SerializationError("computer must be provided.")
            writer.add_string(data._computer)
            writer.add_byte(0xFF)
            if data._hdid is None:
                raise SerializationError("hdid must be provided.")
            writer.add_string(data._hdid)
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AccountCreateClientPacket":
        """
        Deserializes an instance of `AccountCreateClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AccountCreateClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            session_id = reader.get_short()
            reader.next_chunk()
            username = reader.get_string()
            reader.next_chunk()
            password = reader.get_string()
            reader.next_chunk()
            full_name = reader.get_string()
            reader.next_chunk()
            location = reader.get_string()
            reader.next_chunk()
            email = reader.get_string()
            reader.next_chunk()
            computer = reader.get_string()
            reader.next_chunk()
            hdid = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            result = AccountCreateClientPacket(session_id=session_id, username=username, password=password, full_name=full_name, location=location, email=email, computer=computer, hdid=hdid)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AccountCreateClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, username={repr(self._username)}, password={repr(self._password)}, full_name={repr(self._full_name)}, location={repr(self._location)}, email={repr(self._email)}, computer={repr(self._computer)}, hdid={repr(self._hdid)})"
