from typing import TypeAlias

from flake8_digit_separator.validators.validator_binary import BinaryValidator
from flake8_digit_separator.validators.validator_float import FloatValidator
from flake8_digit_separator.validators.validator_hex import HexValidator
from flake8_digit_separator.validators.validator_int import IntValidator
from flake8_digit_separator.validators.validator_octal import OctalValidator

ValidatorsWithPrefixAlias: TypeAlias = HexValidator | OctalValidator | BinaryValidator
ValidatorsWithOutPrefixAlias: TypeAlias = IntValidator | FloatValidator
ValidatorsAlias: TypeAlias = ValidatorsWithPrefixAlias | ValidatorsWithOutPrefixAlias
