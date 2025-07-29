# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...gender import Gender
from ...admin_level import AdminLevel
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterDetails:
    """
    Information displayed on the paperdoll and book
    """
    _byte_size: int = 0
    _name: str
    _home: str
    _partner: str
    _title: str
    _guild: str
    _guild_rank: str
    _player_id: int
    _class_id: int
    _gender: Gender
    _admin: AdminLevel

    def __init__(self, *, name: str, home: str, partner: str, title: str, guild: str, guild_rank: str, player_id: int, class_id: int, gender: Gender, admin: AdminLevel):
        """
        Create a new instance of CharacterDetails.

        Args:
            name (str): 
            home (str): 
            partner (str): 
            title (str): 
            guild (str): 
            guild_rank (str): 
            player_id (int): (Value range is 0-64008.)
            class_id (int): (Value range is 0-252.)
            gender (Gender): 
            admin (AdminLevel): 
        """
        self._name = name
        self._home = home
        self._partner = partner
        self._title = title
        self._guild = guild
        self._guild_rank = guild_rank
        self._player_id = player_id
        self._class_id = class_id
        self._gender = gender
        self._admin = admin

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @property
    def home(self) -> str:
        return self._home

    @property
    def partner(self) -> str:
        return self._partner

    @property
    def title(self) -> str:
        return self._title

    @property
    def guild(self) -> str:
        return self._guild

    @property
    def guild_rank(self) -> str:
        return self._guild_rank

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def class_id(self) -> int:
        return self._class_id

    @property
    def gender(self) -> Gender:
        return self._gender

    @property
    def admin(self) -> AdminLevel:
        return self._admin

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterDetails") -> None:
        """
        Serializes an instance of `CharacterDetails` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterDetails): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._home is None:
                raise SerializationError("home must be provided.")
            writer.add_string(data._home)
            writer.add_byte(0xFF)
            if data._partner is None:
                raise SerializationError("partner must be provided.")
            writer.add_string(data._partner)
            writer.add_byte(0xFF)
            if data._title is None:
                raise SerializationError("title must be provided.")
            writer.add_string(data._title)
            writer.add_byte(0xFF)
            if data._guild is None:
                raise SerializationError("guild must be provided.")
            writer.add_string(data._guild)
            writer.add_byte(0xFF)
            if data._guild_rank is None:
                raise SerializationError("guild_rank must be provided.")
            writer.add_string(data._guild_rank)
            writer.add_byte(0xFF)
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._class_id is None:
                raise SerializationError("class_id must be provided.")
            writer.add_char(data._class_id)
            if data._gender is None:
                raise SerializationError("gender must be provided.")
            writer.add_char(int(data._gender))
            if data._admin is None:
                raise SerializationError("admin must be provided.")
            writer.add_char(int(data._admin))
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterDetails":
        """
        Deserializes an instance of `CharacterDetails` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterDetails: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            name = reader.get_string()
            reader.next_chunk()
            home = reader.get_string()
            reader.next_chunk()
            partner = reader.get_string()
            reader.next_chunk()
            title = reader.get_string()
            reader.next_chunk()
            guild = reader.get_string()
            reader.next_chunk()
            guild_rank = reader.get_string()
            reader.next_chunk()
            player_id = reader.get_short()
            class_id = reader.get_char()
            gender = Gender(reader.get_char())
            admin = AdminLevel(reader.get_char())
            reader.chunked_reading_mode = False
            result = CharacterDetails(name=name, home=home, partner=partner, title=title, guild=guild, guild_rank=guild_rank, player_id=player_id, class_id=class_id, gender=gender, admin=admin)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterDetails(byte_size={repr(self._byte_size)}, name={repr(self._name)}, home={repr(self._home)}, partner={repr(self._partner)}, title={repr(self._title)}, guild={repr(self._guild)}, guild_rank={repr(self._guild_rank)}, player_id={repr(self._player_id)}, class_id={repr(self._class_id)}, gender={repr(self._gender)}, admin={repr(self._admin)})"
