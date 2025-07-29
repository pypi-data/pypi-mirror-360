# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from collections.abc import Iterable
from .welcome_code import WelcomeCode
from .server_settings import ServerSettings
from .nearby_info import NearbyInfo
from .login_message_code import LoginMessageCode
from .equipment_welcome import EquipmentWelcome
from .character_stats_welcome import CharacterStatsWelcome
from ..weight import Weight
from ..spell import Spell
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ...admin_level import AdminLevel
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WelcomeReplyServerPacket(Packet):
    """
    Reply to selecting a character / entering game
    """
    _byte_size: int = 0
    _welcome_code: WelcomeCode
    _welcome_code_data: 'WelcomeReplyServerPacket.WelcomeCodeData'

    def __init__(self, *, welcome_code: WelcomeCode, welcome_code_data: 'WelcomeReplyServerPacket.WelcomeCodeData' = None):
        """
        Create a new instance of WelcomeReplyServerPacket.

        Args:
            welcome_code (WelcomeCode): 
            welcome_code_data (WelcomeReplyServerPacket.WelcomeCodeData): Data associated with the `welcome_code` field.
        """
        self._welcome_code = welcome_code
        self._welcome_code_data = welcome_code_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def welcome_code(self) -> WelcomeCode:
        return self._welcome_code

    @property
    def welcome_code_data(self) -> 'WelcomeReplyServerPacket.WelcomeCodeData':
        """
        WelcomeReplyServerPacket.WelcomeCodeData: Data associated with the `welcome_code` field.
        """
        return self._welcome_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Welcome

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WelcomeReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WelcomeReplyServerPacket") -> None:
        """
        Serializes an instance of `WelcomeReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WelcomeReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._welcome_code is None:
                raise SerializationError("welcome_code must be provided.")
            writer.add_short(int(data._welcome_code))
            writer.string_sanitization_mode = True
            if data._welcome_code == WelcomeCode.SelectCharacter:
                if not isinstance(data._welcome_code_data, WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter):
                    raise SerializationError("Expected welcome_code_data to be type WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter for welcome_code " + WelcomeCode(data._welcome_code).name + ".")
                WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter.serialize(writer, data._welcome_code_data)
            elif data._welcome_code == WelcomeCode.EnterGame:
                if not isinstance(data._welcome_code_data, WelcomeReplyServerPacket.WelcomeCodeDataEnterGame):
                    raise SerializationError("Expected welcome_code_data to be type WelcomeReplyServerPacket.WelcomeCodeDataEnterGame for welcome_code " + WelcomeCode(data._welcome_code).name + ".")
                WelcomeReplyServerPacket.WelcomeCodeDataEnterGame.serialize(writer, data._welcome_code_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WelcomeReplyServerPacket":
        """
        Deserializes an instance of `WelcomeReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WelcomeReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            welcome_code = WelcomeCode(reader.get_short())
            reader.chunked_reading_mode = True
            welcome_code_data: WelcomeReplyServerPacket.WelcomeCodeData = None
            if welcome_code == WelcomeCode.SelectCharacter:
                welcome_code_data = WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter.deserialize(reader)
            elif welcome_code == WelcomeCode.EnterGame:
                welcome_code_data = WelcomeReplyServerPacket.WelcomeCodeDataEnterGame.deserialize(reader)
            reader.chunked_reading_mode = False
            result = WelcomeReplyServerPacket(welcome_code=welcome_code, welcome_code_data=welcome_code_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WelcomeReplyServerPacket(byte_size={repr(self._byte_size)}, welcome_code={repr(self._welcome_code)}, welcome_code_data={repr(self._welcome_code_data)})"

    WelcomeCodeData = Union['WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter', 'WelcomeReplyServerPacket.WelcomeCodeDataEnterGame', None]
    """
    Data associated with different values of the `welcome_code` field.
    """

    class WelcomeCodeDataSelectCharacter:
        """
        Data associated with welcome_code value WelcomeCode.SelectCharacter
        """
        _byte_size: int = 0
        _session_id: int
        _character_id: int
        _map_id: int
        _map_rid: tuple[int, ...]
        _map_file_size: int
        _eif_rid: tuple[int, ...]
        _eif_length: int
        _enf_rid: tuple[int, ...]
        _enf_length: int
        _esf_rid: tuple[int, ...]
        _esf_length: int
        _ecf_rid: tuple[int, ...]
        _ecf_length: int
        _name: str
        _title: str
        _guild_name: str
        _guild_rank_name: str
        _class_id: int
        _guild_tag: str
        _admin: AdminLevel
        _level: int
        _experience: int
        _usage: int
        _stats: CharacterStatsWelcome
        _equipment: EquipmentWelcome
        _guild_rank: int
        _settings: ServerSettings
        _login_message_code: LoginMessageCode

        def __init__(self, *, session_id: int, character_id: int, map_id: int, map_rid: Iterable[int], map_file_size: int, eif_rid: Iterable[int], eif_length: int, enf_rid: Iterable[int], enf_length: int, esf_rid: Iterable[int], esf_length: int, ecf_rid: Iterable[int], ecf_length: int, name: str, title: str, guild_name: str, guild_rank_name: str, class_id: int, guild_tag: str, admin: AdminLevel, level: int, experience: int, usage: int, stats: CharacterStatsWelcome, equipment: EquipmentWelcome, guild_rank: int, settings: ServerSettings, login_message_code: LoginMessageCode):
            """
            Create a new instance of WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter.

            Args:
                session_id (int): (Value range is 0-64008.)
                character_id (int): (Value range is 0-4097152080.)
                map_id (int): (Value range is 0-64008.)
                map_rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
                map_file_size (int): (Value range is 0-16194276.)
                eif_rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
                eif_length (int): (Value range is 0-64008.)
                enf_rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
                enf_length (int): (Value range is 0-64008.)
                esf_rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
                esf_length (int): (Value range is 0-64008.)
                ecf_rid (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
                ecf_length (int): (Value range is 0-64008.)
                name (str): 
                title (str): 
                guild_name (str): 
                guild_rank_name (str): 
                class_id (int): (Value range is 0-252.)
                guild_tag (str): (Length must be `3`.)
                admin (AdminLevel): 
                level (int): (Value range is 0-252.)
                experience (int): (Value range is 0-4097152080.)
                usage (int): (Value range is 0-4097152080.)
                stats (CharacterStatsWelcome): 
                equipment (EquipmentWelcome): 
                guild_rank (int): (Value range is 0-252.)
                settings (ServerSettings): 
                login_message_code (LoginMessageCode): 
            """
            self._session_id = session_id
            self._character_id = character_id
            self._map_id = map_id
            self._map_rid = tuple(map_rid)
            self._map_file_size = map_file_size
            self._eif_rid = tuple(eif_rid)
            self._eif_length = eif_length
            self._enf_rid = tuple(enf_rid)
            self._enf_length = enf_length
            self._esf_rid = tuple(esf_rid)
            self._esf_length = esf_length
            self._ecf_rid = tuple(ecf_rid)
            self._ecf_length = ecf_length
            self._name = name
            self._title = title
            self._guild_name = guild_name
            self._guild_rank_name = guild_rank_name
            self._class_id = class_id
            self._guild_tag = guild_tag
            self._admin = admin
            self._level = level
            self._experience = experience
            self._usage = usage
            self._stats = stats
            self._equipment = equipment
            self._guild_rank = guild_rank
            self._settings = settings
            self._login_message_code = login_message_code

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
        def character_id(self) -> int:
            return self._character_id

        @property
        def map_id(self) -> int:
            return self._map_id

        @property
        def map_rid(self) -> tuple[int, ...]:
            return self._map_rid

        @property
        def map_file_size(self) -> int:
            return self._map_file_size

        @property
        def eif_rid(self) -> tuple[int, ...]:
            return self._eif_rid

        @property
        def eif_length(self) -> int:
            return self._eif_length

        @property
        def enf_rid(self) -> tuple[int, ...]:
            return self._enf_rid

        @property
        def enf_length(self) -> int:
            return self._enf_length

        @property
        def esf_rid(self) -> tuple[int, ...]:
            return self._esf_rid

        @property
        def esf_length(self) -> int:
            return self._esf_length

        @property
        def ecf_rid(self) -> tuple[int, ...]:
            return self._ecf_rid

        @property
        def ecf_length(self) -> int:
            return self._ecf_length

        @property
        def name(self) -> str:
            return self._name

        @property
        def title(self) -> str:
            return self._title

        @property
        def guild_name(self) -> str:
            return self._guild_name

        @property
        def guild_rank_name(self) -> str:
            return self._guild_rank_name

        @property
        def class_id(self) -> int:
            return self._class_id

        @property
        def guild_tag(self) -> str:
            return self._guild_tag

        @property
        def admin(self) -> AdminLevel:
            return self._admin

        @property
        def level(self) -> int:
            return self._level

        @property
        def experience(self) -> int:
            return self._experience

        @property
        def usage(self) -> int:
            return self._usage

        @property
        def stats(self) -> CharacterStatsWelcome:
            return self._stats

        @property
        def equipment(self) -> EquipmentWelcome:
            return self._equipment

        @property
        def guild_rank(self) -> int:
            return self._guild_rank

        @property
        def settings(self) -> ServerSettings:
            return self._settings

        @property
        def login_message_code(self) -> LoginMessageCode:
            return self._login_message_code

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter") -> None:
            """
            Serializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._session_id is None:
                    raise SerializationError("session_id must be provided.")
                writer.add_short(data._session_id)
                if data._character_id is None:
                    raise SerializationError("character_id must be provided.")
                writer.add_int(data._character_id)
                if data._map_id is None:
                    raise SerializationError("map_id must be provided.")
                writer.add_short(data._map_id)
                if data._map_rid is None:
                    raise SerializationError("map_rid must be provided.")
                if len(data._map_rid) != 2:
                    raise SerializationError(f"Expected length of map_rid to be exactly 2, got {len(data._map_rid)}.")
                for i in range(2):
                    writer.add_short(data._map_rid[i])
                if data._map_file_size is None:
                    raise SerializationError("map_file_size must be provided.")
                writer.add_three(data._map_file_size)
                if data._eif_rid is None:
                    raise SerializationError("eif_rid must be provided.")
                if len(data._eif_rid) != 2:
                    raise SerializationError(f"Expected length of eif_rid to be exactly 2, got {len(data._eif_rid)}.")
                for i in range(2):
                    writer.add_short(data._eif_rid[i])
                if data._eif_length is None:
                    raise SerializationError("eif_length must be provided.")
                writer.add_short(data._eif_length)
                if data._enf_rid is None:
                    raise SerializationError("enf_rid must be provided.")
                if len(data._enf_rid) != 2:
                    raise SerializationError(f"Expected length of enf_rid to be exactly 2, got {len(data._enf_rid)}.")
                for i in range(2):
                    writer.add_short(data._enf_rid[i])
                if data._enf_length is None:
                    raise SerializationError("enf_length must be provided.")
                writer.add_short(data._enf_length)
                if data._esf_rid is None:
                    raise SerializationError("esf_rid must be provided.")
                if len(data._esf_rid) != 2:
                    raise SerializationError(f"Expected length of esf_rid to be exactly 2, got {len(data._esf_rid)}.")
                for i in range(2):
                    writer.add_short(data._esf_rid[i])
                if data._esf_length is None:
                    raise SerializationError("esf_length must be provided.")
                writer.add_short(data._esf_length)
                if data._ecf_rid is None:
                    raise SerializationError("ecf_rid must be provided.")
                if len(data._ecf_rid) != 2:
                    raise SerializationError(f"Expected length of ecf_rid to be exactly 2, got {len(data._ecf_rid)}.")
                for i in range(2):
                    writer.add_short(data._ecf_rid[i])
                if data._ecf_length is None:
                    raise SerializationError("ecf_length must be provided.")
                writer.add_short(data._ecf_length)
                if data._name is None:
                    raise SerializationError("name must be provided.")
                writer.add_string(data._name)
                writer.add_byte(0xFF)
                if data._title is None:
                    raise SerializationError("title must be provided.")
                writer.add_string(data._title)
                writer.add_byte(0xFF)
                if data._guild_name is None:
                    raise SerializationError("guild_name must be provided.")
                writer.add_string(data._guild_name)
                writer.add_byte(0xFF)
                if data._guild_rank_name is None:
                    raise SerializationError("guild_rank_name must be provided.")
                writer.add_string(data._guild_rank_name)
                writer.add_byte(0xFF)
                if data._class_id is None:
                    raise SerializationError("class_id must be provided.")
                writer.add_char(data._class_id)
                if data._guild_tag is None:
                    raise SerializationError("guild_tag must be provided.")
                if len(data._guild_tag) != 3:
                    raise SerializationError(f"Expected length of guild_tag to be exactly 3, got {len(data._guild_tag)}.")
                writer.add_fixed_string(data._guild_tag, 3, False)
                if data._admin is None:
                    raise SerializationError("admin must be provided.")
                writer.add_char(int(data._admin))
                if data._level is None:
                    raise SerializationError("level must be provided.")
                writer.add_char(data._level)
                if data._experience is None:
                    raise SerializationError("experience must be provided.")
                writer.add_int(data._experience)
                if data._usage is None:
                    raise SerializationError("usage must be provided.")
                writer.add_int(data._usage)
                if data._stats is None:
                    raise SerializationError("stats must be provided.")
                CharacterStatsWelcome.serialize(writer, data._stats)
                if data._equipment is None:
                    raise SerializationError("equipment must be provided.")
                EquipmentWelcome.serialize(writer, data._equipment)
                if data._guild_rank is None:
                    raise SerializationError("guild_rank must be provided.")
                writer.add_char(data._guild_rank)
                if data._settings is None:
                    raise SerializationError("settings must be provided.")
                ServerSettings.serialize(writer, data._settings)
                if data._login_message_code is None:
                    raise SerializationError("login_message_code must be provided.")
                writer.add_char(int(data._login_message_code))
                writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter":
            """
            Deserializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                session_id = reader.get_short()
                character_id = reader.get_int()
                map_id = reader.get_short()
                map_rid = []
                for i in range(2):
                    map_rid.append(reader.get_short())
                map_file_size = reader.get_three()
                eif_rid = []
                for i in range(2):
                    eif_rid.append(reader.get_short())
                eif_length = reader.get_short()
                enf_rid = []
                for i in range(2):
                    enf_rid.append(reader.get_short())
                enf_length = reader.get_short()
                esf_rid = []
                for i in range(2):
                    esf_rid.append(reader.get_short())
                esf_length = reader.get_short()
                ecf_rid = []
                for i in range(2):
                    ecf_rid.append(reader.get_short())
                ecf_length = reader.get_short()
                name = reader.get_string()
                reader.next_chunk()
                title = reader.get_string()
                reader.next_chunk()
                guild_name = reader.get_string()
                reader.next_chunk()
                guild_rank_name = reader.get_string()
                reader.next_chunk()
                class_id = reader.get_char()
                guild_tag = reader.get_fixed_string(3, False)
                admin = AdminLevel(reader.get_char())
                level = reader.get_char()
                experience = reader.get_int()
                usage = reader.get_int()
                stats = CharacterStatsWelcome.deserialize(reader)
                equipment = EquipmentWelcome.deserialize(reader)
                guild_rank = reader.get_char()
                settings = ServerSettings.deserialize(reader)
                login_message_code = LoginMessageCode(reader.get_char())
                reader.next_chunk()
                result = WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter(session_id=session_id, character_id=character_id, map_id=map_id, map_rid=map_rid, map_file_size=map_file_size, eif_rid=eif_rid, eif_length=eif_length, enf_rid=enf_rid, enf_length=enf_length, esf_rid=esf_rid, esf_length=esf_length, ecf_rid=ecf_rid, ecf_length=ecf_length, name=name, title=title, guild_name=guild_name, guild_rank_name=guild_rank_name, class_id=class_id, guild_tag=guild_tag, admin=admin, level=level, experience=experience, usage=usage, stats=stats, equipment=equipment, guild_rank=guild_rank, settings=settings, login_message_code=login_message_code)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, character_id={repr(self._character_id)}, map_id={repr(self._map_id)}, map_rid={repr(self._map_rid)}, map_file_size={repr(self._map_file_size)}, eif_rid={repr(self._eif_rid)}, eif_length={repr(self._eif_length)}, enf_rid={repr(self._enf_rid)}, enf_length={repr(self._enf_length)}, esf_rid={repr(self._esf_rid)}, esf_length={repr(self._esf_length)}, ecf_rid={repr(self._ecf_rid)}, ecf_length={repr(self._ecf_length)}, name={repr(self._name)}, title={repr(self._title)}, guild_name={repr(self._guild_name)}, guild_rank_name={repr(self._guild_rank_name)}, class_id={repr(self._class_id)}, guild_tag={repr(self._guild_tag)}, admin={repr(self._admin)}, level={repr(self._level)}, experience={repr(self._experience)}, usage={repr(self._usage)}, stats={repr(self._stats)}, equipment={repr(self._equipment)}, guild_rank={repr(self._guild_rank)}, settings={repr(self._settings)}, login_message_code={repr(self._login_message_code)})"

    class WelcomeCodeDataEnterGame:
        """
        Data associated with welcome_code value WelcomeCode.EnterGame
        """
        _byte_size: int = 0
        _news: tuple[str, ...]
        _weight: Weight
        _items: tuple[Item, ...]
        _spells: tuple[Spell, ...]
        _nearby: NearbyInfo

        def __init__(self, *, news: Iterable[str], weight: Weight, items: Iterable[Item], spells: Iterable[Spell], nearby: NearbyInfo):
            """
            Create a new instance of WelcomeReplyServerPacket.WelcomeCodeDataEnterGame.

            Args:
                news (Iterable[str]): (Length must be `9`.)
                weight (Weight): 
                items (Iterable[Item]): 
                spells (Iterable[Spell]): 
                nearby (NearbyInfo): 
            """
            self._news = tuple(news)
            self._weight = weight
            self._items = tuple(items)
            self._spells = tuple(spells)
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
        def news(self) -> tuple[str, ...]:
            return self._news

        @property
        def weight(self) -> Weight:
            return self._weight

        @property
        def items(self) -> tuple[Item, ...]:
            return self._items

        @property
        def spells(self) -> tuple[Spell, ...]:
            return self._spells

        @property
        def nearby(self) -> NearbyInfo:
            return self._nearby

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeReplyServerPacket.WelcomeCodeDataEnterGame") -> None:
            """
            Serializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataEnterGame` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeReplyServerPacket.WelcomeCodeDataEnterGame): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_byte(0xFF)
                if data._news is None:
                    raise SerializationError("news must be provided.")
                if len(data._news) != 9:
                    raise SerializationError(f"Expected length of news to be exactly 9, got {len(data._news)}.")
                for i in range(9):
                    writer.add_string(data._news[i])
                    writer.add_byte(0xFF)
                if data._weight is None:
                    raise SerializationError("weight must be provided.")
                Weight.serialize(writer, data._weight)
                if data._items is None:
                    raise SerializationError("items must be provided.")
                for i in range(len(data._items)):
                    Item.serialize(writer, data._items[i])
                writer.add_byte(0xFF)
                if data._spells is None:
                    raise SerializationError("spells must be provided.")
                for i in range(len(data._spells)):
                    Spell.serialize(writer, data._spells[i])
                writer.add_byte(0xFF)
                if data._nearby is None:
                    raise SerializationError("nearby must be provided.")
                NearbyInfo.serialize(writer, data._nearby)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeReplyServerPacket.WelcomeCodeDataEnterGame":
            """
            Deserializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataEnterGame` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeReplyServerPacket.WelcomeCodeDataEnterGame: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.next_chunk()
                news = []
                for i in range(9):
                    news.append(reader.get_string())
                    reader.next_chunk()
                weight = Weight.deserialize(reader)
                items_length = int(reader.remaining / 6)
                items = []
                for i in range(items_length):
                    items.append(Item.deserialize(reader))
                reader.next_chunk()
                spells_length = int(reader.remaining / 4)
                spells = []
                for i in range(spells_length):
                    spells.append(Spell.deserialize(reader))
                reader.next_chunk()
                nearby = NearbyInfo.deserialize(reader)
                result = WelcomeReplyServerPacket.WelcomeCodeDataEnterGame(news=news, weight=weight, items=items, spells=spells, nearby=nearby)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeReplyServerPacket.WelcomeCodeDataEnterGame(byte_size={repr(self._byte_size)}, news={repr(self._news)}, weight={repr(self._weight)}, items={repr(self._items)}, spells={repr(self._spells)}, nearby={repr(self._nearby)})"
