# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Version:
    """
    Client version
    """
    _byte_size: int = 0
    _major: int
    _minor: int
    _patch: int

    def __init__(self, *, major: int, minor: int, patch: int):
        """
        Create a new instance of Version.

        Args:
            major (int): (Value range is 0-252.)
            minor (int): (Value range is 0-252.)
            patch (int): (Value range is 0-252.)
        """
        self._major = major
        self._minor = minor
        self._patch = patch

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return self._patch

    @staticmethod
    def serialize(writer: EoWriter, data: "Version") -> None:
        """
        Serializes an instance of `Version` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Version): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._major is None:
                raise SerializationError("major must be provided.")
            writer.add_char(data._major)
            if data._minor is None:
                raise SerializationError("minor must be provided.")
            writer.add_char(data._minor)
            if data._patch is None:
                raise SerializationError("patch must be provided.")
            writer.add_char(data._patch)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Version":
        """
        Deserializes an instance of `Version` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Version: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            major = reader.get_char()
            minor = reader.get_char()
            patch = reader.get_char()
            result = Version(major=major, minor=minor, patch=patch)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Version(byte_size={repr(self._byte_size)}, major={repr(self._major)}, minor={repr(self._minor)}, patch={repr(self._patch)})"
