# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class InnQuestionRecord:
    """
    Record of a question and answer that the player must answer to register citizenship with an inn
    """
    _byte_size: int = 0
    _question_length: int
    _question: str
    _answer_length: int
    _answer: str

    def __init__(self, *, question: str, answer: str):
        """
        Create a new instance of InnQuestionRecord.

        Args:
            question (str): (Length must be 252 or less.)
            answer (str): (Length must be 252 or less.)
        """
        self._question = question
        self._question_length = len(self._question)
        self._answer = answer
        self._answer_length = len(self._answer)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def question(self) -> str:
        return self._question

    @property
    def answer(self) -> str:
        return self._answer

    @staticmethod
    def serialize(writer: EoWriter, data: "InnQuestionRecord") -> None:
        """
        Serializes an instance of `InnQuestionRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (InnQuestionRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._question_length is None:
                raise SerializationError("question_length must be provided.")
            writer.add_char(data._question_length)
            if data._question is None:
                raise SerializationError("question must be provided.")
            if len(data._question) > 252:
                raise SerializationError(f"Expected length of question to be 252 or less, got {len(data._question)}.")
            writer.add_fixed_string(data._question, data._question_length, False)
            if data._answer_length is None:
                raise SerializationError("answer_length must be provided.")
            writer.add_char(data._answer_length)
            if data._answer is None:
                raise SerializationError("answer must be provided.")
            if len(data._answer) > 252:
                raise SerializationError(f"Expected length of answer to be 252 or less, got {len(data._answer)}.")
            writer.add_fixed_string(data._answer, data._answer_length, False)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "InnQuestionRecord":
        """
        Deserializes an instance of `InnQuestionRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            InnQuestionRecord: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            question_length = reader.get_char()
            question = reader.get_fixed_string(question_length, False)
            answer_length = reader.get_char()
            answer = reader.get_fixed_string(answer_length, False)
            result = InnQuestionRecord(question=question, answer=answer)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"InnQuestionRecord(byte_size={repr(self._byte_size)}, question={repr(self._question)}, answer={repr(self._answer)})"
