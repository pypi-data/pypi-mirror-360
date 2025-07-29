import ast
import tokenize
from typing import Iterator, TypeVar

from flake8_digit_separator import __version__ as version
from flake8_digit_separator.classifiers.registry import ClassifierRegistry
from flake8_digit_separator.error import Error
from flake8_digit_separator.fds_numbers.types import FDSNumbersAlias
from flake8_digit_separator.types import ErrorMessage
from flake8_digit_separator.validators.registry import ValidatorRegistry

SelfChecker = TypeVar('SelfChecker', bound='Checker')


class Checker:
    name = version.NAME
    version = version.VERSION

    def __init__(
        self: SelfChecker,
        tree: ast.AST,
        file_tokens: list[tokenize.TokenInfo],
    ) -> None:
        self.file_tokens = file_tokens

    def run(self: SelfChecker) -> Iterator[ErrorMessage]:
        """
        Entry point and start of validation.

        1. Check that the token is a number.
        2. Classify the token.
        3. Validate the token.
        4. Display an error.

        :yield: FDS rule that was broken.
        :rtype: Iterator[ErrorMessage]
        """
        for token in self.file_tokens:
            if token.type == tokenize.NUMBER:
                error = self._process_number_token(token)
                if error:
                    yield error.as_tuple()

    def _process_number_token(
        self: SelfChecker,
        token: tokenize.TokenInfo,
    ) -> Error | None:
        number = self._classify(token)

        if number:
            if not number.is_supported:
                return None

            validator = ValidatorRegistry.get_validator(number)
            if validator.validate():
                return None

            return Error(
                line=token.start[0],
                column=token.start[1],
                message=validator.error_message,
                object_type=type(self),
            )

        return None

    def _classify(self: SelfChecker, token: tokenize.TokenInfo) -> FDSNumbersAlias | None:
        classifiers = ClassifierRegistry.get_ordered_classifiers()
        for classifier in classifiers:
            number = classifier(token.string).classify()
            if number:
                break

        return number if number else None
