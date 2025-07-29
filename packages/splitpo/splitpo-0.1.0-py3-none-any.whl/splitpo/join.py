"""Join split po files back together."""

import argparse
import sys
from pathlib import Path
from typing import List

from .common import parse_po_file, write_po_file


def join_po(input_files: List[str], output_file: str) -> None:
    """Join split .po files back together."""
    print(f"Joining {len(input_files)} files into {output_file}")
    
    # Sort files to ensure correct order
    sorted_files = sorted(input_files)
    
    if not sorted_files:
        print("No input files specified")
        sys.exit(1)
    
    # Parse the first file to get header
    header_lines, all_entries = parse_po_file(sorted_files[0])
    
    # Parse remaining files and collect entries
    for file_path in sorted_files[1:]:
        if not Path(file_path).exists():
            print(f"Warning: File {file_path} does not exist, skipping")
            continue
        
        _, entries = parse_po_file(file_path)
        all_entries.extend(entries)
    
    # Filter out empty entries
    valid_entries = [entry for entry in all_entries if not entry.is_empty()]
    
    # Write the combined file
    write_po_file(output_file, header_lines, valid_entries)
    
    print(f"Join complete: {len(valid_entries)} entries written to {output_file}")


def main():
    """Main entry point for join-po command."""
    parser = argparse.ArgumentParser(
        description="Join split .po files back together"
    )
    parser.add_argument("input_files", nargs="+", 
                       help="Input .po files to join (supports wildcards)")
    parser.add_argument("-o", "--output", required=True,
                       help="Output .po file")
    
    args = parser.parse_args()
    
    join_po(args.input_files, args.output)


if __name__ == "__main__":
    main()