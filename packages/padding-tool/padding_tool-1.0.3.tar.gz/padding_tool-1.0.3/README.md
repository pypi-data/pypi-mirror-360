# Binary File Padding Tool

A simple Python CLI tool to pad a binary file to a specified size using a given byte value.

## Features

- Pads any binary file to a target size
- Customizable padding byte value
- Simple command-line interface
- Version flag support

## Requirements

- Python 3.6 or higher

Install dependencies using:

pip install -r requirements.txt

---

## Installation

Clone the repository.

```bash
git clone git@github.com:gilweis/padding-tool.git
cd padding-tool
```
---

## Usage

```bash
python -m padding_tool --in INPUT_FILE --out OUTPUT_FILE --needed_size SIZE --padding_value VALUE
```

### Arguments

| Argument           | Description                                      |
|--------------------|--------------------------------------------------|
| `--in`             | Path to the input binary file                    |
| `--out`            | Path to save the padded output file              |
| `--needed_size`    | Total desired size of the output file (in bytes) |
| `--padding_value`  | Byte value to use for padding (0–255)            |
| `--version`        | Show program version and exit                    |

### Example

```bash
python -m padding_tool --in firmware.bin --out padded_firmware.bin --needed_size 4096 --padding_value 255
```

This command reads `firmware.bin`, pads it with `0xFF` (255) bytes until the size is `4096` bytes,
and writes the result to `padded_firmware.bin`.

## Exit Codes

- `0`: File padded successfully
- `1`: Failed to pad the file

---

## Error Handling

- If the input file is larger than `--needed_size`, the program will raise an error and stop.
- Ensure that `--padding_value` is in the valid range `0–255`.

---

## Build and Install

To build source and wheel distributions:

python -m build

If you don't have the build tool installed:

pip install build

To install the package locally:

pip install .

To upload to PyPI (optional):

pip install twine
twine upload dist/*

---

## License

MIT License

## Version

1.0.3
