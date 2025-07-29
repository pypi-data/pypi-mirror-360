"""Split po files into chunks."""

import argparse
import sys
from pathlib import Path

from .common import parse_po_file, write_po_file


def split_po(input_file: str, output_dir: str, entries: int) -> None:
    """Split a .po file into chunks by entry count."""
    print(f"Splitting {input_file} into {entries} entries per file in {output_dir}")
    
    if not Path(input_file).exists():
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    
    # Parse the input file
    header_lines, po_entries = parse_po_file(input_file)
    
    # Filter out empty entries
    valid_entries = [entry for entry in po_entries if not entry.is_empty()]
    
    if not valid_entries:
        print("No valid entries found in the po file")
        return
    
    # Split entries into chunks
    total_entries = len(valid_entries)
    num_files = (total_entries + entries - 1) // entries  # Ceiling division
    
    input_path = Path(input_file)
    base_name = input_path.stem
    
    # Calculate number of digits needed, minimum 3
    import math
    num_digits = max(3, len(str(num_files)))
    
    for i in range(num_files):
        start_idx = i * entries
        end_idx = min((i + 1) * entries, total_entries)
        chunk_entries = valid_entries[start_idx:end_idx]
        
        # Create output filename with zero-based numbering
        output_file = Path(output_dir) / f"{base_name}_part_{i:0{num_digits}d}.po"
        
        # Write the chunk
        write_po_file(str(output_file), header_lines, chunk_entries)
        print(f"Created {output_file} with {len(chunk_entries)} entries")
    
    print(f"Split complete: {total_entries} entries into {num_files} files")


def main():
    """Main entry point for split-po command."""
    parser = argparse.ArgumentParser(
        description="Split a .po file into chunks by entry count"
    )
    parser.add_argument("input_file", help="Input .po file to split")
    parser.add_argument("-o", "--output-dir", 
                       help="Output directory for split files")
    parser.add_argument("-e", "--entries", type=int, default=100,
                       help="Number of entries per split file (default: 100)")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    split_po(args.input_file, args.output_dir, args.entries)


if __name__ == "__main__":
    main()