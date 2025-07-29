import re
from abc import ABC, abstractmethod
from typing import TypeVar

from flake8_digit_separator.fds_numbers.base import (
    FDSNumber,
    NumberWithDelimiter,
    NumberWithPrefix,
)

SelfValidator = TypeVar('SelfValidator', bound='Validator')
SelfBaseValidator = TypeVar('SelfBaseValidator', bound='BaseValidator')


class Validator(ABC):
    """Abstract validator."""

    @property
    @abstractmethod
    def number(self: SelfValidator) -> FDSNumber | NumberWithDelimiter | NumberWithPrefix:
        """
        Number object obtained from classifier.

        :return: FDSNumber obj.
        :rtype: FDSNumber | NumberWithDelimiter | NumberWithPrefix
        """

    @property
    @abstractmethod
    def pattern(self: SelfValidator) -> str:
        """
        The regular expression that will be validated.

        :return: Regular expression.
        :rtype: str
        """

    @abstractmethod
    def validate(self: SelfValidator) -> bool:
        """
        Validation logic.

        :return: `True` if validation is success. Otherwise `False`.
        :rtype: bool
        """

    @property
    @abstractmethod
    def error_message(self: SelfValidator) -> str:
        """
        The rule that the validator checked.

        :return: FDS rule.
        :rtype: str
        """


class BaseValidator(Validator):
    """
    Base validator.

    Specific validators should be inherited from this class
    """

    def validate_token_by_pattern(self: SelfBaseValidator) -> bool:
        """
        Token validation by pattern.

        :return: `True` if token matches pattern. Otherwise `False`.
        :rtype: bool
        """
        return bool(re.fullmatch(self.pattern, self.number.token))

    def validate_token_as_int(self: SelfBaseValidator) -> bool:
        """
        Attempt to convert token to int.

        :return: `True` if operation is success. Otherwise `False`.
        :rtype: bool
        """
        try:
            int(self.number.token, self.number.numeral_system.value)
        except ValueError:
            return False

        return True

    def validate_token_as_float(self: SelfBaseValidator) -> bool:
        """
        Attempt to convert token to float.

        :return: `True` if operation is success. Otherwise `False`.
        :rtype: bool
        """
        try:
            float(self.number.token)
        except ValueError:
            return False

        return True
