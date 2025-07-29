# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .item_type import ItemType
from .item_subtype import ItemSubtype
from .item_special import ItemSpecial
from .item_size import ItemSize
from .element import Element
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EifRecord:
    """
    Record of Item data in an Endless Item File
    """
    _byte_size: int = 0
    _name_length: int
    _name: str
    _graphic_id: int
    _type: ItemType
    _subtype: ItemSubtype
    _special: ItemSpecial
    _hp: int
    _tp: int
    _min_damage: int
    _max_damage: int
    _accuracy: int
    _evade: int
    _armor: int
    _return_damage: int
    _str: int
    _intl: int
    _wis: int
    _agi: int
    _con: int
    _cha: int
    _light_resistance: int
    _dark_resistance: int
    _earth_resistance: int
    _air_resistance: int
    _water_resistance: int
    _fire_resistance: int
    _spec1: int
    _spec2: int
    _spec3: int
    _level_requirement: int
    _class_requirement: int
    _str_requirement: int
    _int_requirement: int
    _wis_requirement: int
    _agi_requirement: int
    _con_requirement: int
    _cha_requirement: int
    _element: Element
    _element_damage: int
    _weight: int
    _size: ItemSize

    def __init__(self, *, name: str, graphic_id: int, type: ItemType, subtype: ItemSubtype, special: ItemSpecial, hp: int, tp: int, min_damage: int, max_damage: int, accuracy: int, evade: int, armor: int, return_damage: int, str: int, intl: int, wis: int, agi: int, con: int, cha: int, light_resistance: int, dark_resistance: int, earth_resistance: int, air_resistance: int, water_resistance: int, fire_resistance: int, spec1: int, spec2: int, spec3: int, level_requirement: int, class_requirement: int, str_requirement: int, int_requirement: int, wis_requirement: int, agi_requirement: int, con_requirement: int, cha_requirement: int, element: Element, element_damage: int, weight: int, size: ItemSize):
        """
        Create a new instance of EifRecord.

        Args:
            name (str): (Length must be 252 or less.)
            graphic_id (int): (Value range is 0-64008.)
            type (ItemType): 
            subtype (ItemSubtype): 
            special (ItemSpecial): 
            hp (int): (Value range is 0-64008.)
            tp (int): (Value range is 0-64008.)
            min_damage (int): (Value range is 0-64008.)
            max_damage (int): (Value range is 0-64008.)
            accuracy (int): (Value range is 0-64008.)
            evade (int): (Value range is 0-64008.)
            armor (int): (Value range is 0-64008.)
            return_damage (int): (Value range is 0-252.)
            str (int): (Value range is 0-252.)
            intl (int): (Value range is 0-252.)
            wis (int): (Value range is 0-252.)
            agi (int): (Value range is 0-252.)
            con (int): (Value range is 0-252.)
            cha (int): (Value range is 0-252.)
            light_resistance (int): (Value range is 0-252.)
            dark_resistance (int): (Value range is 0-252.)
            earth_resistance (int): (Value range is 0-252.)
            air_resistance (int): (Value range is 0-252.)
            water_resistance (int): (Value range is 0-252.)
            fire_resistance (int): (Value range is 0-252.)
            spec1 (int): Holds one the following values, depending on item type: scroll_map, doll_graphic, exp_reward, hair_color, effect, key, alcohol_potency (Value range is 0-16194276.)
            spec2 (int): Holds one the following values, depending on item type: scroll_x, gender (Value range is 0-252.)
            spec3 (int): Holds one the following values, depending on item type: scroll_y (Value range is 0-252.)
            level_requirement (int): (Value range is 0-64008.)
            class_requirement (int): (Value range is 0-64008.)
            str_requirement (int): (Value range is 0-64008.)
            int_requirement (int): (Value range is 0-64008.)
            wis_requirement (int): (Value range is 0-64008.)
            agi_requirement (int): (Value range is 0-64008.)
            con_requirement (int): (Value range is 0-64008.)
            cha_requirement (int): (Value range is 0-64008.)
            element (Element): 
            element_damage (int): (Value range is 0-252.)
            weight (int): (Value range is 0-252.)
            size (ItemSize): 
        """
        self._name = name
        self._name_length = len(self._name)
        self._graphic_id = graphic_id
        self._type = type
        self._subtype = subtype
        self._special = special
        self._hp = hp
        self._tp = tp
        self._min_damage = min_damage
        self._max_damage = max_damage
        self._accuracy = accuracy
        self._evade = evade
        self._armor = armor
        self._return_damage = return_damage
        self._str = str
        self._intl = intl
        self._wis = wis
        self._agi = agi
        self._con = con
        self._cha = cha
        self._light_resistance = light_resistance
        self._dark_resistance = dark_resistance
        self._earth_resistance = earth_resistance
        self._air_resistance = air_resistance
        self._water_resistance = water_resistance
        self._fire_resistance = fire_resistance
        self._spec1 = spec1
        self._spec2 = spec2
        self._spec3 = spec3
        self._level_requirement = level_requirement
        self._class_requirement = class_requirement
        self._str_requirement = str_requirement
        self._int_requirement = int_requirement
        self._wis_requirement = wis_requirement
        self._agi_requirement = agi_requirement
        self._con_requirement = con_requirement
        self._cha_requirement = cha_requirement
        self._element = element
        self._element_damage = element_damage
        self._weight = weight
        self._size = size

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
    def type(self) -> ItemType:
        return self._type

    @property
    def subtype(self) -> ItemSubtype:
        return self._subtype

    @property
    def special(self) -> ItemSpecial:
        return self._special

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
    def str(self) -> int:
        return self._str

    @property
    def intl(self) -> int:
        return self._intl

    @property
    def wis(self) -> int:
        return self._wis

    @property
    def agi(self) -> int:
        return self._agi

    @property
    def con(self) -> int:
        return self._con

    @property
    def cha(self) -> int:
        return self._cha

    @property
    def light_resistance(self) -> int:
        return self._light_resistance

    @property
    def dark_resistance(self) -> int:
        return self._dark_resistance

    @property
    def earth_resistance(self) -> int:
        return self._earth_resistance

    @property
    def air_resistance(self) -> int:
        return self._air_resistance

    @property
    def water_resistance(self) -> int:
        return self._water_resistance

    @property
    def fire_resistance(self) -> int:
        return self._fire_resistance

    @property
    def spec1(self) -> int:
        """
        Holds one the following values, depending on item type:
        scroll_map, doll_graphic, exp_reward, hair_color, effect, key, alcohol_potency
        """
        return self._spec1

    @property
    def spec2(self) -> int:
        """
        Holds one the following values, depending on item type:
        scroll_x, gender
        """
        return self._spec2

    @property
    def spec3(self) -> int:
        """
        Holds one the following values, depending on item type:
        scroll_y
        """
        return self._spec3

    @property
    def level_requirement(self) -> int:
        return self._level_requirement

    @property
    def class_requirement(self) -> int:
        return self._class_requirement

    @property
    def str_requirement(self) -> int:
        return self._str_requirement

    @property
    def int_requirement(self) -> int:
        return self._int_requirement

    @property
    def wis_requirement(self) -> int:
        return self._wis_requirement

    @property
    def agi_requirement(self) -> int:
        return self._agi_requirement

    @property
    def con_requirement(self) -> int:
        return self._con_requirement

    @property
    def cha_requirement(self) -> int:
        return self._cha_requirement

    @property
    def element(self) -> Element:
        return self._element

    @property
    def element_damage(self) -> int:
        return self._element_damage

    @property
    def weight(self) -> int:
        return self._weight

    @property
    def size(self) -> ItemSize:
        return self._size

    @staticmethod
    def serialize(writer: EoWriter, data: "EifRecord") -> None:
        """
        Serializes an instance of `EifRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EifRecord): The data to serialize.
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
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_char(int(data._type))
            if data._subtype is None:
                raise SerializationError("subtype must be provided.")
            writer.add_char(int(data._subtype))
            if data._special is None:
                raise SerializationError("special must be provided.")
            writer.add_char(int(data._special))
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
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
            if data._str is None:
                raise SerializationError("str must be provided.")
            writer.add_char(data._str)
            if data._intl is None:
                raise SerializationError("intl must be provided.")
            writer.add_char(data._intl)
            if data._wis is None:
                raise SerializationError("wis must be provided.")
            writer.add_char(data._wis)
            if data._agi is None:
                raise SerializationError("agi must be provided.")
            writer.add_char(data._agi)
            if data._con is None:
                raise SerializationError("con must be provided.")
            writer.add_char(data._con)
            if data._cha is None:
                raise SerializationError("cha must be provided.")
            writer.add_char(data._cha)
            if data._light_resistance is None:
                raise SerializationError("light_resistance must be provided.")
            writer.add_char(data._light_resistance)
            if data._dark_resistance is None:
                raise SerializationError("dark_resistance must be provided.")
            writer.add_char(data._dark_resistance)
            if data._earth_resistance is None:
                raise SerializationError("earth_resistance must be provided.")
            writer.add_char(data._earth_resistance)
            if data._air_resistance is None:
                raise SerializationError("air_resistance must be provided.")
            writer.add_char(data._air_resistance)
            if data._water_resistance is None:
                raise SerializationError("water_resistance must be provided.")
            writer.add_char(data._water_resistance)
            if data._fire_resistance is None:
                raise SerializationError("fire_resistance must be provided.")
            writer.add_char(data._fire_resistance)
            if data._spec1 is None:
                raise SerializationError("spec1 must be provided.")
            writer.add_three(data._spec1)
            if data._spec2 is None:
                raise SerializationError("spec2 must be provided.")
            writer.add_char(data._spec2)
            if data._spec3 is None:
                raise SerializationError("spec3 must be provided.")
            writer.add_char(data._spec3)
            if data._level_requirement is None:
                raise SerializationError("level_requirement must be provided.")
            writer.add_short(data._level_requirement)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_short(data._class_requirement)
            if data._str_requirement is None:
                raise SerializationError("str_requirement must be provided.")
            writer.add_short(data._str_requirement)
            if data._int_requirement is None:
                raise SerializationError("int_requirement must be provided.")
            writer.add_short(data._int_requirement)
            if data._wis_requirement is None:
                raise SerializationError("wis_requirement must be provided.")
            writer.add_short(data._wis_requirement)
            if data._agi_requirement is None:
                raise SerializationError("agi_requirement must be provided.")
            writer.add_short(data._agi_requirement)
            if data._con_requirement is None:
                raise SerializationError("con_requirement must be provided.")
            writer.add_short(data._con_requirement)
            if data._cha_requirement is None:
                raise SerializationError("cha_requirement must be provided.")
            writer.add_short(data._cha_requirement)
            if data._element is None:
                raise SerializationError("element must be provided.")
            writer.add_char(int(data._element))
            if data._element_damage is None:
                raise SerializationError("element_damage must be provided.")
            writer.add_char(data._element_damage)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            writer.add_char(data._weight)
            writer.add_char(0)
            if data._size is None:
                raise SerializationError("size must be provided.")
            writer.add_char(int(data._size))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EifRecord":
        """
        Deserializes an instance of `EifRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EifRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            name_length = reader.get_char()
            name = reader.get_fixed_string(name_length, False)
            graphic_id = reader.get_short()
            type = ItemType(reader.get_char())
            subtype = ItemSubtype(reader.get_char())
            special = ItemSpecial(reader.get_char())
            hp = reader.get_short()
            tp = reader.get_short()
            min_damage = reader.get_short()
            max_damage = reader.get_short()
            accuracy = reader.get_short()
            evade = reader.get_short()
            armor = reader.get_short()
            return_damage = reader.get_char()
            str = reader.get_char()
            intl = reader.get_char()
            wis = reader.get_char()
            agi = reader.get_char()
            con = reader.get_char()
            cha = reader.get_char()
            light_resistance = reader.get_char()
            dark_resistance = reader.get_char()
            earth_resistance = reader.get_char()
            air_resistance = reader.get_char()
            water_resistance = reader.get_char()
            fire_resistance = reader.get_char()
            spec1 = reader.get_three()
            spec2 = reader.get_char()
            spec3 = reader.get_char()
            level_requirement = reader.get_short()
            class_requirement = reader.get_short()
            str_requirement = reader.get_short()
            int_requirement = reader.get_short()
            wis_requirement = reader.get_short()
            agi_requirement = reader.get_short()
            con_requirement = reader.get_short()
            cha_requirement = reader.get_short()
            element = Element(reader.get_char())
            element_damage = reader.get_char()
            weight = reader.get_char()
            reader.get_char()
            size = ItemSize(reader.get_char())
            result = EifRecord(name=name, graphic_id=graphic_id, type=type, subtype=subtype, special=special, hp=hp, tp=tp, min_damage=min_damage, max_damage=max_damage, accuracy=accuracy, evade=evade, armor=armor, return_damage=return_damage, str=str, intl=intl, wis=wis, agi=agi, con=con, cha=cha, light_resistance=light_resistance, dark_resistance=dark_resistance, earth_resistance=earth_resistance, air_resistance=air_resistance, water_resistance=water_resistance, fire_resistance=fire_resistance, spec1=spec1, spec2=spec2, spec3=spec3, level_requirement=level_requirement, class_requirement=class_requirement, str_requirement=str_requirement, int_requirement=int_requirement, wis_requirement=wis_requirement, agi_requirement=agi_requirement, con_requirement=con_requirement, cha_requirement=cha_requirement, element=element, element_damage=element_damage, weight=weight, size=size)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EifRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, graphic_id={repr(self._graphic_id)}, type={repr(self._type)}, subtype={repr(self._subtype)}, special={repr(self._special)}, hp={repr(self._hp)}, tp={repr(self._tp)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)}, return_damage={repr(self._return_damage)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)}, light_resistance={repr(self._light_resistance)}, dark_resistance={repr(self._dark_resistance)}, earth_resistance={repr(self._earth_resistance)}, air_resistance={repr(self._air_resistance)}, water_resistance={repr(self._water_resistance)}, fire_resistance={repr(self._fire_resistance)}, spec1={repr(self._spec1)}, spec2={repr(self._spec2)}, spec3={repr(self._spec3)}, level_requirement={repr(self._level_requirement)}, class_requirement={repr(self._class_requirement)}, str_requirement={repr(self._str_requirement)}, int_requirement={repr(self._int_requirement)}, wis_requirement={repr(self._wis_requirement)}, agi_requirement={repr(self._agi_requirement)}, con_requirement={repr(self._con_requirement)}, cha_requirement={repr(self._cha_requirement)}, element={repr(self._element)}, element_damage={repr(self._element_damage)}, weight={repr(self._weight)}, size={repr(self._size)})"
