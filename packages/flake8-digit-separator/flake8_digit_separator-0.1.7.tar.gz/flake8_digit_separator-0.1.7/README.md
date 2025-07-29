# flake8-digit-separator
[![coverage](https://raw.githubusercontent.com/imtoopunkforyou/flake8-digit-separator/refs/heads/main/.github/badge/coverage.svg)](https://github.com/pytest-dev/pytest-cov)
[![tests](https://github.com/imtoopunkforyou/flake8-digit-separator/actions/workflows/tests.yaml/badge.svg)](https://github.com/imtoopunkforyou/flake8-digit-separator/actions/workflows/tests.yaml)
[![pypi package version](https://img.shields.io/pypi/v/flake8-digit-separator.svg)](https://pypi.org/project/flake8-digit-separator)
[![pypi downloads](https://img.shields.io/pypi/dm/flake8-digit-separator.svg)](https://pypi.org/project/flake8-digit-separator)
[![supported python versions](https://img.shields.io/pypi/pyversions/flake8-digit-separator.svg)](https://pypi.org/project/flake8-digit-separator)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![license](https://img.shields.io/pypi/l/flake8-digit-separator.svg)](https://github.com/imtoopunkforyou/flake8-digit-separator/blob/main/LICENSE)  


<p align="center">
  <a href="https://pypi.org/project/flake8-digit-separator">
    <img src="https://raw.githubusercontent.com/imtoopunkforyou/flake8-digit-separator/main/.github/badge/logo.png"
         alt="FDS logo">
  </a>
</p>

A set of [rules](https://github.com/imtoopunkforyou/flake8-digit-separator?tab=readme-ov-file#rules) on top of the capabilities provided by [PEP515](https://peps.python.org/pep-0515/).

```python
correct_int = 10_000
correct_float = 10_000.1_234
correct_binary = 0b_1101_1001
correct_octal = 0o_134_155
correct_hex = 0x_CAFE_F00D
```

## Installation
```bash
pip install flake8-digit-separator
```

### Dependencies
- `python (>=3.10, <4.0)`
- `flake8 (>=7.1, <8.0)`

## Usage
```bash
flake8 . --select FDS
```

## Rules
[PEP515](https://peps.python.org/pep-0515/) allows separators, but does not impose any restrictions on their position in a number (except that a number should not start/end with a separator and there should not be two separators in a row). To introduce more rigor and beauty into the code, we have written a few simple rules that we suggest following.

| Rule   | Number  | Description                               | Correct       | Wrong       |
|--------|---------|-------------------------------------------|---------------|-------------|
| FDS100 | integer | Group by 3s from right                    | 10_000        | 10_0        |
| FDS200 | float   | Group by 3s from right                    | 10_000.1_234  | 1_0_0.123_4 |
| FDS300 | binary  | Group by 4s from right after prefix `0b_` | 0b_1101_1001  | 0b110_11    |
| FDS400 | octal   | Group by 3s from right after prefix `0o_` | 0o_12_134_155 | 0o1_23_45   |
| FDS500 | hex     | Group by 4s from right after prefix `0x_` | 0x_CAFE_F00D  | 0xCAFEF0_0D |

## License
[FDS](https://github.com/imtoopunkforyou/flake8-digit-separator) is released under the MIT License. See the bundled [LICENSE](https://github.com/imtoopunkforyou/flake8-digit-separator/blob/main/LICENSE) file for details.

The logo was created using [Font Meme](https://fontmeme.com/graffiti-creator/).