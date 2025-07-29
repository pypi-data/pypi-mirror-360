# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .tile_effect import TileEffect
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectAgreeServerPacket(Packet):
    """
    Effects playing on nearby tiles
    """
    _byte_size: int = 0
    _effects: tuple[TileEffect, ...]

    def __init__(self, *, effects: Iterable[TileEffect]):
        """
        Create a new instance of EffectAgreeServerPacket.

        Args:
            effects (Iterable[TileEffect]): 
        """
        self._effects = tuple(effects)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def effects(self) -> tuple[TileEffect, ...]:
        return self._effects

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
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        EffectAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectAgreeServerPacket") -> None:
        """
        Serializes an instance of `EffectAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectAgreeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._effects is None:
                raise SerializationError("effects must be provided.")
            for i in range(len(data._effects)):
                TileEffect.serialize(writer, data._effects[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectAgreeServerPacket":
        """
        Deserializes an instance of `EffectAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectAgreeServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            effects_length = int(reader.remaining / 4)
            effects = []
            for i in range(effects_length):
                effects.append(TileEffect.deserialize(reader))
            result = EffectAgreeServerPacket(effects=effects)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectAgreeServerPacket(byte_size={repr(self._byte_size)}, effects={repr(self._effects)})"
