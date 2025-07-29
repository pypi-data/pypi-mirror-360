from dataclasses import dataclass
from enum import Enum


VALID_DTYPES = [
    "Categorical",
    "Numeric",
    "Datetime",
]


NAN_NUM = [
    "Replace with 0",
    "Drop Rows",
    "Keep as NaN",
]
NAN_CAT = [
    "Replace with No Data",
    "Drop Rows",
    "Keep as NaN",
]
NAN_DATETIME = [
    "Drop Rows",
    "Keep as NaN",
]
NAN_OPS = list(dict.fromkeys(NAN_NUM + NAN_CAT + NAN_DATETIME))

NUM_TO_CAT_OPS = [
    "As Category",
    "Into n equal bins",
    "Bin by widths",
]


class NumericConversion(Enum):
    AS_CATEGORY = NUM_TO_CAT_OPS[0]
    BINNED = NUM_TO_CAT_OPS[1]
    BIN_WIDTH = NUM_TO_CAT_OPS[2]


@dataclass
class NumericConverter:
    conversion: NumericConversion
    value: int | list[float] | None


class Dtype(Enum):
    CATEGORICAL = VALID_DTYPES[0]
    NUMERIC = VALID_DTYPES[1]
    DATETIME = VALID_DTYPES[2]


DtypeOperation = Dtype


class NaNOperation(Enum):
    REPLACE_WITH_0 = NAN_OPS[0]
    DROP_ROWS = NAN_OPS[1]
    KEEP_AS_NaN = NAN_OPS[2]
    REPLACE_WITH_NO_DATA = NAN_OPS[3]
