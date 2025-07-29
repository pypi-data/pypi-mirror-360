from dataclasses import dataclass

from flake8_digit_separator.fds_numbers.base import (
    FDSNumber,
    NumberWithDelimiter,
    NumberWithPrefix,
)
from flake8_digit_separator.fds_numbers.enums import (
    NumberDelimiter,
    NumberPrefix,
    NumeralSystem,
)


@dataclass(frozen=True)
class IntNumber(FDSNumber):
    """Int number object."""

    numeral_system: NumeralSystem = NumeralSystem.FLOAT
    is_supported: bool = True


@dataclass(frozen=True)
class HexNumber(NumberWithPrefix):
    """Hex number object."""

    numeral_system: NumeralSystem = NumeralSystem.HEX
    is_supported: bool = True
    prefix: NumberPrefix = NumberPrefix.HEX


@dataclass(frozen=True)
class OctalNumber(NumberWithPrefix):
    """Octal number object."""

    numeral_system: NumeralSystem = NumeralSystem.OCTAL
    is_supported: bool = True
    prefix: NumberPrefix = NumberPrefix.OCTAL


@dataclass(frozen=True)
class FloatNumber(NumberWithDelimiter):
    """Float number object."""

    numeral_system: NumeralSystem = NumeralSystem.FLOAT
    is_supported: bool = True
    delimiter: NumberDelimiter = NumberDelimiter.FLOAT


@dataclass(frozen=True)
class BinaryNumber(NumberWithPrefix):
    """Binary number object."""

    numeral_system: NumeralSystem = NumeralSystem.BINARY
    is_supported: bool = True
    prefix: NumberPrefix = NumberPrefix.BINARY


@dataclass(frozen=True)
class ComplexNumber(FDSNumber):
    """Complex number object."""

    numeral_system: NumeralSystem = NumeralSystem.FLOAT
    is_supported: bool = False


@dataclass(frozen=True)
class ScientificNumber(FDSNumber):
    """Scientific number object."""

    numeral_system: NumeralSystem = NumeralSystem.FLOAT
    is_supported: bool = False
