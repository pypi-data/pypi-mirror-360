"""Common utilities for po file processing."""

import sys
from pathlib import Path
from typing import List, Tuple


class PoEntry:
    """Represents a single po file entry."""
    def __init__(self):
        self.msgid = ""
        self.msgstr = ""
        self.comments = []
        self.references = []
        self.flags = []
        self.msgctxt = ""
        self.raw_lines = []
    
    def is_empty(self) -> bool:
        """Check if this is an empty entry (no raw content)."""
        return not self.raw_lines
    
    def to_string(self) -> str:
        """Convert entry back to po format."""
        return '\n'.join(self.raw_lines)


def parse_po_file(file_path: str) -> Tuple[List[str], List[PoEntry]]:
    """Parse a po file and return header lines and entries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into entries by looking for msgid patterns
    # but preserve all the original formatting
    
    lines = content.split('\n')
    entries = []
    current_entry = None
    header_lines = []
    found_first_msgid = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for msgid to start a new entry
        if line.strip().startswith('msgid '):
            found_first_msgid = True
            if current_entry is not None:
                entries.append(current_entry)
            current_entry = PoEntry()
            current_entry.raw_lines = []
            
            # Parse msgid
            current_entry.msgid = line.strip()[6:].strip('"')
        
        # If we haven't found the first msgid yet, it's part of header
        if not found_first_msgid:
            header_lines.append(line)
        else:
            # Add line to current entry
            if current_entry is not None:
                current_entry.raw_lines.append(line)
                
                # Parse other fields
                if line.strip().startswith('msgstr '):
                    current_entry.msgstr = line.strip()[7:].strip('"')
                elif line.strip().startswith('msgctxt '):
                    current_entry.msgctxt = line.strip()[8:].strip('"')
        
        i += 1
    
    # Add the last entry
    if current_entry is not None:
        entries.append(current_entry)
    
    return header_lines, entries


def write_po_file(file_path: str, header_lines: List[str], entries: List[PoEntry]) -> None:
    """Write po file with header and entries."""
    with open(file_path, 'w', encoding='utf-8') as f:
        # Write header
        for line in header_lines:
            f.write(line + '\n')
        
        # Write entries - preserve their original formatting exactly
        for entry in entries:
            entry_content = entry.to_string()
            f.write(entry_content)
            # Only add newline if the entry doesn't already end with one
            if entry_content and not entry_content.endswith('\n'):
                f.write('\n')