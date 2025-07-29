import sys
import argparse
from pybr import run_pybr, convert_pybr_to_py

def main():
    parser = argparse.ArgumentParser(description='PyBr - Python with Braces')
    parser.add_argument('file', help='PyBr file to run or convert')
    parser.add_argument('--convert', '-c', action='store_true', help='Convert to Python file')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--output', '-o', help='Output file for conversion')

    args = parser.parse_args()

    if args.convert or args.output:
        output_path = args.output or args.file.replace('.pybr', '.py')
        result = convert_pybr_to_py(args.file, output_path)
        print(f"Converted {args.file} to {output_path}")
        if args.debug:
            print("Converted code:")
            print(result)
    else:
        run_pybr(args.file)

if __name__ == "__main__":
    main()