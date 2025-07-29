# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .npc_type import NpcType
from .element import Element
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EnfRecord:
    """
    Record of NPC data in an Endless NPC File
    """
    _byte_size: int = 0
    _name_length: int
    _name: str
    _graphic_id: int
    _race: int
    _boss: bool
    _child: bool
    _type: NpcType
    _behavior_id: int
    _hp: int
    _tp: int
    _min_damage: int
    _max_damage: int
    _accuracy: int
    _evade: int
    _armor: int
    _return_damage: int
    _element: Element
    _element_damage: int
    _element_weakness: Element
    _element_weakness_damage: int
    _level: int
    _experience: int

    def __init__(self, *, name: str, graphic_id: int, race: int, boss: bool, child: bool, type: NpcType, behavior_id: int, hp: int, tp: int, min_damage: int, max_damage: int, accuracy: int, evade: int, armor: int, return_damage: int, element: Element, element_damage: int, element_weakness: Element, element_weakness_damage: int, level: int, experience: int):
        """
        Create a new instance of EnfRecord.

        Args:
            name (str): (Length must be 252 or less.)
            graphic_id (int): (Value range is 0-64008.)
            race (int): (Value range is 0-252.)
            boss (bool): 
            child (bool): 
            type (NpcType): 
            behavior_id (int): (Value range is 0-64008.)
            hp (int): (Value range is 0-16194276.)
            tp (int): (Value range is 0-64008.)
            min_damage (int): (Value range is 0-64008.)
            max_damage (int): (Value range is 0-64008.)
            accuracy (int): (Value range is 0-64008.)
            evade (int): (Value range is 0-64008.)
            armor (int): (Value range is 0-64008.)
            return_damage (int): (Value range is 0-252.)
            element (Element): 
            element_damage (int): (Value range is 0-64008.)
            element_weakness (Element): 
            element_weakness_damage (int): (Value range is 0-64008.)
            level (int): (Value range is 0-252.)
            experience (int): (Value range is 0-16194276.)
        """
        self._name = name
        self._name_length = len(self._name)
        self._graphic_id = graphic_id
        self._race = race
        self._boss = boss
        self._child = child
        self._type = type
        self._behavior_id = behavior_id
        self._hp = hp
        self._tp = tp
        self._min_damage = min_damage
        self._max_damage = max_damage
        self._accuracy = accuracy
        self._evade = evade
        self._armor = armor
        self._return_damage = return_damage
        self._element = element
        self._element_damage = element_damage
        self._element_weakness = element_weakness
        self._element_weakness_damage = element_weakness_damage
        self._level = level
        self._experience = experience

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
    def graphic_id(self) -> int:
        return self._graphic_id

    @property
    def race(self) -> int:
        return self._race

    @property
    def boss(self) -> bool:
        return self._boss

    @property
    def child(self) -> bool:
        return self._child

    @property
    def type(self) -> NpcType:
        return self._type

    @property
    def behavior_id(self) -> int:
        return self._behavior_id

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def tp(self) -> int:
        return self._tp

    @property
    def min_damage(self) -> int:
        return self._min_damage

    @property
    def max_damage(self) -> int:
        return self._max_damage

    @property
    def accuracy(self) -> int:
        return self._accuracy

    @property
    def evade(self) -> int:
        return self._evade

    @property
    def armor(self) -> int:
        return self._armor

    @property
    def return_damage(self) -> int:
        return self._return_damage

    @property
    def element(self) -> Element:
        return self._element

    @property
    def element_damage(self) -> int:
        return self._element_damage

    @property
    def element_weakness(self) -> Element:
        return self._element_weakness

    @property
    def element_weakness_damage(self) -> int:
        return self._element_weakness_damage

    @property
    def level(self) -> int:
        return self._level

    @property
    def experience(self) -> int:
        return self._experience

    @staticmethod
    def serialize(writer: EoWriter, data: "EnfRecord") -> None:
        """
        Serializes an instance of `EnfRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EnfRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._graphic_id is None:
                raise SerializationError("graphic_id must be provided.")
            writer.add_short(data._graphic_id)
            if data._race is None:
                raise SerializationError("race must be provided.")
            writer.add_char(data._race)
            if data._boss is None:
                raise SerializationError("boss must be provided.")
            writer.add_short(1 if data._boss else 0)
            if data._child is None:
                raise SerializationError("child must be provided.")
            writer.add_short(1 if data._child else 0)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_short(int(data._type))
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_three(data._hp)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
            if data._min_damage is None:
                raise SerializationError("min_damage must be provided.")
            writer.add_short(data._min_damage)
            if data._max_damage is None:
                raise SerializationError("max_damage must be provided.")
            writer.add_short(data._max_damage)
            if data._accuracy is None:
                raise SerializationError("accuracy must be provided.")
            writer.add_short(data._accuracy)
            if data._evade is None:
                raise SerializationError("evade must be provided.")
            writer.add_short(data._evade)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
            if data._return_damage is None:
                raise SerializationError("return_damage must be provided.")
            writer.add_char(data._return_damage)
            if data._element is None:
                raise SerializationError("element must be provided.")
            writer.add_short(int(data._element))
            if data._element_damage is None:
                raise SerializationError("element_damage must be provided.")
            writer.add_short(data._element_damage)
            if data._element_weakness is None:
                raise SerializationError("element_weakness must be provided.")
            writer.add_short(int(data._element_weakness))
            if data._element_weakness_damage is None:
                raise SerializationError("element_weakness_damage must be provided.")
            writer.add_short(data._element_weakness_damage)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._experience is None:
                raise SerializationError("experience must be provided.")
            writer.add_three(data._experience)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EnfRecord":
        """
        Deserializes an instance of `EnfRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EnfRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            name_length = reader.get_char()
            name = reader.get_fixed_string(name_length, False)
            graphic_id = reader.get_short()
            race = reader.get_char()
            boss = reader.get_short() != 0
            child = reader.get_short() != 0
            type = NpcType(reader.get_short())
            behavior_id = reader.get_short()
            hp = reader.get_three()
            tp = reader.get_short()
            min_damage = reader.get_short()
            max_damage = reader.get_short()
            accuracy = reader.get_short()
            evade = reader.get_short()
            armor = reader.get_short()
            return_damage = reader.get_char()
            element = Element(reader.get_short())
            element_damage = reader.get_short()
            element_weakness = Element(reader.get_short())
            element_weakness_damage = reader.get_short()
            level = reader.get_char()
            experience = reader.get_three()
            result = EnfRecord(name=name, graphic_id=graphic_id, race=race, boss=boss, child=child, type=type, behavior_id=behavior_id, hp=hp, tp=tp, min_damage=min_damage, max_damage=max_damage, accuracy=accuracy, evade=evade, armor=armor, return_damage=return_damage, element=element, element_damage=element_damage, element_weakness=element_weakness, element_weakness_damage=element_weakness_damage, level=level, experience=experience)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EnfRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, graphic_id={repr(self._graphic_id)}, race={repr(self._race)}, boss={repr(self._boss)}, child={repr(self._child)}, type={repr(self._type)}, behavior_id={repr(self._behavior_id)}, hp={repr(self._hp)}, tp={repr(self._tp)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)}, return_damage={repr(self._return_damage)}, element={repr(self._element)}, element_damage={repr(self._element_damage)}, element_weakness={repr(self._element_weakness)}, element_weakness_damage={repr(self._element_weakness_damage)}, level={repr(self._level)}, experience={repr(self._experience)})"
