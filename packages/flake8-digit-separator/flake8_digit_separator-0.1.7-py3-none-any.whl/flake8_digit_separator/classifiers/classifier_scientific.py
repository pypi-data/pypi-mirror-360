from typing import TypeVar, final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.fds_numbers import ScientificNumber

SelfScientifiClassifier = TypeVar('SelfScientifiClassifier', bound='ScientifiClassifier')


@final
class ScientifiClassifier(BaseClassifier):
    """Classifier for scientific numbers."""

    def __init__(
        self: SelfScientifiClassifier,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self: SelfScientifiClassifier) -> ScientificNumber | None:
        """
        Returns a scientific number if it matches.

        :return: Scientific number
        :rtype: ScientificNumber | None
        """
        if 'e' in self.token_lower:
            return ScientificNumber(self.token_lower)

        return None

    @property
    def token(self: SelfScientifiClassifier) -> TokenLikeStr:
        """
        Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
