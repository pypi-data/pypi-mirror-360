from typing import TypeAlias, TypeVar, final

from flake8_digit_separator.classifiers.classifier_binary import (
    BinaryClassifier,
)
from flake8_digit_separator.classifiers.classifier_complex import (
    ComplexClassifier,
)
from flake8_digit_separator.classifiers.classifier_float import FloatClassifier
from flake8_digit_separator.classifiers.classifier_hex import HexClassifier
from flake8_digit_separator.classifiers.classifier_int import IntClassifier
from flake8_digit_separator.classifiers.classifier_octal import OctalClassifier
from flake8_digit_separator.classifiers.classifier_scientific import (
    ScientifiClassifier,
)

SelfClassifierRegistry = TypeVar('SelfClassifierRegistry', bound='ClassifierRegistry')

ClassifiersWithPrefixAlias: TypeAlias = OctalClassifier | HexClassifier | BinaryClassifier
ClassifiersWithOutPrefixAlias: TypeAlias = IntClassifier | FloatClassifier
ClassifiersUnsupported: TypeAlias = ScientifiClassifier | ComplexClassifier
ClassifiersAlias: TypeAlias = ClassifiersUnsupported | ClassifiersWithOutPrefixAlias | ClassifiersWithPrefixAlias


@final
class ClassifierRegistry:
    """
    Classifier Registrator.

    Classification of numbers requires a deterministic order of classifiers.
    """

    hex_classifier = HexClassifier
    octal_classifier = OctalClassifier
    binary_classifier = BinaryClassifier
    complex_classifier = ComplexClassifier
    scientific_classifier = ScientifiClassifier
    float_classifier = FloatClassifier
    int_classifier = IntClassifier

    @classmethod
    def get_ordered_classifiers(cls: type[SelfClassifierRegistry]) -> tuple[type[ClassifiersAlias], ...]:
        """
        Generates an ordered tuple of classifiers.

        :return: Ordered tuple of classifiers.
        :rtype: tuple[type[ClassifiersAlias], ...]
        """
        return (  # noqa: WPS227
            cls.hex_classifier,
            cls.octal_classifier,
            cls.binary_classifier,
            cls.complex_classifier,
            cls.scientific_classifier,
            cls.float_classifier,
            cls.int_classifier,
        )
