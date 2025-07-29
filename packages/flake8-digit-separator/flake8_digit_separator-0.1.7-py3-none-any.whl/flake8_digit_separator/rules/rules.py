from flake8_digit_separator.rules.base import FDSRules


class IntFDSRules(FDSRules):
    """FDS rules for int"""

    FDS100 = 'Group by 3s from right', '10_000'


class FloatFDSRules(FDSRules):
    """FDS rules for float"""

    FDS200 = 'Group by 3s from right', '10_000.1_234'


class BinaryFDSRules(FDSRules):
    """FDS rules for binary"""

    FDS300 = 'Group by 4s from right after prefix `0b_`', '0b_1101_1001'


class OctalFDSRules(FDSRules):
    """FDS rules for octal"""

    FDS400 = 'Group by 3s from right after prefix `0o_`', '0o_12_134_155'


class HexFDSRules(FDSRules):
    """FDS rules for hex"""

    FDS500 = 'Group by 4s from right after prefix `0x_`', '0x_CAFE_F00D'
