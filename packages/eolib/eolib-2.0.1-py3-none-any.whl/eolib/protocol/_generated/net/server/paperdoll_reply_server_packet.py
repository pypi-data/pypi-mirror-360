# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .equipment_paperdoll import EquipmentPaperdoll
from .character_icon import CharacterIcon
from .character_details import CharacterDetails
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PaperdollReplyServerPacket(Packet):
    """
    Reply to requesting a paperdoll
    """
    _byte_size: int = 0
    _details: CharacterDetails
    _equipment: EquipmentPaperdoll
    _icon: CharacterIcon

    def __init__(self, *, details: CharacterDetails, equipment: EquipmentPaperdoll, icon: CharacterIcon):
        """
        Create a new instance of PaperdollReplyServerPacket.

        Args:
            details (CharacterDetails): 
            equipment (EquipmentPaperdoll): 
            icon (CharacterIcon): 
        """
        self._details = details
        self._equipment = equipment
        self._icon = icon

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def details(self) -> CharacterDetails:
        return self._details

    @property
    def equipment(self) -> EquipmentPaperdoll:
        return self._equipment

    @property
    def icon(self) -> CharacterIcon:
        return self._icon

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Paperdoll

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PaperdollReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PaperdollReplyServerPacket") -> None:
        """
        Serializes an instance of `PaperdollReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PaperdollReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._details is None:
                raise SerializationError("details must be provided.")
            CharacterDetails.serialize(writer, data._details)
            if data._equipment is None:
                raise SerializationError("equipment must be provided.")
            EquipmentPaperdoll.serialize(writer, data._equipment)
            if data._icon is None:
                raise SerializationError("icon must be provided.")
            writer.add_char(int(data._icon))
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PaperdollReplyServerPacket":
        """
        Deserializes an instance of `PaperdollReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PaperdollReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            details = CharacterDetails.deserialize(reader)
            equipment = EquipmentPaperdoll.deserialize(reader)
            icon = CharacterIcon(reader.get_char())
            reader.chunked_reading_mode = False
            result = PaperdollReplyServerPacket(details=details, equipment=equipment, icon=icon)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PaperdollReplyServerPacket(byte_size={repr(self._byte_size)}, details={repr(self._details)}, equipment={repr(self._equipment)}, icon={repr(self._icon)})"
