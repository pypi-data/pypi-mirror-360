# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EquipmentPaperdoll:
    """
    Player equipment data.
    Sent with information about a player's paperdoll.
    Note that these values are item IDs.
    """
    _byte_size: int = 0
    _boots: int
    _accessory: int
    _gloves: int
    _belt: int
    _armor: int
    _necklace: int
    _hat: int
    _shield: int
    _weapon: int
    _ring: tuple[int, ...]
    _armlet: tuple[int, ...]
    _bracer: tuple[int, ...]

    def __init__(self, *, boots: int, accessory: int, gloves: int, belt: int, armor: int, necklace: int, hat: int, shield: int, weapon: int, ring: Iterable[int], armlet: Iterable[int], bracer: Iterable[int]):
        """
        Create a new instance of EquipmentPaperdoll.

        Args:
            boots (int): (Value range is 0-64008.)
            accessory (int): (Value range is 0-64008.)
            gloves (int): (Value range is 0-64008.)
            belt (int): (Value range is 0-64008.)
            armor (int): (Value range is 0-64008.)
            necklace (int): (Value range is 0-64008.)
            hat (int): (Value range is 0-64008.)
            shield (int): (Value range is 0-64008.)
            weapon (int): (Value range is 0-64008.)
            ring (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
            armlet (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
            bracer (Iterable[int]): (Length must be `2`.) (Element value range is 0-64008.)
        """
        self._boots = boots
        self._accessory = accessory
        self._gloves = gloves
        self._belt = belt
        self._armor = armor
        self._necklace = necklace
        self._hat = hat
        self._shield = shield
        self._weapon = weapon
        self._ring = tuple(ring)
        self._armlet = tuple(armlet)
        self._bracer = tuple(bracer)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def boots(self) -> int:
        return self._boots

    @property
    def accessory(self) -> int:
        return self._accessory

    @property
    def gloves(self) -> int:
        return self._gloves

    @property
    def belt(self) -> int:
        return self._belt

    @property
    def armor(self) -> int:
        return self._armor

    @property
    def necklace(self) -> int:
        return self._necklace

    @property
    def hat(self) -> int:
        return self._hat

    @property
    def shield(self) -> int:
        return self._shield

    @property
    def weapon(self) -> int:
        return self._weapon

    @property
    def ring(self) -> tuple[int, ...]:
        return self._ring

    @property
    def armlet(self) -> tuple[int, ...]:
        return self._armlet

    @property
    def bracer(self) -> tuple[int, ...]:
        return self._bracer

    @staticmethod
    def serialize(writer: EoWriter, data: "EquipmentPaperdoll") -> None:
        """
        Serializes an instance of `EquipmentPaperdoll` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EquipmentPaperdoll): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._boots is None:
                raise SerializationError("boots must be provided.")
            writer.add_short(data._boots)
            if data._accessory is None:
                raise SerializationError("accessory must be provided.")
            writer.add_short(data._accessory)
            if data._gloves is None:
                raise SerializationError("gloves must be provided.")
            writer.add_short(data._gloves)
            if data._belt is None:
                raise SerializationError("belt must be provided.")
            writer.add_short(data._belt)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
            if data._necklace is None:
                raise SerializationError("necklace must be provided.")
            writer.add_short(data._necklace)
            if data._hat is None:
                raise SerializationError("hat must be provided.")
            writer.add_short(data._hat)
            if data._shield is None:
                raise SerializationError("shield must be provided.")
            writer.add_short(data._shield)
            if data._weapon is None:
                raise SerializationError("weapon must be provided.")
            writer.add_short(data._weapon)
            if data._ring is None:
                raise SerializationError("ring must be provided.")
            if len(data._ring) != 2:
                raise SerializationError(f"Expected length of ring to be exactly 2, got {len(data._ring)}.")
            for i in range(2):
                writer.add_short(data._ring[i])
            if data._armlet is None:
                raise SerializationError("armlet must be provided.")
            if len(data._armlet) != 2:
                raise SerializationError(f"Expected length of armlet to be exactly 2, got {len(data._armlet)}.")
            for i in range(2):
                writer.add_short(data._armlet[i])
            if data._bracer is None:
                raise SerializationError("bracer must be provided.")
            if len(data._bracer) != 2:
                raise SerializationError(f"Expected length of bracer to be exactly 2, got {len(data._bracer)}.")
            for i in range(2):
                writer.add_short(data._bracer[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EquipmentPaperdoll":
        """
        Deserializes an instance of `EquipmentPaperdoll` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EquipmentPaperdoll: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            boots = reader.get_short()
            accessory = reader.get_short()
            gloves = reader.get_short()
            belt = reader.get_short()
            armor = reader.get_short()
            necklace = reader.get_short()
            hat = reader.get_short()
            shield = reader.get_short()
            weapon = reader.get_short()
            ring = []
            for i in range(2):
                ring.append(reader.get_short())
            armlet = []
            for i in range(2):
                armlet.append(reader.get_short())
            bracer = []
            for i in range(2):
                bracer.append(reader.get_short())
            result = EquipmentPaperdoll(boots=boots, accessory=accessory, gloves=gloves, belt=belt, armor=armor, necklace=necklace, hat=hat, shield=shield, weapon=weapon, ring=ring, armlet=armlet, bracer=bracer)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EquipmentPaperdoll(byte_size={repr(self._byte_size)}, boots={repr(self._boots)}, accessory={repr(self._accessory)}, gloves={repr(self._gloves)}, belt={repr(self._belt)}, armor={repr(self._armor)}, necklace={repr(self._necklace)}, hat={repr(self._hat)}, shield={repr(self._shield)}, weapon={repr(self._weapon)}, ring={repr(self._ring)}, armlet={repr(self._armlet)}, bracer={repr(self._bracer)})"
