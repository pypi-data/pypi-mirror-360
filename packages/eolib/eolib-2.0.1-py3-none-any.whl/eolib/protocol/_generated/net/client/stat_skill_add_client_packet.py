# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .train_type import TrainType
from .stat_id import StatId
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillAddClientPacket(Packet):
    """
    Spending a stat point on a stat or skill
    """
    _byte_size: int = 0
    _action_type: TrainType
    _action_type_data: 'StatSkillAddClientPacket.ActionTypeData'

    def __init__(self, *, action_type: TrainType, action_type_data: 'StatSkillAddClientPacket.ActionTypeData' = None):
        """
        Create a new instance of StatSkillAddClientPacket.

        Args:
            action_type (TrainType): 
            action_type_data (StatSkillAddClientPacket.ActionTypeData): Data associated with the `action_type` field.
        """
        self._action_type = action_type
        self._action_type_data = action_type_data

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def action_type(self) -> TrainType:
        return self._action_type

    @property
    def action_type_data(self) -> 'StatSkillAddClientPacket.ActionTypeData':
        """
        StatSkillAddClientPacket.ActionTypeData: Data associated with the `action_type` field.
        """
        return self._action_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.StatSkill

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Add

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillAddClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillAddClientPacket") -> None:
        """
        Serializes an instance of `StatSkillAddClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillAddClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._action_type is None:
                raise SerializationError("action_type must be provided.")
            writer.add_char(int(data._action_type))
            if data._action_type == TrainType.Stat:
                if not isinstance(data._action_type_data, StatSkillAddClientPacket.ActionTypeDataStat):
                    raise SerializationError("Expected action_type_data to be type StatSkillAddClientPacket.ActionTypeDataStat for action_type " + TrainType(data._action_type).name + ".")
                StatSkillAddClientPacket.ActionTypeDataStat.serialize(writer, data._action_type_data)
            elif data._action_type == TrainType.Skill:
                if not isinstance(data._action_type_data, StatSkillAddClientPacket.ActionTypeDataSkill):
                    raise SerializationError("Expected action_type_data to be type StatSkillAddClientPacket.ActionTypeDataSkill for action_type " + TrainType(data._action_type).name + ".")
                StatSkillAddClientPacket.ActionTypeDataSkill.serialize(writer, data._action_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillAddClientPacket":
        """
        Deserializes an instance of `StatSkillAddClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillAddClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            action_type = TrainType(reader.get_char())
            action_type_data: StatSkillAddClientPacket.ActionTypeData = None
            if action_type == TrainType.Stat:
                action_type_data = StatSkillAddClientPacket.ActionTypeDataStat.deserialize(reader)
            elif action_type == TrainType.Skill:
                action_type_data = StatSkillAddClientPacket.ActionTypeDataSkill.deserialize(reader)
            result = StatSkillAddClientPacket(action_type=action_type, action_type_data=action_type_data)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillAddClientPacket(byte_size={repr(self._byte_size)}, action_type={repr(self._action_type)}, action_type_data={repr(self._action_type_data)})"

    ActionTypeData = Union['StatSkillAddClientPacket.ActionTypeDataStat', 'StatSkillAddClientPacket.ActionTypeDataSkill', None]
    """
    Data associated with different values of the `action_type` field.
    """

    class ActionTypeDataStat:
        """
        Data associated with action_type value TrainType.Stat
        """
        _byte_size: int = 0
        _stat_id: StatId

        def __init__(self, *, stat_id: StatId):
            """
            Create a new instance of StatSkillAddClientPacket.ActionTypeDataStat.

            Args:
                stat_id (StatId): 
            """
            self._stat_id = stat_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def stat_id(self) -> StatId:
            return self._stat_id

        @staticmethod
        def serialize(writer: EoWriter, data: "StatSkillAddClientPacket.ActionTypeDataStat") -> None:
            """
            Serializes an instance of `StatSkillAddClientPacket.ActionTypeDataStat` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (StatSkillAddClientPacket.ActionTypeDataStat): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._stat_id is None:
                    raise SerializationError("stat_id must be provided.")
                writer.add_short(int(data._stat_id))
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "StatSkillAddClientPacket.ActionTypeDataStat":
            """
            Deserializes an instance of `StatSkillAddClientPacket.ActionTypeDataStat` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                StatSkillAddClientPacket.ActionTypeDataStat: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                stat_id = StatId(reader.get_short())
                result = StatSkillAddClientPacket.ActionTypeDataStat(stat_id=stat_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"StatSkillAddClientPacket.ActionTypeDataStat(byte_size={repr(self._byte_size)}, stat_id={repr(self._stat_id)})"

    class ActionTypeDataSkill:
        """
        Data associated with action_type value TrainType.Skill
        """
        _byte_size: int = 0
        _spell_id: int

        def __init__(self, *, spell_id: int):
            """
            Create a new instance of StatSkillAddClientPacket.ActionTypeDataSkill.

            Args:
                spell_id (int): (Value range is 0-64008.)
            """
            self._spell_id = spell_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def spell_id(self) -> int:
            return self._spell_id

        @staticmethod
        def serialize(writer: EoWriter, data: "StatSkillAddClientPacket.ActionTypeDataSkill") -> None:
            """
            Serializes an instance of `StatSkillAddClientPacket.ActionTypeDataSkill` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (StatSkillAddClientPacket.ActionTypeDataSkill): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._spell_id is None:
                    raise SerializationError("spell_id must be provided.")
                writer.add_short(data._spell_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "StatSkillAddClientPacket.ActionTypeDataSkill":
            """
            Deserializes an instance of `StatSkillAddClientPacket.ActionTypeDataSkill` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                StatSkillAddClientPacket.ActionTypeDataSkill: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                spell_id = reader.get_short()
                result = StatSkillAddClientPacket.ActionTypeDataSkill(spell_id=spell_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"StatSkillAddClientPacket.ActionTypeDataSkill(byte_size={repr(self._byte_size)}, spell_id={repr(self._spell_id)})"
