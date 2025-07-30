from typing import Callable, Dict, Union
from uuid import UUID
from maleo_metadata.enums.gender import MaleoMetadataGenderEnums


class MaleoMetadataGenderConstants:
    IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
        MaleoMetadataGenderEnums.IdentifierType, Callable[[str], Union[int, str, UUID]]
    ] = {
        MaleoMetadataGenderEnums.IdentifierType.ID: int,
        MaleoMetadataGenderEnums.IdentifierType.UUID: UUID,
        MaleoMetadataGenderEnums.IdentifierType.KEY: str,
        MaleoMetadataGenderEnums.IdentifierType.NAME: str,
    }
