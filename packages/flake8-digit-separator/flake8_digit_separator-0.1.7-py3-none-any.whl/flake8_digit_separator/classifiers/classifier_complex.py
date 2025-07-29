from typing import TypeVar, final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.fds_numbers import ComplexNumber

SelfComplexClassifier = TypeVar('SelfComplexClassifier', bound='ComplexClassifier')


@final
class ComplexClassifier(BaseClassifier):
    """Classifier for complex numbers."""

    def __init__(
        self: SelfComplexClassifier,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self: SelfComplexClassifier) -> ComplexNumber | None:
        """
        Returns a complex number if it matches.

        :return: Complex number
        :rtype: ComplexNumber | None
        """
        if 'j' in self.token_lower:
            return ComplexNumber(self.token_lower)

        return None

    @property
    def token(self: SelfComplexClassifier) -> TokenLikeStr:
        """
        Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
