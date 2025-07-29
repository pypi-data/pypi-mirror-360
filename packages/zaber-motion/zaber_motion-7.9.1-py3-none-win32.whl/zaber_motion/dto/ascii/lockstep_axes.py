# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class LockstepAxes:
    """
    The axis numbers of a lockstep group.
    """

    axis_1: int
    """
    The axis number used to set the first axis.
    """

    axis_2: int
    """
    The axis number used to set the second axis.
    """

    axis_3: int
    """
    The axis number used to set the third axis.
    """

    axis_4: int
    """
    The axis number used to set the fourth axis.
    """

    @staticmethod
    def zero_values() -> 'LockstepAxes':
        return LockstepAxes(
            axis_1=0,
            axis_2=0,
            axis_3=0,
            axis_4=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepAxes':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepAxes.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axis1': int(self.axis_1),
            'axis2': int(self.axis_2),
            'axis3': int(self.axis_3),
            'axis4': int(self.axis_4),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepAxes':
        return LockstepAxes(
            axis_1=data.get('axis1'),  # type: ignore
            axis_2=data.get('axis2'),  # type: ignore
            axis_3=data.get('axis3'),  # type: ignore
            axis_4=data.get('axis4'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_1 is None:
            raise ValueError(f'Property "Axis1" of "LockstepAxes" is None.')

        if not isinstance(self.axis_1, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis1" of "LockstepAxes" is not a number.')

        if int(self.axis_1) != self.axis_1:
            raise ValueError(f'Property "Axis1" of "LockstepAxes" is not integer value.')

        if self.axis_2 is None:
            raise ValueError(f'Property "Axis2" of "LockstepAxes" is None.')

        if not isinstance(self.axis_2, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis2" of "LockstepAxes" is not a number.')

        if int(self.axis_2) != self.axis_2:
            raise ValueError(f'Property "Axis2" of "LockstepAxes" is not integer value.')

        if self.axis_3 is None:
            raise ValueError(f'Property "Axis3" of "LockstepAxes" is None.')

        if not isinstance(self.axis_3, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis3" of "LockstepAxes" is not a number.')

        if int(self.axis_3) != self.axis_3:
            raise ValueError(f'Property "Axis3" of "LockstepAxes" is not integer value.')

        if self.axis_4 is None:
            raise ValueError(f'Property "Axis4" of "LockstepAxes" is None.')

        if not isinstance(self.axis_4, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis4" of "LockstepAxes" is not a number.')

        if int(self.axis_4) != self.axis_4:
            raise ValueError(f'Property "Axis4" of "LockstepAxes" is not integer value.')
