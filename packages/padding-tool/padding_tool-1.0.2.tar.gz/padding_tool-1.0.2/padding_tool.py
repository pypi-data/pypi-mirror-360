"""Module padding-tool."""

import argparse
import sys

__version__ = "1.0.2"


def pad_file(in_file, out_file: str, needed_size: int, padding_value: int, chunk_size: int = 1024 * 1024) -> bool:
    """ pad_file """
    total_written = 0

    with open(in_file, 'rb') as fin, open(out_file, 'wb') as fout:
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            fout.write(chunk)
            total_written += len(chunk)

            if total_written > needed_size:
                print(f"Input file is larger than needed_size ({total_written} > {needed_size})")
                return False

        remaining = needed_size - total_written
        if remaining > 0:
            padding = bytes([padding_value]) * min(chunk_size, remaining)
            while remaining > 0:
                to_write = padding[:min(len(padding), remaining)]
                fout.write(to_write)
                remaining -= len(to_write)

    print(f"Padded file saved to '{out_file}' ({needed_size} bytes)")
    return True


def main():
    """ main """
    parser = argparse.ArgumentParser(description="Pad a binary file to a specific size with a given byte value.")
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('--in', dest='in_file', required=True, help='Input filename')
    parser.add_argument('--out', dest='out_file', required=True, help='Output filename')
    parser.add_argument('--needed_size', type=int, required=True, help='Total size of output file in bytes')
    parser.add_argument('--padding_value', type=int, choices=range(0, 256), required=True,
                        default=255, help='Byte value for padding (0-255, default: 255)')

    args = parser.parse_args()

    success: bool = pad_file(args.in_file, args.out_file, args.needed_size, args.padding_value)

    if success:
        print(f"{args.out_file} successfully padded")
        sys.exit(0)

    print(f"Failed to pad {args.in_file}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
