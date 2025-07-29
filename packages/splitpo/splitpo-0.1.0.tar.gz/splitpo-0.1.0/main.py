import argparse
import sys

from splitpo.split import split_po
from splitpo.join import join_po


def main():
    parser = argparse.ArgumentParser(
        description="Split and join gettext .po files"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # split-po subcommand
    split_parser = subparsers.add_parser("split-po", help="Split a .po file into chunks")
    split_parser.add_argument("input_file", help="Input .po file to split")
    split_parser.add_argument("--output-dir", default="./splitted", 
                             help="Output directory for split files (default: ./splitted)")
    split_parser.add_argument("--entries", type=int, default=100,
                             help="Number of entries per split file (default: 100)")
    
    # join-po subcommand
    join_parser = subparsers.add_parser("join-po", help="Join split .po files back together")
    join_parser.add_argument("input_files", nargs="+", 
                           help="Input .po files to join (supports wildcards)")
    join_parser.add_argument("--output", required=True,
                           help="Output .po file")
    
    args = parser.parse_args()
    
    if args.command == "split-po":
        from pathlib import Path
        # Create output directory if it doesn't exist
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        split_po(args.input_file, args.output_dir, args.entries)
    elif args.command == "join-po":
        join_po(args.input_files, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
