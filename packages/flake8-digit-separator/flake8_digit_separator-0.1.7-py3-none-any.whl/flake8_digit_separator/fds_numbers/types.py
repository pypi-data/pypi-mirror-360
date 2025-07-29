from typing import TypeAlias

from flake8_digit_separator.fds_numbers.fds_numbers import (
    BinaryNumber,
    ComplexNumber,
    FloatNumber,
    HexNumber,
    IntNumber,
    OctalNumber,
    ScientificNumber,
)

FDSNumbersWithPrefixAlias: TypeAlias = HexNumber | OctalNumber | BinaryNumber
FDSNumbersWithOutPrefixAlias: TypeAlias = IntNumber | FloatNumber
FDSNumbersUnsupported: TypeAlias = ComplexNumber | ScientificNumber
FDSNumbersAlias: TypeAlias = FDSNumbersWithOutPrefixAlias | FDSNumbersWithPrefixAlias | FDSNumbersUnsupported
