from typing import TypeVar, final

from flake8_digit_separator.fds_numbers.fds_numbers import BinaryNumber
from flake8_digit_separator.rules.rules import BinaryFDSRules
from flake8_digit_separator.validators.base import BaseValidator

SelfBinaryValidator = TypeVar('SelfBinaryValidator', bound='BinaryValidator')


@final
class BinaryValidator(BaseValidator):
    """Validator for binary numbers."""

    def __init__(self: SelfBinaryValidator, number: BinaryNumber) -> None:
        self._pattern = r'^[+-]?0[bB]_([01]{1,4}(_[01]{4})*)$'
        self._number = number

    def validate(self: SelfBinaryValidator) -> bool:
        """
        Validates number token.

        1. Check that it can be converted to int.
        2. Check for pattern compliance.

        :return: `True` if all steps are completed. Otherwise `False`.
        :rtype: bool
        """
        if not self.validate_token_as_int():
            return False
        if not self.validate_token_by_pattern():
            return False

        return True

    @property
    def number(self: SelfBinaryValidator) -> BinaryNumber:
        """FDS binary number"""
        return self._number

    @property
    def pattern(self: SelfBinaryValidator) -> str:
        """The regular expression that will be validated."""
        return self._pattern

    @property
    def error_message(self: SelfBinaryValidator) -> str:
        """The rule that the validator checked."""
        return BinaryFDSRules.FDS300.create_message()
