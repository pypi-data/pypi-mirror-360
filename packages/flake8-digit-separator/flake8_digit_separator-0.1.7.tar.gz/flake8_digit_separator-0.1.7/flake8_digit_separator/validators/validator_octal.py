from typing import TypeVar, final

from flake8_digit_separator.fds_numbers.fds_numbers import OctalNumber
from flake8_digit_separator.rules.rules import OctalFDSRules
from flake8_digit_separator.validators.base import BaseValidator

SelfOctalValidator = TypeVar('SelfOctalValidator', bound='OctalValidator')


@final
class OctalValidator(BaseValidator):
    """Validator for octal numbers."""

    def __init__(self: SelfOctalValidator, number: OctalNumber):
        self._number = number
        self._pattern = r'^[+-]?0[oO]_[0-7]{1,3}(_[0-7]{3})*$'

    def validate(self: SelfOctalValidator) -> bool:
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
    def number(self: SelfOctalValidator) -> OctalNumber:
        """FDS octal number object."""
        return self._number

    @property
    def pattern(self: SelfOctalValidator) -> str:
        """
        The regular expression that will be validated.

        :return: Regular expression.
        :rtype: str
        """
        return self._pattern

    @property
    def error_message(self: SelfOctalValidator) -> str:
        """
        The rule that the validator checked.

        :return: FDS rule.
        :rtype: str
        """
        return OctalFDSRules.FDS400.create_message()
