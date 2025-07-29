# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .skill_type import SkillType
from .skill_target_type import SkillTargetType
from .skill_target_restrict import SkillTargetRestrict
from .skill_nature import SkillNature
from .element import Element
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EsfRecord:
    """
    Record of Skill data in an Endless Skill File
    """
    _byte_size: int = 0
    _name_length: int
    _chant_length: int
    _name: str
    _chant: str
    _icon_id: int
    _graphic_id: int
    _tp_cost: int
    _sp_cost: int
    _cast_time: int
    _nature: SkillNature
    _type: SkillType
    _element: Element
    _element_power: int
    _target_restrict: SkillTargetRestrict
    _target_type: SkillTargetType
    _target_time: int
    _max_skill_level: int
    _min_damage: int
    _max_damage: int
    _accuracy: int
    _evade: int
    _armor: int
    _return_damage: int
    _hp_heal: int
    _tp_heal: int
    _sp_heal: int
    _str: int
    _intl: int
    _wis: int
    _agi: int
    _con: int
    _cha: int

    def __init__(self, *, name: str, chant: str, icon_id: int, graphic_id: int, tp_cost: int, sp_cost: int, cast_time: int, nature: SkillNature, type: SkillType, element: Element, element_power: int, target_restrict: SkillTargetRestrict, target_type: SkillTargetType, target_time: int, max_skill_level: int, min_damage: int, max_damage: int, accuracy: int, evade: int, armor: int, return_damage: int, hp_heal: int, tp_heal: int, sp_heal: int, str: int, intl: int, wis: int, agi: int, con: int, cha: int):
        """
        Create a new instance of EsfRecord.

        Args:
            name (str): (Length must be 252 or less.)
            chant (str): (Length must be 252 or less.)
            icon_id (int): (Value range is 0-64008.)
            graphic_id (int): (Value range is 0-64008.)
            tp_cost (int): (Value range is 0-64008.)
            sp_cost (int): (Value range is 0-64008.)
            cast_time (int): (Value range is 0-252.)
            nature (SkillNature): 
            type (SkillType): 
            element (Element): 
            element_power (int): (Value range is 0-64008.)
            target_restrict (SkillTargetRestrict): 
            target_type (SkillTargetType): 
            target_time (int): (Value range is 0-252.)
            max_skill_level (int): (Value range is 0-64008.)
            min_damage (int): (Value range is 0-64008.)
            max_damage (int): (Value range is 0-64008.)
            accuracy (int): (Value range is 0-64008.)
            evade (int): (Value range is 0-64008.)
            armor (int): (Value range is 0-64008.)
            return_damage (int): (Value range is 0-252.)
            hp_heal (int): (Value range is 0-64008.)
            tp_heal (int): (Value range is 0-64008.)
            sp_heal (int): (Value range is 0-252.)
            str (int): (Value range is 0-64008.)
            intl (int): (Value range is 0-64008.)
            wis (int): (Value range is 0-64008.)
            agi (int): (Value range is 0-64008.)
            con (int): (Value range is 0-64008.)
            cha (int): (Value range is 0-64008.)
        """
        self._name = name
        self._name_length = len(self._name)
        self._chant = chant
        self._chant_length = len(self._chant)
        self._icon_id = icon_id
        self._graphic_id = graphic_id
        self._tp_cost = tp_cost
        self._sp_cost = sp_cost
        self._cast_time = cast_time
        self._nature = nature
        self._type = type
        self._element = element
        self._element_power = element_power
        self._target_restrict = target_restrict
        self._target_type = target_type
        self._target_time = target_time
        self._max_skill_level = max_skill_level
        self._min_damage = min_damage
        self._max_damage = max_damage
        self._accuracy = accuracy
        self._evade = evade
        self._armor = armor
        self._return_damage = return_damage
        self._hp_heal = hp_heal
        self._tp_heal = tp_heal
        self._sp_heal = sp_heal
        self._str = str
        self._intl = intl
        self._wis = wis
        self._agi = agi
        self._con = con
        self._cha = cha

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
    def chant(self) -> str:
        return self._chant

    @property
    def icon_id(self) -> int:
        return self._icon_id

    @property
    def graphic_id(self) -> int:
        return self._graphic_id

    @property
    def tp_cost(self) -> int:
        return self._tp_cost

    @property
    def sp_cost(self) -> int:
        return self._sp_cost

    @property
    def cast_time(self) -> int:
        return self._cast_time

    @property
    def nature(self) -> SkillNature:
        return self._nature

    @property
    def type(self) -> SkillType:
        return self._type

    @property
    def element(self) -> Element:
        return self._element

    @property
    def element_power(self) -> int:
        return self._element_power

    @property
    def target_restrict(self) -> SkillTargetRestrict:
        return self._target_restrict

    @property
    def target_type(self) -> SkillTargetType:
        return self._target_type

    @property
    def target_time(self) -> int:
        return self._target_time

    @property
    def max_skill_level(self) -> int:
        return self._max_skill_level

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
    def hp_heal(self) -> int:
        return self._hp_heal

    @property
    def tp_heal(self) -> int:
        return self._tp_heal

    @property
    def sp_heal(self) -> int:
        return self._sp_heal

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

    @staticmethod
    def serialize(writer: EoWriter, data: "EsfRecord") -> None:
        """
        Serializes an instance of `EsfRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EsfRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._chant_length is None:
                raise SerializationError("chant_length must be provided.")
            writer.add_char(data._chant_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._chant is None:
                raise SerializationError("chant must be provided.")
            if len(data._chant) > 252:
                raise SerializationError(f"Expected length of chant to be 252 or less, got {len(data._chant)}.")
            writer.add_fixed_string(data._chant, data._chant_length, False)
            if data._icon_id is None:
                raise SerializationError("icon_id must be provided.")
            writer.add_short(data._icon_id)
            if data._graphic_id is None:
                raise SerializationError("graphic_id must be provided.")
            writer.add_short(data._graphic_id)
            if data._tp_cost is None:
                raise SerializationError("tp_cost must be provided.")
            writer.add_short(data._tp_cost)
            if data._sp_cost is None:
                raise SerializationError("sp_cost must be provided.")
            writer.add_short(data._sp_cost)
            if data._cast_time is None:
                raise SerializationError("cast_time must be provided.")
            writer.add_char(data._cast_time)
            if data._nature is None:
                raise SerializationError("nature must be provided.")
            writer.add_char(int(data._nature))
            writer.add_char(1)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_three(int(data._type))
            if data._element is None:
                raise SerializationError("element must be provided.")
            writer.add_char(int(data._element))
            if data._element_power is None:
                raise SerializationError("element_power must be provided.")
            writer.add_short(data._element_power)
            if data._target_restrict is None:
                raise SerializationError("target_restrict must be provided.")
            writer.add_char(int(data._target_restrict))
            if data._target_type is None:
                raise SerializationError("target_type must be provided.")
            writer.add_char(int(data._target_type))
            if data._target_time is None:
                raise SerializationError("target_time must be provided.")
            writer.add_char(data._target_time)
            writer.add_char(0)
            if data._max_skill_level is None:
                raise SerializationError("max_skill_level must be provided.")
            writer.add_short(data._max_skill_level)
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
            if data._hp_heal is None:
                raise SerializationError("hp_heal must be provided.")
            writer.add_short(data._hp_heal)
            if data._tp_heal is None:
                raise SerializationError("tp_heal must be provided.")
            writer.add_short(data._tp_heal)
            if data._sp_heal is None:
                raise SerializationError("sp_heal must be provided.")
            writer.add_char(data._sp_heal)
            if data._str is None:
                raise SerializationError("str must be provided.")
            writer.add_short(data._str)
            if data._intl is None:
                raise SerializationError("intl must be provided.")
            writer.add_short(data._intl)
            if data._wis is None:
                raise SerializationError("wis must be provided.")
            writer.add_short(data._wis)
            if data._agi is None:
                raise SerializationError("agi must be provided.")
            writer.add_short(data._agi)
            if data._con is None:
                raise SerializationError("con must be provided.")
            writer.add_short(data._con)
            if data._cha is None:
                raise SerializationError("cha must be provided.")
            writer.add_short(data._cha)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EsfRecord":
        """
        Deserializes an instance of `EsfRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EsfRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            name_length = reader.get_char()
            chant_length = reader.get_char()
            name = reader.get_fixed_string(name_length, False)
            chant = reader.get_fixed_string(chant_length, False)
            icon_id = reader.get_short()
            graphic_id = reader.get_short()
            tp_cost = reader.get_short()
            sp_cost = reader.get_short()
            cast_time = reader.get_char()
            nature = SkillNature(reader.get_char())
            reader.get_char()
            type = SkillType(reader.get_three())
            element = Element(reader.get_char())
            element_power = reader.get_short()
            target_restrict = SkillTargetRestrict(reader.get_char())
            target_type = SkillTargetType(reader.get_char())
            target_time = reader.get_char()
            reader.get_char()
            max_skill_level = reader.get_short()
            min_damage = reader.get_short()
            max_damage = reader.get_short()
            accuracy = reader.get_short()
            evade = reader.get_short()
            armor = reader.get_short()
            return_damage = reader.get_char()
            hp_heal = reader.get_short()
            tp_heal = reader.get_short()
            sp_heal = reader.get_char()
            str = reader.get_short()
            intl = reader.get_short()
            wis = reader.get_short()
            agi = reader.get_short()
            con = reader.get_short()
            cha = reader.get_short()
            result = EsfRecord(name=name, chant=chant, icon_id=icon_id, graphic_id=graphic_id, tp_cost=tp_cost, sp_cost=sp_cost, cast_time=cast_time, nature=nature, type=type, element=element, element_power=element_power, target_restrict=target_restrict, target_type=target_type, target_time=target_time, max_skill_level=max_skill_level, min_damage=min_damage, max_damage=max_damage, accuracy=accuracy, evade=evade, armor=armor, return_damage=return_damage, hp_heal=hp_heal, tp_heal=tp_heal, sp_heal=sp_heal, str=str, intl=intl, wis=wis, agi=agi, con=con, cha=cha)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EsfRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, chant={repr(self._chant)}, icon_id={repr(self._icon_id)}, graphic_id={repr(self._graphic_id)}, tp_cost={repr(self._tp_cost)}, sp_cost={repr(self._sp_cost)}, cast_time={repr(self._cast_time)}, nature={repr(self._nature)}, type={repr(self._type)}, element={repr(self._element)}, element_power={repr(self._element_power)}, target_restrict={repr(self._target_restrict)}, target_type={repr(self._target_type)}, target_time={repr(self._target_time)}, max_skill_level={repr(self._max_skill_level)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)}, return_damage={repr(self._return_damage)}, hp_heal={repr(self._hp_heal)}, tp_heal={repr(self._tp_heal)}, sp_heal={repr(self._sp_heal)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)})"
