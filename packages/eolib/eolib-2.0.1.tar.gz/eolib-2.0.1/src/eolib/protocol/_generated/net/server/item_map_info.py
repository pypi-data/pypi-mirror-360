# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemMapInfo:
    """
    Information about a nearby item on the ground
    """
    _byte_size: int = 0
    _uid: int
    _id: int
    _coords: Coords
    _amount: int

    def __init__(self, *, uid: int, id: int, coords: Coords, amount: int):
        """
        Create a new instance of ItemMapInfo.

        Args:
            uid (int): (Value range is 0-64008.)
            id (int): (Value range is 0-64008.)
            coords (Coords): 
            amount (int): (Value range is 0-16194276.)
        """
        self._uid = uid
        self._id = id
        self._coords = coords
        self._amount = amount

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def id(self) -> int:
        return self._id

    @property
    def coords(self) -> Coords:
        return self._coords

    @property
    def amount(self) -> int:
        return self._amount

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemMapInfo") -> None:
        """
        Serializes an instance of `ItemMapInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemMapInfo): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._uid is None:
                raise SerializationError("uid must be provided.")
            writer.add_short(data._uid)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_three(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemMapInfo":
        """
        Deserializes an instance of `ItemMapInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemMapInfo: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            uid = reader.get_short()
            id = reader.get_short()
            coords = Coords.deserialize(reader)
            amount = reader.get_three()
            result = ItemMapInfo(uid=uid, id=id, coords=coords, amount=amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemMapInfo(byte_size={repr(self._byte_size)}, uid={repr(self._uid)}, id={repr(self._id)}, coords={repr(self._coords)}, amount={repr(self._amount)})"
