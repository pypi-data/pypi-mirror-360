# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .map_damage_type import MapDamageType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectSpecServerPacket(Packet):
    """
    Taking spike or tp drain damage
    """
    _byte_size: int = 0
    _map_damage_type: MapDamageType
    _map_damage_type_data: 'EffectSpecServerPacket.MapDamageTypeData'

    def __init__(self, *, map_damage_type: MapDamageType, map_damage_type_data: 'EffectSpecServerPacket.MapDamageTypeData' = None):
        """
        Create a new instance of EffectSpecServerPacket.

        Args:
            map_damage_type (MapDamageType): 
            map_damage_type_data (EffectSpecServerPacket.MapDamageTypeData): Data associated with the `map_damage_type` field.
        """
        self._map_damage_type = map_damage_type
        self._map_damage_type_data = map_damage_type_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def map_damage_type(self) -> MapDamageType:
        return self._map_damage_type

    @property
    def map_damage_type_data(self) -> 'EffectSpecServerPacket.MapDamageTypeData':
        """
        EffectSpecServerPacket.MapDamageTypeData: Data associated with the `map_damage_type` field.
        """
        return self._map_damage_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Effect

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Spec

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        EffectSpecServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectSpecServerPacket") -> None:
        """
        Serializes an instance of `EffectSpecServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectSpecServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._map_damage_type is None:
                raise SerializationError("map_damage_type must be provided.")
            writer.add_char(int(data._map_damage_type))
            if data._map_damage_type == MapDamageType.TpDrain:
                if not isinstance(data._map_damage_type_data, EffectSpecServerPacket.MapDamageTypeDataTpDrain):
                    raise SerializationError("Expected map_damage_type_data to be type EffectSpecServerPacket.MapDamageTypeDataTpDrain for map_damage_type " + MapDamageType(data._map_damage_type).name + ".")
                EffectSpecServerPacket.MapDamageTypeDataTpDrain.serialize(writer, data._map_damage_type_data)
            elif data._map_damage_type == MapDamageType.Spikes:
                if not isinstance(data._map_damage_type_data, EffectSpecServerPacket.MapDamageTypeDataSpikes):
                    raise SerializationError("Expected map_damage_type_data to be type EffectSpecServerPacket.MapDamageTypeDataSpikes for map_damage_type " + MapDamageType(data._map_damage_type).name + ".")
                EffectSpecServerPacket.MapDamageTypeDataSpikes.serialize(writer, data._map_damage_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectSpecServerPacket":
        """
        Deserializes an instance of `EffectSpecServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectSpecServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            map_damage_type = MapDamageType(reader.get_char())
            map_damage_type_data: EffectSpecServerPacket.MapDamageTypeData = None
            if map_damage_type == MapDamageType.TpDrain:
                map_damage_type_data = EffectSpecServerPacket.MapDamageTypeDataTpDrain.deserialize(reader)
            elif map_damage_type == MapDamageType.Spikes:
                map_damage_type_data = EffectSpecServerPacket.MapDamageTypeDataSpikes.deserialize(reader)
            result = EffectSpecServerPacket(map_damage_type=map_damage_type, map_damage_type_data=map_damage_type_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectSpecServerPacket(byte_size={repr(self._byte_size)}, map_damage_type={repr(self._map_damage_type)}, map_damage_type_data={repr(self._map_damage_type_data)})"

    MapDamageTypeData = Union['EffectSpecServerPacket.MapDamageTypeDataTpDrain', 'EffectSpecServerPacket.MapDamageTypeDataSpikes', None]
    """
    Data associated with different values of the `map_damage_type` field.
    """

    class MapDamageTypeDataTpDrain:
        """
        Data associated with map_damage_type value MapDamageType.TpDrain
        """
        _byte_size: int = 0
        _tp_damage: int
        _tp: int
        _max_tp: int

        def __init__(self, *, tp_damage: int, tp: int, max_tp: int):
            """
            Create a new instance of EffectSpecServerPacket.MapDamageTypeDataTpDrain.

            Args:
                tp_damage (int): (Value range is 0-64008.)
                tp (int): (Value range is 0-64008.)
                max_tp (int): (Value range is 0-64008.)
            """
            self._tp_damage = tp_damage
            self._tp = tp
            self._max_tp = max_tp

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def tp_damage(self) -> int:
            return self._tp_damage

        @property
        def tp(self) -> int:
            return self._tp

        @property
        def max_tp(self) -> int:
            return self._max_tp

        @staticmethod
        def serialize(writer: EoWriter, data: "EffectSpecServerPacket.MapDamageTypeDataTpDrain") -> None:
            """
            Serializes an instance of `EffectSpecServerPacket.MapDamageTypeDataTpDrain` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (EffectSpecServerPacket.MapDamageTypeDataTpDrain): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._tp_damage is None:
                    raise SerializationError("tp_damage must be provided.")
                writer.add_short(data._tp_damage)
                if data._tp is None:
                    raise SerializationError("tp must be provided.")
                writer.add_short(data._tp)
                if data._max_tp is None:
                    raise SerializationError("max_tp must be provided.")
                writer.add_short(data._max_tp)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "EffectSpecServerPacket.MapDamageTypeDataTpDrain":
            """
            Deserializes an instance of `EffectSpecServerPacket.MapDamageTypeDataTpDrain` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                EffectSpecServerPacket.MapDamageTypeDataTpDrain: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                tp_damage = reader.get_short()
                tp = reader.get_short()
                max_tp = reader.get_short()
                result = EffectSpecServerPacket.MapDamageTypeDataTpDrain(tp_damage=tp_damage, tp=tp, max_tp=max_tp)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"EffectSpecServerPacket.MapDamageTypeDataTpDrain(byte_size={repr(self._byte_size)}, tp_damage={repr(self._tp_damage)}, tp={repr(self._tp)}, max_tp={repr(self._max_tp)})"

    class MapDamageTypeDataSpikes:
        """
        Data associated with map_damage_type value MapDamageType.Spikes
        """
        _byte_size: int = 0
        _hp_damage: int
        _hp: int
        _max_hp: int

        def __init__(self, *, hp_damage: int, hp: int, max_hp: int):
            """
            Create a new instance of EffectSpecServerPacket.MapDamageTypeDataSpikes.

            Args:
                hp_damage (int): (Value range is 0-64008.)
                hp (int): (Value range is 0-64008.)
                max_hp (int): (Value range is 0-64008.)
            """
            self._hp_damage = hp_damage
            self._hp = hp
            self._max_hp = max_hp

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def hp_damage(self) -> int:
            return self._hp_damage

        @property
        def hp(self) -> int:
            return self._hp

        @property
        def max_hp(self) -> int:
            return self._max_hp

        @staticmethod
        def serialize(writer: EoWriter, data: "EffectSpecServerPacket.MapDamageTypeDataSpikes") -> None:
            """
            Serializes an instance of `EffectSpecServerPacket.MapDamageTypeDataSpikes` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (EffectSpecServerPacket.MapDamageTypeDataSpikes): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._hp_damage is None:
                    raise SerializationError("hp_damage must be provided.")
                writer.add_short(data._hp_damage)
                if data._hp is None:
                    raise SerializationError("hp must be provided.")
                writer.add_short(data._hp)
                if data._max_hp is None:
                    raise SerializationError("max_hp must be provided.")
                writer.add_short(data._max_hp)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "EffectSpecServerPacket.MapDamageTypeDataSpikes":
            """
            Deserializes an instance of `EffectSpecServerPacket.MapDamageTypeDataSpikes` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                EffectSpecServerPacket.MapDamageTypeDataSpikes: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                hp_damage = reader.get_short()
                hp = reader.get_short()
                max_hp = reader.get_short()
                result = EffectSpecServerPacket.MapDamageTypeDataSpikes(hp_damage=hp_damage, hp=hp, max_hp=max_hp)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"EffectSpecServerPacket.MapDamageTypeDataSpikes(byte_size={repr(self._byte_size)}, hp_damage={repr(self._hp_damage)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)})"
