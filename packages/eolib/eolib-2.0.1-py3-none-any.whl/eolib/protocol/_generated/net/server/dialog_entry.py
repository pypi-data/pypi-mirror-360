# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .dialog_entry_type import DialogEntryType
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class DialogEntry:
    """
    An entry in a quest dialog
    """
    _byte_size: int = 0
    _entry_type: DialogEntryType
    _entry_type_data: 'DialogEntry.EntryTypeData'
    _line: str

    def __init__(self, *, entry_type: DialogEntryType, entry_type_data: 'DialogEntry.EntryTypeData' = None, line: str):
        """
        Create a new instance of DialogEntry.

        Args:
            entry_type (DialogEntryType): 
            entry_type_data (DialogEntry.EntryTypeData): Data associated with the `entry_type` field.
            line (str): 
        """
        self._entry_type = entry_type
        self._entry_type_data = entry_type_data
        self._line = line

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def entry_type(self) -> DialogEntryType:
        return self._entry_type

    @property
    def entry_type_data(self) -> 'DialogEntry.EntryTypeData':
        """
        DialogEntry.EntryTypeData: Data associated with the `entry_type` field.
        """
        return self._entry_type_data

    @property
    def line(self) -> str:
        return self._line

    @staticmethod
    def serialize(writer: EoWriter, data: "DialogEntry") -> None:
        """
        Serializes an instance of `DialogEntry` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (DialogEntry): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._entry_type is None:
                raise SerializationError("entry_type must be provided.")
            writer.add_short(int(data._entry_type))
            if data._entry_type == DialogEntryType.Link:
                if not isinstance(data._entry_type_data, DialogEntry.EntryTypeDataLink):
                    raise SerializationError("Expected entry_type_data to be type DialogEntry.EntryTypeDataLink for entry_type " + DialogEntryType(data._entry_type).name + ".")
                DialogEntry.EntryTypeDataLink.serialize(writer, data._entry_type_data)
            if data._line is None:
                raise SerializationError("line must be provided.")
            writer.add_string(data._line)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "DialogEntry":
        """
        Deserializes an instance of `DialogEntry` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            DialogEntry: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            entry_type = DialogEntryType(reader.get_short())
            entry_type_data: DialogEntry.EntryTypeData = None
            if entry_type == DialogEntryType.Link:
                entry_type_data = DialogEntry.EntryTypeDataLink.deserialize(reader)
            line = reader.get_string()
            result = DialogEntry(entry_type=entry_type, entry_type_data=entry_type_data, line=line)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"DialogEntry(byte_size={repr(self._byte_size)}, entry_type={repr(self._entry_type)}, entry_type_data={repr(self._entry_type_data)}, line={repr(self._line)})"

    EntryTypeData = Union['DialogEntry.EntryTypeDataLink', None]
    """
    Data associated with different values of the `entry_type` field.
    """

    class EntryTypeDataLink:
        """
        Data associated with entry_type value DialogEntryType.Link
        """
        _byte_size: int = 0
        _link_id: int

        def __init__(self, *, link_id: int):
            """
            Create a new instance of DialogEntry.EntryTypeDataLink.

            Args:
                link_id (int): (Value range is 0-64008.)
            """
            self._link_id = link_id

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def link_id(self) -> int:
            return self._link_id

        @staticmethod
        def serialize(writer: EoWriter, data: "DialogEntry.EntryTypeDataLink") -> None:
            """
            Serializes an instance of `DialogEntry.EntryTypeDataLink` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (DialogEntry.EntryTypeDataLink): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._link_id is None:
                    raise SerializationError("link_id must be provided.")
                writer.add_short(data._link_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "DialogEntry.EntryTypeDataLink":
            """
            Deserializes an instance of `DialogEntry.EntryTypeDataLink` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                DialogEntry.EntryTypeDataLink: The data to serialize.
            """
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                link_id = reader.get_short()
                result = DialogEntry.EntryTypeDataLink(link_id=link_id)
                result._byte_size = reader.position - reader_start_position
                return result
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"DialogEntry.EntryTypeDataLink(byte_size={repr(self._byte_size)}, link_id={repr(self._link_id)})"
