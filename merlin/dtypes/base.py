#
# Copyright (c) 2022, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from merlin.dtypes.registry import _dtype_registry


class ElementType(Enum):
    """
    Merlin DType base types

    Since a Merlin DType may describe a list, these are the either the types of
    scalars or the types of list elements.
    """

    Bool = "bool"
    Int = "int"
    UInt = "uint"
    Float = "float"
    String = "string"
    DateTime = "datetime"
    Object = "object"
    Unknown = "unknown"


class ElementUnit(Enum):
    """
    Dtype units, used only for datetime types

    Since a Merlin DType may describe a list, these are the either the units of
    scalars or the units of list elements.
    """

    Year = "year"
    Month = "month"
    Day = "day"
    Hour = "hour"
    Minute = "minute"
    Second = "second"
    Millisecond = "millisecond"
    Microsecond = "microsecond"
    Nanosecond = "nanosecond"


@dataclass(eq=True, frozen=True)
class DType:
    """
    Merlin dtypes are objects of this dataclass
    """

    name: str
    element_type: ElementType
    element_size: Optional[int] = None
    element_unit: Optional[ElementUnit] = None
    signed: Optional[bool] = None

    def to(self, mapping_name: str):
        """
        Convert this Merlin dtype to another framework's dtypes

        Parameters
        ----------
        mapping_name : str
            Name of the framework dtype mapping to apply

        Returns
        -------
        Any
            An external framework dtype object

        Raises
        ------
        ValueError
            If there is no registered mapping for the given framework name
        ValueError
            The registered mapping for the given framework name doesn't map
            this Merlin dtype to a framework dtype
        """
        try:
            mapping = _dtype_registry.mappings[mapping_name]
        except KeyError as exc:
            raise ValueError(
                f"Merlin doesn't have a registered dtype mapping for '{mapping_name}'. "
                "If you'd like to register a new dtype mapping, use `merlin.dtype.register()`. "
                "If you're expecting this mapping to already exist, has the library or package "
                "that defines the mapping been imported successfully?"
            ) from exc

        try:
            return mapping.from_merlin(self)
        except KeyError as exc:
            raise ValueError(
                f"The registered dtype mapping for {mapping_name} doesn't contain type {self.name}."
            ) from exc

    @property
    def to_numpy(self):
        return self.to("numpy")

    @property
    def to_python(self):
        return self.to("python")

    # These properties refer to a single scalar (potentially a list element)
    @property
    def is_integer(self):
        return self.element_type.value == "int"

    @property
    def is_float(self):
        return self.element_type.value == "float"
