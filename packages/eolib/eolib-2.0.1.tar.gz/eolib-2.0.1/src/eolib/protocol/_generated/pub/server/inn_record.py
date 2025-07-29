# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .inn_question_record import InnQuestionRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class InnRecord:
    """
    Record of Inn data in an Endless Inn File
    """
    _byte_size: int = 0
    _behavior_id: int
    _name_length: int
    _name: str
    _spawn_map: int
    _spawn_x: int
    _spawn_y: int
    _sleep_map: int
    _sleep_x: int
    _sleep_y: int
    _alternate_spawn_enabled: bool
    _alternate_spawn_map: int
    _alternate_spawn_x: int
    _alternate_spawn_y: int
    _questions: tuple[InnQuestionRecord, ...]

    def __init__(self, *, behavior_id: int, name: str, spawn_map: int, spawn_x: int, spawn_y: int, sleep_map: int, sleep_x: int, sleep_y: int, alternate_spawn_enabled: bool, alternate_spawn_map: int, alternate_spawn_x: int, alternate_spawn_y: int, questions: Iterable[InnQuestionRecord]):
        """
        Create a new instance of InnRecord.

        Args:
            behavior_id (int): Behavior ID of the NPC that runs the inn. 0 for default inn (Value range is 0-64008.)
            name (str): (Length must be 252 or less.)
            spawn_map (int): ID of the map the player is sent to after respawning (Value range is 0-64008.)
            spawn_x (int): X coordinate of the map the player is sent to after respawning (Value range is 0-252.)
            spawn_y (int): Y coordinate of the map the player is sent to after respawning (Value range is 0-252.)
            sleep_map (int): ID of the map the player is sent to after sleeping at the inn (Value range is 0-64008.)
            sleep_x (int): X coordinate of the map the player is sent to after sleeping at the inn (Value range is 0-252.)
            sleep_y (int): Y coordinate of the map the player is sent to after sleeping at the inn (Value range is 0-252.)
            alternate_spawn_enabled (bool): Flag for an alternate spawn point. If true, the server will use this alternate spawn map, x, and, y based on some other condition.  In the official server, this is used to respawn new characters on the noob island until they reach a certain level.
            alternate_spawn_map (int): (Value range is 0-64008.)
            alternate_spawn_x (int): (Value range is 0-252.)
            alternate_spawn_y (int): (Value range is 0-252.)
            questions (Iterable[InnQuestionRecord]): (Length must be `3`.)
        """
        self._behavior_id = behavior_id
        self._name = name
        self._name_length = len(self._name)
        self._spawn_map = spawn_map
        self._spawn_x = spawn_x
        self._spawn_y = spawn_y
        self._sleep_map = sleep_map
        self._sleep_x = sleep_x
        self._sleep_y = sleep_y
        self._alternate_spawn_enabled = alternate_spawn_enabled
        self._alternate_spawn_map = alternate_spawn_map
        self._alternate_spawn_x = alternate_spawn_x
        self._alternate_spawn_y = alternate_spawn_y
        self._questions = tuple(questions)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        """
        Behavior ID of the NPC that runs the inn. 0 for default inn
        """
        return self._behavior_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def spawn_map(self) -> int:
        """
        ID of the map the player is sent to after respawning
        """
        return self._spawn_map

    @property
    def spawn_x(self) -> int:
        """
        X coordinate of the map the player is sent to after respawning
        """
        return self._spawn_x

    @property
    def spawn_y(self) -> int:
        """
        Y coordinate of the map the player is sent to after respawning
        """
        return self._spawn_y

    @property
    def sleep_map(self) -> int:
        """
        ID of the map the player is sent to after sleeping at the inn
        """
        return self._sleep_map

    @property
    def sleep_x(self) -> int:
        """
        X coordinate of the map the player is sent to after sleeping at the inn
        """
        return self._sleep_x

    @property
    def sleep_y(self) -> int:
        """
        Y coordinate of the map the player is sent to after sleeping at the inn
        """
        return self._sleep_y

    @property
    def alternate_spawn_enabled(self) -> bool:
        """
        Flag for an alternate spawn point. If true, the server will use this alternate spawn
        map, x, and, y based on some other condition.

        In the official server, this is used to respawn new characters on the noob island
        until they reach a certain level.
        """
        return self._alternate_spawn_enabled

    @property
    def alternate_spawn_map(self) -> int:
        return self._alternate_spawn_map

    @property
    def alternate_spawn_x(self) -> int:
        return self._alternate_spawn_x

    @property
    def alternate_spawn_y(self) -> int:
        return self._alternate_spawn_y

    @property
    def questions(self) -> tuple[InnQuestionRecord, ...]:
        return self._questions

    @staticmethod
    def serialize(writer: EoWriter, data: "InnRecord") -> None:
        """
        Serializes an instance of `InnRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (InnRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._spawn_map is None:
                raise SerializationError("spawn_map must be provided.")
            writer.add_short(data._spawn_map)
            if data._spawn_x is None:
                raise SerializationError("spawn_x must be provided.")
            writer.add_char(data._spawn_x)
            if data._spawn_y is None:
                raise SerializationError("spawn_y must be provided.")
            writer.add_char(data._spawn_y)
            if data._sleep_map is None:
                raise SerializationError("sleep_map must be provided.")
            writer.add_short(data._sleep_map)
            if data._sleep_x is None:
                raise SerializationError("sleep_x must be provided.")
            writer.add_char(data._sleep_x)
            if data._sleep_y is None:
                raise SerializationError("sleep_y must be provided.")
            writer.add_char(data._sleep_y)
            if data._alternate_spawn_enabled is None:
                raise SerializationError("alternate_spawn_enabled must be provided.")
            writer.add_char(1 if data._alternate_spawn_enabled else 0)
            if data._alternate_spawn_map is None:
                raise SerializationError("alternate_spawn_map must be provided.")
            writer.add_short(data._alternate_spawn_map)
            if data._alternate_spawn_x is None:
                raise SerializationError("alternate_spawn_x must be provided.")
            writer.add_char(data._alternate_spawn_x)
            if data._alternate_spawn_y is None:
                raise SerializationError("alternate_spawn_y must be provided.")
            writer.add_char(data._alternate_spawn_y)
            if data._questions is None:
                raise SerializationError("questions must be provided.")
            if len(data._questions) != 3:
                raise SerializationError(f"Expected length of questions to be exactly 3, got {len(data._questions)}.")
            for i in range(3):
                InnQuestionRecord.serialize(writer, data._questions[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "InnRecord":
        """
        Deserializes an instance of `InnRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            InnRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            behavior_id = reader.get_short()
            name_length = reader.get_char()
            name = reader.get_fixed_string(name_length, False)
            spawn_map = reader.get_short()
            spawn_x = reader.get_char()
            spawn_y = reader.get_char()
            sleep_map = reader.get_short()
            sleep_x = reader.get_char()
            sleep_y = reader.get_char()
            alternate_spawn_enabled = reader.get_char() != 0
            alternate_spawn_map = reader.get_short()
            alternate_spawn_x = reader.get_char()
            alternate_spawn_y = reader.get_char()
            questions = []
            for i in range(3):
                questions.append(InnQuestionRecord.deserialize(reader))
            result = InnRecord(behavior_id=behavior_id, name=name, spawn_map=spawn_map, spawn_x=spawn_x, spawn_y=spawn_y, sleep_map=sleep_map, sleep_x=sleep_x, sleep_y=sleep_y, alternate_spawn_enabled=alternate_spawn_enabled, alternate_spawn_map=alternate_spawn_map, alternate_spawn_x=alternate_spawn_x, alternate_spawn_y=alternate_spawn_y, questions=questions)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"InnRecord(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, name={repr(self._name)}, spawn_map={repr(self._spawn_map)}, spawn_x={repr(self._spawn_x)}, spawn_y={repr(self._spawn_y)}, sleep_map={repr(self._sleep_map)}, sleep_x={repr(self._sleep_x)}, sleep_y={repr(self._sleep_y)}, alternate_spawn_enabled={repr(self._alternate_spawn_enabled)}, alternate_spawn_map={repr(self._alternate_spawn_map)}, alternate_spawn_x={repr(self._alternate_spawn_x)}, alternate_spawn_y={repr(self._alternate_spawn_y)}, questions={repr(self._questions)})"
