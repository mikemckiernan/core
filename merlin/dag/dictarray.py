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
from typing import Dict, Optional

import numpy as np

import merlin.dtypes as md
from merlin.core.protocols import SeriesLike


class Column(SeriesLike):
    """
    A simple wrapper around an array of values
    """

    def __init__(self, values, dtype=None):
        super().__init__()

        self.values = values
        self.dtype = md.dtype(dtype or values.dtype)

    def __getitem__(self, index):
        return self.values[index]

    def __eq__(self, other):
        return all(self.values == other.values) and self.dtype == other.dtype


class DictArray:
    """
    A simple dataframe-like wrapper around a dictionary of values. Matches the Transformable
    protocol for (limited) interchangeability with actual dataframes in Merlin DAGs.
    """

    def __init__(self, values: Optional[Dict] = None, dtypes: Optional[Dict] = None):
        super().__init__()

        values = values or {}

        array_values = {}
        for key, value in values.items():
            array_values[key] = np.array(value) if isinstance(value, list) else value

        self.arrays = array_values
        self.dtypes = dtypes or self._dtypes_from_values(self.arrays)

    @property
    def columns(self):
        return list(self.arrays.keys())

    def __len__(self):
        return len(self.arrays)

    def __iter__(self):
        return iter(self.arrays)

    def __eq__(self, other):
        return self.arrays == other.values and self.dtypes == other.dtypes

    def __setitem__(self, key, value):
        self.arrays[key] = value
        self.dtypes[key] = value.dtype

    def __getitem__(self, key):
        if isinstance(key, list):
            return DictArray(
                values={k: self.arrays[k] for k in key},
                dtypes={k: self.dtypes[k] for k in key},
            )
        else:
            return self.arrays[key]

    def __delitem__(self, key):
        del self.arrays[key]
        del self.dtypes[key]

    def _grab_keys(self, source, keys):
        return {k: source[k] for k in keys}

    def keys(self):
        """
        Shortcut to get the dictionary keys
        """
        return self.arrays.keys()

    def items(self):
        """
        Shortcut to get the dictionary items
        """
        return self.arrays.items()

    def values(self):
        """
        Shortcut to get the dictionary values
        """
        return self.arrays.values()

    def update(self, other):
        """
        Shortcut to update the dictionary items
        """
        self.arrays.update(other)
        self.dtypes = self._dtypes_from_values(self.arrays)

    def copy(self):
        """
        Create a new DictArray with the same data and dtypes
        """
        return DictArray(self.arrays.copy(), self.dtypes.copy())

    def _dtypes_from_values(self, values):
        return {key: value.dtype for key, value in values.items()}
