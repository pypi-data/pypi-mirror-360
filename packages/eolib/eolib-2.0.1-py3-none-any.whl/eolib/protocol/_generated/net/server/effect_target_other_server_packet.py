# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .map_drain_damage_other import MapDrainDamageOther
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectTargetOtherServerPacket(Packet):
    """
    Map drain damage
    """
    _byte_size: int = 0
    _damage: int
    _hp: int
    _max_hp: int
    _others: tuple[MapDrainDamageOther, ...]

    def __init__(self, *, damage: int, hp: int, max_hp: int, others: Iterable[MapDrainDamageOther]):
        """
        Create a new instance of EffectTargetOtherServerPacket.

        Args:
            damage (int): (Value range is 0-64008.)
            hp (int): (Value range is 0-64008.)
            max_hp (int): (Value range is 0-64008.)
            others (Iterable[MapDrainDamageOther]): 
        """
        self._damage = damage
        self._hp = hp
        self._max_hp = max_hp
        self._others = tuple(others)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def others(self) -> tuple[MapDrainDamageOther, ...]:
        return self._others

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
        return PacketAction.TargetOther

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        EffectTargetOtherServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectTargetOtherServerPacket") -> None:
        """
        Serializes an instance of `EffectTargetOtherServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectTargetOtherServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_short(data._damage)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._others is None:
                raise SerializationError("others must be provided.")
            for i in range(len(data._others)):
                MapDrainDamageOther.serialize(writer, data._others[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectTargetOtherServerPacket":
        """
        Deserializes an instance of `EffectTargetOtherServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectTargetOtherServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            damage = reader.get_short()
            hp = reader.get_short()
            max_hp = reader.get_short()
            others_length = int(reader.remaining / 5)
            others = []
            for i in range(others_length):
                others.append(MapDrainDamageOther.deserialize(reader))
            result = EffectTargetOtherServerPacket(damage=damage, hp=hp, max_hp=max_hp, others=others)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectTargetOtherServerPacket(byte_size={repr(self._byte_size)}, damage={repr(self._damage)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)}, others={repr(self._others)})"
