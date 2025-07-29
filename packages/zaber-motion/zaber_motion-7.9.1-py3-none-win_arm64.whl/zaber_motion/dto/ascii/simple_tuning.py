# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from .servo_tuning_param import ServoTuningParam


@dataclass
class SimpleTuning:
    """
    The masses and parameters last used by simple tuning.
    """

    is_used: bool
    """
    Whether the tuning returned is currently in use by this paramset,
    or if it has been overwritten by a later change.
    """

    is_set: bool
    """
    If this paramset has been tuned using the simple tuning method, whether or not it's currently in use.
    """

    load_mass: float
    """
    The mass of the load in kg, excluding the mass of the carriage.
    """

    tuning_params: List[ServoTuningParam]
    """
    The parameters used by simple tuning.
    """

    carriage_mass: Optional[float] = None
    """
    The mass of the carriage in kg.
    """

    motor_inertia: Optional[float] = None
    """
    The mass of the carriage in kg.
    """

    @staticmethod
    def zero_values() -> 'SimpleTuning':
        return SimpleTuning(
            is_used=False,
            is_set=False,
            carriage_mass=None,
            motor_inertia=None,
            load_mass=0,
            tuning_params=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SimpleTuning':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SimpleTuning.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'isUsed': bool(self.is_used),
            'isSet': bool(self.is_set),
            'carriageMass': float(self.carriage_mass) if self.carriage_mass is not None else None,
            'motorInertia': float(self.motor_inertia) if self.motor_inertia is not None else None,
            'loadMass': float(self.load_mass),
            'tuningParams': [item.to_dict() for item in self.tuning_params] if self.tuning_params is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SimpleTuning':
        return SimpleTuning(
            is_used=data.get('isUsed'),  # type: ignore
            is_set=data.get('isSet'),  # type: ignore
            carriage_mass=data.get('carriageMass'),  # type: ignore
            motor_inertia=data.get('motorInertia'),  # type: ignore
            load_mass=data.get('loadMass'),  # type: ignore
            tuning_params=[ServoTuningParam.from_dict(item) for item in data.get('tuningParams')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.carriage_mass is not None:
            if not isinstance(self.carriage_mass, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "CarriageMass" of "SimpleTuning" is not a number.')

        if self.motor_inertia is not None:
            if not isinstance(self.motor_inertia, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "MotorInertia" of "SimpleTuning" is not a number.')

        if self.load_mass is None:
            raise ValueError(f'Property "LoadMass" of "SimpleTuning" is None.')

        if not isinstance(self.load_mass, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LoadMass" of "SimpleTuning" is not a number.')

        if self.tuning_params is not None:
            if not isinstance(self.tuning_params, Iterable):
                raise ValueError('Property "TuningParams" of "SimpleTuning" is not iterable.')

            for i, tuning_params_item in enumerate(self.tuning_params):
                if tuning_params_item is None:
                    raise ValueError(f'Item {i} in property "TuningParams" of "SimpleTuning" is None.')

                if not isinstance(tuning_params_item, ServoTuningParam):
                    raise ValueError(f'Item {i} in property "TuningParams" of "SimpleTuning" is not an instance of "ServoTuningParam".')

                tuning_params_item.validate()
