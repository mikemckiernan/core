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
import pandas as pd
import pytest

import merlin.dtypes as md
from merlin.schema import ColumnSchema
from merlin.schema.schema import ColumnQuantity
from merlin.schema.tags import Tags, TagSet


@pytest.mark.parametrize("d_types", [md.float32, md.float64, md.uint32, md.uint64])
def test_dtype_column_schema(d_types):
    column = ColumnSchema("name", tags=[], properties={}, dtype=d_types)
    assert column.dtype == d_types


@pytest.mark.parametrize("external_dtype, merlin_dtype", [(pd.StringDtype, md.string)])
def test_column_schema_normalizes_dtypes(external_dtype, merlin_dtype):
    column = ColumnSchema("name", tags=[], properties={}, dtype=external_dtype)
    assert column.dtype == merlin_dtype


@pytest.mark.parametrize(
    ["column_schema_a", "column_schema_b"],
    [
        [ColumnSchema("col"), ColumnSchema("col")],
        [ColumnSchema("col_b", tags=["tag-1"]), ColumnSchema("col_b", tags=["tag-1"])],
        [
            ColumnSchema("col", dtype=md.int32, properties={"domain": {"min": 0, "max": 8}}),
            ColumnSchema("col", dtype=md.int32, properties={"domain": {"min": 0, "max": 8}}),
        ],
        [
            ColumnSchema(
                "col",
                dtype=md.float32,
                tags=["tag-2", Tags.CONTINUOUS],
                properties={"p1": "prop-1"},
            ),
            ColumnSchema(
                "col",
                dtype=md.float32,
                tags=["tag-2", Tags.CONTINUOUS],
                properties={"p1": "prop-1"},
            ),
        ],
    ],
)
def test_equal(column_schema_a, column_schema_b):
    assert column_schema_a == column_schema_b
    assert column_schema_a.name == column_schema_b.name
    assert column_schema_a.dtype == column_schema_b.dtype
    assert column_schema_a.tags == column_schema_b.tags
    assert column_schema_a.properties == column_schema_b.properties


@pytest.mark.parametrize(
    ["column_schema_a", "column_schema_b"],
    [
        [ColumnSchema("col_a"), ColumnSchema("col_b")],
        [ColumnSchema("name"), ColumnSchema("name", tags=["tags-1"])],
        [ColumnSchema("name"), ColumnSchema("name", properties={"p1": "prop-1"})],
        [
            ColumnSchema("name", tags=["tag-1"]),
            ColumnSchema("name", properties={"p1": "prop-1"}),
        ],
        [
            ColumnSchema("name", tags=["tag-1"], properties={"p1": "prop-1"}),
            ColumnSchema("name", properties={"p1": "prop-1"}),
        ],
    ],
)
def test_not_equal(column_schema_a, column_schema_b):
    assert column_schema_a != column_schema_b


@pytest.mark.parametrize(
    ["column_schema", "name", "expected_column_schema"],
    [
        [ColumnSchema("col_a"), "col_b", ColumnSchema("col_b")],
        [ColumnSchema("feat", tags=["tag-1"]), "seq", ColumnSchema("seq", tags=["tag-1"])],
        [
            ColumnSchema(
                "feat",
                tags=["tag-1"],
                dtype=md.float32,
                properties={"domain": {"min": 0.0, "max": 6.0}},
            ),
            "feat_b",
            ColumnSchema(
                "feat_b",
                tags=["tag-1"],
                dtype=md.float32,
                properties={"domain": {"min": 0.0, "max": 6.0}},
            ),
        ],
    ],
)
def test_with_name(column_schema, name, expected_column_schema):
    assert column_schema.with_name(name) == expected_column_schema


@pytest.mark.parametrize(
    ["column_schema", "tags", "expected_column_schema"],
    [
        [
            ColumnSchema("example", tags=["tag-1"], properties={"p1": "prop-1"}),
            "tag-2",
            ColumnSchema("example", tags=["tag-1", "tag-2"], properties={"p1": "prop-1"}),
        ],
        [
            ColumnSchema("example", tags=["tag-1"], dtype=md.float32),
            ["tag-2", Tags.CONTINUOUS],
            ColumnSchema("example", tags=["tag-1", "tag-2", Tags.CONTINUOUS], dtype=md.float32),
        ],
    ],
)
def test_with_tags(column_schema, tags, expected_column_schema):
    assert column_schema.with_tags(tags) == expected_column_schema


@pytest.mark.parametrize(
    ["column_schema", "properties", "expected_column_schema"],
    [
        [
            ColumnSchema("example", properties={"a": "old"}),
            {"a": "new"},
            ColumnSchema("example", properties={"a": "new"}),
        ],
        [
            ColumnSchema("example", properties={"a": 1, "b": 2}),
            {"a": 4, "c": 3},
            ColumnSchema("example", properties={"a": 4, "b": 2, "c": 3}),
        ],
        [
            ColumnSchema(
                "example_col_2",
                dtype=md.float32,
                tags=[Tags.CONTINUOUS],
                properties={"a": 1, "domain": {"min": 0, "max": 5}},
            ),
            {"a": 4, "c": 3, "domain": {"max": 8}},
            ColumnSchema(
                "example_col_2",
                dtype=md.float32,
                tags=[Tags.CONTINUOUS],
                properties={"a": 4, "c": 3, "domain": {"max": 8}},
            ),
        ],
    ],
)
def test_with_properties(column_schema, properties, expected_column_schema):
    assert column_schema.with_properties(properties) == expected_column_schema


def test_column_schema_tags_normalize():
    schema1 = ColumnSchema("col1", tags=["categorical", "list", "item_id"])
    assert schema1.tags == TagSet([Tags.CATEGORICAL, Tags.LIST, Tags.ITEM_ID])


def test_list_column_attributes():
    col0_schema = ColumnSchema("col0")

    assert not col0_schema.is_list
    assert not col0_schema.is_ragged
    assert col0_schema.quantity == ColumnQuantity.SCALAR

    col1_schema = ColumnSchema("col1", is_list=False, is_ragged=False)

    assert not col1_schema.is_list
    assert not col1_schema.is_ragged
    assert col1_schema.quantity == ColumnQuantity.SCALAR

    col2_schema = ColumnSchema("col2", is_list=True)

    assert col2_schema.is_list
    assert col2_schema.is_ragged
    assert col2_schema.quantity == ColumnQuantity.RAGGED_LIST

    col3_schema = ColumnSchema("col3", is_list=True, is_ragged=True)

    assert col3_schema.is_list
    assert col3_schema.is_ragged
    assert col3_schema.quantity == ColumnQuantity.RAGGED_LIST

    col4_schema = ColumnSchema("col4", is_list=True, is_ragged=False)

    assert col4_schema.is_list
    assert not col4_schema.is_ragged
    assert col4_schema.quantity == ColumnQuantity.FIXED_LIST

    with pytest.raises(ValueError):
        ColumnSchema("col5", is_list=False, is_ragged=True)


def test_value_count_invalid_min_max():
    with pytest.raises(ValueError) as exc_info:
        ColumnSchema("col", is_ragged=True, properties={"value_count": {"min": 2, "max": 2}})
    assert "`is_ragged` is set to `True` but `value_count.min` == `value_count.max`" in str(
        exc_info.value
    )


@pytest.mark.parametrize(
    "properties",
    [
        {"value_count": {"max": 0}},
        {"value_count": {"min": 0}},
        {"value_count": {"min": 0, "max": 2}},
    ],
)
def test_value_count_zero_min_max(properties):
    with pytest.raises(ValueError) as exc_info:
        ColumnSchema("col", is_ragged=True, properties=properties)
    assert "`value_count` min and max must be greater than zero. " in str(exc_info.value)


@pytest.mark.parametrize(
    ["value_count_min", "value_count_max"],
    [
        [None, 4],
        [3, None],
        [1, 2],
    ],
)
def test_value_count(value_count_min, value_count_max):
    value_count = {}
    if value_count_min:
        value_count["min"] = value_count_min
    if value_count_max:
        value_count["max"] = value_count_max

    col_schema = ColumnSchema("col", properties={"value_count": value_count})

    assert col_schema.value_count.max == value_count_max
    assert col_schema.value_count.min == value_count_min


def test_value_count_assign_properties():
    col_schema = ColumnSchema("col", is_list=True, is_ragged=True)
    new_col_schema = col_schema.with_properties({"value_count": {"min": 5, "max": 5}})
    assert new_col_schema.is_ragged is False
    assert new_col_schema.value_count.min == new_col_schema.value_count.max == 5
