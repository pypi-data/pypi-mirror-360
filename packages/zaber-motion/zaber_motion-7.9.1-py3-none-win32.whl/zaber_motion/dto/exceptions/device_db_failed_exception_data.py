# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class DeviceDbFailedExceptionData:
    """
    Contains additional data for a DeviceDbFailedException.
    """

    code: str
    """
    Code describing type of the error.
    """

    @staticmethod
    def zero_values() -> 'DeviceDbFailedExceptionData':
        return DeviceDbFailedExceptionData(
            code="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceDbFailedExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceDbFailedExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': str(self.code or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceDbFailedExceptionData':
        return DeviceDbFailedExceptionData(
            code=data.get('code'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.code is not None:
            if not isinstance(self.code, str):
                raise ValueError(f'Property "Code" of "DeviceDbFailedExceptionData" is not a string.')
