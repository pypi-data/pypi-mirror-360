from typing import TypeVar, final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.enums import NumberDelimiter
from flake8_digit_separator.fds_numbers.fds_numbers import FloatNumber

SelfFloatClassifier = TypeVar('SelfFloatClassifier', bound='FloatClassifier')


@final
class FloatClassifier(BaseClassifier):
    """Classifier for float numbers."""

    def __init__(
        self: SelfFloatClassifier,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self: SelfFloatClassifier) -> FloatNumber | None:
        """
        Returns a float number if it matches.

        :return: Float number
        :rtype: FloatNumber | None
        """
        if NumberDelimiter.FLOAT.value in self.token:
            return FloatNumber(self.token)

        return None

    @property
    def token(self: SelfFloatClassifier) -> TokenLikeStr:
        """
        Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
