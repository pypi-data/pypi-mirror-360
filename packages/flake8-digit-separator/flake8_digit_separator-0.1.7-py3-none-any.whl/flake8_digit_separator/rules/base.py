import enum
from typing import TypeAlias, TypeVar

NumberWithSeparators: TypeAlias = str

SelfFDSRules = TypeVar('SelfFDSRules', bound='FDSRules')


class FDSRules(enum.Enum):
    """
    Flake8-digits-separator rules.

    When initializing an object, you must specify the rule number as the argument name.
    The rule text and a valid example must be specified as the argument value.
    """

    def __init__(
        self: SelfFDSRules,
        text: str,
        example: NumberWithSeparators,
    ) -> None:
        self._text = text
        self._example = example

    def create_message(self: SelfFDSRules) -> str:
        msg = '{rule}: {text} (e.g. {example})'

        return msg.format(
            rule=self.name,
            text=self.text,
            example=self.example,
        )

    @property
    def text(self: SelfFDSRules) -> str:
        """Text of rule."""
        return self._text

    @property
    def example(self: SelfFDSRules) -> NumberWithSeparators:
        """Valid example of rule."""
        return self._example
