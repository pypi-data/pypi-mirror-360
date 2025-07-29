from typing import TypeVar, final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.fds_numbers import IntNumber

SelfIntClassifier = TypeVar('SelfIntClassifier', bound='IntClassifier')


@final
class IntClassifier(BaseClassifier):
    """Classifier for int numbers."""

    def __init__(
        self: SelfIntClassifier,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self: SelfIntClassifier) -> IntNumber:
        """
        Returns a int number if it matches.

        :return: Int number
        :rtype: IntNumber
        """
        return IntNumber(self.token)

    @property
    def token(self: SelfIntClassifier) -> TokenLikeStr:
        """
        Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
