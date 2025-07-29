# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.servo_tuning_paramset import ServoTuningParamset
from ..ascii.servo_tuning_param import ServoTuningParam
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class SetSimpleTuning:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    paramset: ServoTuningParamset = next(first for first in ServoTuningParamset)

    load_mass: float = 0

    load_mass_units: UnitsAndLiterals = Units.NATIVE

    carriage_mass_units: UnitsAndLiterals = Units.NATIVE

    motor_inertia_units: UnitsAndLiterals = Units.NATIVE

    tuning_params: List[ServoTuningParam] = field(default_factory=list)

    carriage_mass: Optional[float] = None

    motor_inertia: Optional[float] = None

    @staticmethod
    def zero_values() -> 'SetSimpleTuning':
        return SetSimpleTuning(
            interface_id=0,
            device=0,
            axis=0,
            paramset=next(first for first in ServoTuningParamset),
            load_mass=0,
            load_mass_units=Units.NATIVE,
            carriage_mass=None,
            carriage_mass_units=Units.NATIVE,
            motor_inertia=None,
            motor_inertia_units=Units.NATIVE,
            tuning_params=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetSimpleTuning':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetSimpleTuning.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'paramset': self.paramset.value,
            'loadMass': float(self.load_mass),
            'loadMassUnits': units_from_literals(self.load_mass_units).value,
            'carriageMass': float(self.carriage_mass) if self.carriage_mass is not None else None,
            'carriageMassUnits': units_from_literals(self.carriage_mass_units).value,
            'motorInertia': float(self.motor_inertia) if self.motor_inertia is not None else None,
            'motorInertiaUnits': units_from_literals(self.motor_inertia_units).value,
            'tuningParams': [item.to_dict() for item in self.tuning_params] if self.tuning_params is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetSimpleTuning':
        return SetSimpleTuning(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            paramset=ServoTuningParamset(data.get('paramset')),  # type: ignore
            load_mass=data.get('loadMass'),  # type: ignore
            load_mass_units=Units(data.get('loadMassUnits')),  # type: ignore
            carriage_mass=data.get('carriageMass'),  # type: ignore
            carriage_mass_units=Units(data.get('carriageMassUnits')),  # type: ignore
            motor_inertia=data.get('motorInertia'),  # type: ignore
            motor_inertia_units=Units(data.get('motorInertiaUnits')),  # type: ignore
            tuning_params=[ServoTuningParam.from_dict(item) for item in data.get('tuningParams')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "SetSimpleTuning" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "SetSimpleTuning" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "SetSimpleTuning" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "SetSimpleTuning" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "SetSimpleTuning" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "SetSimpleTuning" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "SetSimpleTuning" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "SetSimpleTuning" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "SetSimpleTuning" is not integer value.')

        if self.paramset is None:
            raise ValueError(f'Property "Paramset" of "SetSimpleTuning" is None.')

        if not isinstance(self.paramset, ServoTuningParamset):
            raise ValueError(f'Property "Paramset" of "SetSimpleTuning" is not an instance of "ServoTuningParamset".')

        if self.load_mass is None:
            raise ValueError(f'Property "LoadMass" of "SetSimpleTuning" is None.')

        if not isinstance(self.load_mass, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LoadMass" of "SetSimpleTuning" is not a number.')

        if self.load_mass_units is None:
            raise ValueError(f'Property "LoadMassUnits" of "SetSimpleTuning" is None.')

        if not isinstance(self.load_mass_units, (Units, str)):
            raise ValueError(f'Property "LoadMassUnits" of "SetSimpleTuning" is not Units.')

        if self.carriage_mass is not None:
            if not isinstance(self.carriage_mass, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "CarriageMass" of "SetSimpleTuning" is not a number.')

        if self.carriage_mass_units is None:
            raise ValueError(f'Property "CarriageMassUnits" of "SetSimpleTuning" is None.')

        if not isinstance(self.carriage_mass_units, (Units, str)):
            raise ValueError(f'Property "CarriageMassUnits" of "SetSimpleTuning" is not Units.')

        if self.motor_inertia is not None:
            if not isinstance(self.motor_inertia, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "MotorInertia" of "SetSimpleTuning" is not a number.')

        if self.motor_inertia_units is None:
            raise ValueError(f'Property "MotorInertiaUnits" of "SetSimpleTuning" is None.')

        if not isinstance(self.motor_inertia_units, (Units, str)):
            raise ValueError(f'Property "MotorInertiaUnits" of "SetSimpleTuning" is not Units.')

        if self.tuning_params is not None:
            if not isinstance(self.tuning_params, Iterable):
                raise ValueError('Property "TuningParams" of "SetSimpleTuning" is not iterable.')

            for i, tuning_params_item in enumerate(self.tuning_params):
                if tuning_params_item is None:
                    raise ValueError(f'Item {i} in property "TuningParams" of "SetSimpleTuning" is None.')

                if not isinstance(tuning_params_item, ServoTuningParam):
                    raise ValueError(f'Item {i} in property "TuningParams" of "SetSimpleTuning" is not an instance of "ServoTuningParam".')

                tuning_params_item.validate()
