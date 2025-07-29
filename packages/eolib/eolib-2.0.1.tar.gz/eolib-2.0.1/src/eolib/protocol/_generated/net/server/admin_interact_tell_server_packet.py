# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_stats_info_lookup import CharacterStatsInfoLookup
from .big_coords import BigCoords
from ..weight import Weight
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AdminInteractTellServerPacket(Packet):
    """
    Admin character info lookup
    """
    _byte_size: int = 0
    _name: str
    _usage: int
    _gold_bank: int
    _exp: int
    _level: int
    _map_id: int
    _map_coords: BigCoords
    _stats: CharacterStatsInfoLookup
    _weight: Weight

    def __init__(self, *, name: str, usage: int, gold_bank: int, exp: int, level: int, map_id: int, map_coords: BigCoords, stats: CharacterStatsInfoLookup, weight: Weight):
        """
        Create a new instance of AdminInteractTellServerPacket.

        Args:
            name (str): 
            usage (int): (Value range is 0-4097152080.)
            gold_bank (int): (Value range is 0-4097152080.)
            exp (int): (Value range is 0-4097152080.)
            level (int): (Value range is 0-252.)
            map_id (int): (Value range is 0-64008.)
            map_coords (BigCoords): 
            stats (CharacterStatsInfoLookup): 
            weight (Weight): 
        """
        self._name = name
        self._usage = usage
        self._gold_bank = gold_bank
        self._exp = exp
        self._level = level
        self._map_id = map_id
        self._map_coords = map_coords
        self._stats = stats
        self._weight = weight

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
    def usage(self) -> int:
        return self._usage

    @property
    def gold_bank(self) -> int:
        return self._gold_bank

    @property
    def exp(self) -> int:
        return self._exp

    @property
    def level(self) -> int:
        return self._level

    @property
    def map_id(self) -> int:
        return self._map_id

    @property
    def map_coords(self) -> BigCoords:
        return self._map_coords

    @property
    def stats(self) -> CharacterStatsInfoLookup:
        return self._stats

    @property
    def weight(self) -> Weight:
        return self._weight

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.AdminInteract

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Tell

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AdminInteractTellServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AdminInteractTellServerPacket") -> None:
        """
        Serializes an instance of `AdminInteractTellServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AdminInteractTellServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._usage is None:
                raise SerializationError("usage must be provided.")
            writer.add_int(data._usage)
            writer.add_byte(0xFF)
            if data._gold_bank is None:
                raise SerializationError("gold_bank must be provided.")
            writer.add_int(data._gold_bank)
            writer.add_byte(0xFF)
            if data._exp is None:
                raise SerializationError("exp must be provided.")
            writer.add_int(data._exp)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._map_id is None:
                raise SerializationError("map_id must be provided.")
            writer.add_short(data._map_id)
            if data._map_coords is None:
                raise SerializationError("map_coords must be provided.")
            BigCoords.serialize(writer, data._map_coords)
            if data._stats is None:
                raise SerializationError("stats must be provided.")
            CharacterStatsInfoLookup.serialize(writer, data._stats)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AdminInteractTellServerPacket":
        """
        Deserializes an instance of `AdminInteractTellServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AdminInteractTellServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            name = reader.get_string()
            reader.next_chunk()
            usage = reader.get_int()
            reader.next_chunk()
            gold_bank = reader.get_int()
            reader.next_chunk()
            exp = reader.get_int()
            level = reader.get_char()
            map_id = reader.get_short()
            map_coords = BigCoords.deserialize(reader)
            stats = CharacterStatsInfoLookup.deserialize(reader)
            weight = Weight.deserialize(reader)
            reader.chunked_reading_mode = False
            result = AdminInteractTellServerPacket(name=name, usage=usage, gold_bank=gold_bank, exp=exp, level=level, map_id=map_id, map_coords=map_coords, stats=stats, weight=weight)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AdminInteractTellServerPacket(byte_size={repr(self._byte_size)}, name={repr(self._name)}, usage={repr(self._usage)}, gold_bank={repr(self._gold_bank)}, exp={repr(self._exp)}, level={repr(self._level)}, map_id={repr(self._map_id)}, map_coords={repr(self._map_coords)}, stats={repr(self._stats)}, weight={repr(self._weight)})"
