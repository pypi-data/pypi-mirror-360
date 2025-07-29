from typing import TypeVar, final

from flake8_digit_separator.fds_numbers.fds_numbers import HexNumber
from flake8_digit_separator.rules.rules import HexFDSRules
from flake8_digit_separator.validators.base import BaseValidator

SelfHexValidator = TypeVar('SelfHexValidator', bound='HexValidator')


@final
class HexValidator(BaseValidator):
    """Validator for hex numbers."""

    def __init__(self: SelfHexValidator, number: HexNumber) -> None:
        self._pattern = r'^[+-]?0[xX]_[0-9a-fA-F]{1,4}(?:_[0-9a-fA-F]{4})*$'
        self._number = number

    def validate(self: SelfHexValidator) -> bool:
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
    def number(self: SelfHexValidator) -> HexNumber:
        """FDS hex number object."""
        return self._number

    @property
    def pattern(self: SelfHexValidator) -> str:
        """The regular expression that will be validated."""
        return self._pattern

    @property
    def error_message(self: SelfHexValidator) -> str:
        """
        The rule that the validator checked.

        :return: FDS rule.
        :rtype: str
        """
        return HexFDSRules.FDS500.create_message()
