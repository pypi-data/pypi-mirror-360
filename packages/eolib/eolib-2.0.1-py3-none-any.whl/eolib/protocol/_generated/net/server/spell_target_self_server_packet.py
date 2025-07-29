# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SpellTargetSelfServerPacket(Packet):
    """
    Nearby player self-casted a spell
    """
    _byte_size: int = 0
    _player_id: int
    _spell_id: int
    _spell_heal_hp: int
    _hp_percentage: int
    _hp: Optional[int]
    _tp: Optional[int]

    def __init__(self, *, player_id: int, spell_id: int, spell_heal_hp: int, hp_percentage: int, hp: Optional[int] = None, tp: Optional[int] = None):
        """
        Create a new instance of SpellTargetSelfServerPacket.

        Args:
            player_id (int): (Value range is 0-64008.)
            spell_id (int): (Value range is 0-64008.)
            spell_heal_hp (int): (Value range is 0-4097152080.)
            hp_percentage (int): (Value range is 0-252.)
            hp (Optional[int]): The official client reads this if the packet is larger than 12 bytes (Value range is 0-64008.)
            tp (Optional[int]): The official client reads this if the packet is larger than 12 bytes (Value range is 0-64008.)
        """
        self._player_id = player_id
        self._spell_id = spell_id
        self._spell_heal_hp = spell_heal_hp
        self._hp_percentage = hp_percentage
        self._hp = hp
        self._tp = tp

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def spell_id(self) -> int:
        return self._spell_id

    @property
    def spell_heal_hp(self) -> int:
        return self._spell_heal_hp

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @property
    def hp(self) -> Optional[int]:
        """
        The official client reads this if the packet is larger than 12 bytes
        """
        return self._hp

    @property
    def tp(self) -> Optional[int]:
        """
        The official client reads this if the packet is larger than 12 bytes
        """
        return self._tp

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Spell

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.TargetSelf

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        SpellTargetSelfServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SpellTargetSelfServerPacket") -> None:
        """
        Serializes an instance of `SpellTargetSelfServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SpellTargetSelfServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
            if data._spell_heal_hp is None:
                raise SerializationError("spell_heal_hp must be provided.")
            writer.add_int(data._spell_heal_hp)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            reached_missing_optional = data._hp is None
            if not reached_missing_optional:
                writer.add_short(cast(int, data._hp))
            reached_missing_optional = reached_missing_optional or data._tp is None
            if not reached_missing_optional:
                writer.add_short(cast(int, data._tp))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SpellTargetSelfServerPacket":
        """
        Deserializes an instance of `SpellTargetSelfServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SpellTargetSelfServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            spell_id = reader.get_short()
            spell_heal_hp = reader.get_int()
            hp_percentage = reader.get_char()
            hp: Optional[int] = None
            if reader.remaining > 0:
                hp = reader.get_short()
            tp: Optional[int] = None
            if reader.remaining > 0:
                tp = reader.get_short()
            result = SpellTargetSelfServerPacket(player_id=player_id, spell_id=spell_id, spell_heal_hp=spell_heal_hp, hp_percentage=hp_percentage, hp=hp, tp=tp)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SpellTargetSelfServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, spell_id={repr(self._spell_id)}, spell_heal_hp={repr(self._spell_heal_hp)}, hp_percentage={repr(self._hp_percentage)}, hp={repr(self._hp)}, tp={repr(self._tp)})"
