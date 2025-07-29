"""Test split/join roundtrip functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import glob

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitpo.split import split_po
from splitpo.join import join_po
from splitpo.common import parse_po_file


class TestRoundtrip:
    """Test split/join roundtrip functionality."""

    def test_small_file_roundtrip(self, tmp_path):
        """Test roundtrip with small sample file."""
        # Use the small sample file
        original_file = Path(__file__).parent / "samples" / "small.po"
        assert original_file.exists()
        
        # Create working directory
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        
        # Split the file
        split_dir = work_dir / "split"
        split_dir.mkdir()
        split_po(str(original_file), str(split_dir), 5)
        
        # Find split files
        split_files = sorted(glob.glob(str(split_dir / "small_part_*.po")))
        assert len(split_files) > 0
        
        # Join the files back
        joined_file = work_dir / "joined.po"
        join_po(split_files, str(joined_file))
        
        # Compare original and joined files
        original_header, original_entries = parse_po_file(str(original_file))
        joined_header, joined_entries = parse_po_file(str(joined_file))
        
        # Filter out empty entries
        original_valid = [e for e in original_entries if not e.is_empty()]
        joined_valid = [e for e in joined_entries if not e.is_empty()]
        
        # Check that we have the same number of entries
        assert len(original_valid) == len(joined_valid)
        
        # Check that entries match
        for orig, joined in zip(original_valid, joined_valid):
            assert orig.msgid == joined.msgid
            assert orig.msgstr == joined.msgstr

    def test_large_file_roundtrip_100_entries(self, tmp_path):
        """Test roundtrip with large sample file using 100 entries per split."""
        # Use the large sample file
        original_file = Path(__file__).parent / "samples" / "large.po"
        assert original_file.exists()
        
        # Create working directory
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        
        # Split the file with 100 entries per file
        split_dir = work_dir / "split"
        split_dir.mkdir()
        split_po(str(original_file), str(split_dir), 100)
        
        # Find split files
        split_files = sorted(glob.glob(str(split_dir / "large_part_*.po")))
        assert len(split_files) > 0
        
        # Expected number of files: 251 entries / 100 per file = 3 files
        assert len(split_files) == 3
        
        # Check file naming (should be 000, 001, 002)
        expected_files = [
            split_dir / "large_part_000.po",
            split_dir / "large_part_001.po", 
            split_dir / "large_part_002.po"
        ]
        for expected in expected_files:
            assert expected.exists()
        
        # Join the files back
        joined_file = work_dir / "joined.po"
        join_po(split_files, str(joined_file))
        
        # Compare original and joined files
        original_header, original_entries = parse_po_file(str(original_file))
        joined_header, joined_entries = parse_po_file(str(joined_file))
        
        # Filter out empty entries
        original_valid = [e for e in original_entries if not e.is_empty()]
        joined_valid = [e for e in joined_entries if not e.is_empty()]
        
        # Check that we have the same number of entries
        assert len(original_valid) == len(joined_valid)
        assert len(original_valid) == 251  # 250 content + 1 header
        
        # Check that entries match
        for orig, joined in zip(original_valid, joined_valid):
            assert orig.msgid == joined.msgid
            assert orig.msgstr == joined.msgstr

    def test_large_file_roundtrip_different_chunk_sizes(self, tmp_path):
        """Test roundtrip with different chunk sizes."""
        chunk_sizes = [10, 50, 75, 100]
        
        for chunk_size in chunk_sizes:
            # Use the large sample file
            original_file = Path(__file__).parent / "samples" / "large.po"
            
            # Create working directory
            work_dir = tmp_path / f"work_{chunk_size}"
            work_dir.mkdir()
            
            # Split the file
            split_dir = work_dir / "split"
            split_dir.mkdir()
            split_po(str(original_file), str(split_dir), chunk_size)
            
            # Find split files
            split_files = sorted(glob.glob(str(split_dir / "large_part_*.po")))
            assert len(split_files) > 0
            
            # Join the files back
            joined_file = work_dir / "joined.po"
            join_po(split_files, str(joined_file))
            
            # Compare original and joined files
            original_header, original_entries = parse_po_file(str(original_file))
            joined_header, joined_entries = parse_po_file(str(joined_file))
            
            # Filter out empty entries
            original_valid = [e for e in original_entries if not e.is_empty()]
            joined_valid = [e for e in joined_entries if not e.is_empty()]
            
            # Check that we have the same number of entries
            assert len(original_valid) == len(joined_valid)
            
            # Check that entries match
            for orig, joined in zip(original_valid, joined_valid):
                assert orig.msgid == joined.msgid
                assert orig.msgstr == joined.msgstr

    def test_exact_file_content_preservation(self, tmp_path):
        """Test that file content is preserved exactly (including formatting)."""
        # Use the small sample file
        original_file = Path(__file__).parent / "samples" / "small.po"
        
        # Create working directory
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        
        # Split the file
        split_dir = work_dir / "split"
        split_dir.mkdir()
        split_po(str(original_file), str(split_dir), 100)  # All entries in one file
        
        # Find split files
        split_files = sorted(glob.glob(str(split_dir / "small_part_*.po")))
        assert len(split_files) == 1
        
        # Join the files back
        joined_file = work_dir / "joined.po"
        join_po(split_files, str(joined_file))
        
        # Read original and joined content
        original_content = original_file.read_text(encoding='utf-8')
        joined_content = joined_file.read_text(encoding='utf-8')
        
        # Parse both files to compare structure
        original_header, original_entries = parse_po_file(str(original_file))
        joined_header, joined_entries = parse_po_file(str(joined_file))
        
        # Compare headers (should be identical)
        assert original_header == joined_header
        
        # Filter out empty entries for comparison (since split/join filters them)
        original_valid = [e for e in original_entries if not e.is_empty()]
        joined_valid = [e for e in joined_entries if not e.is_empty()]
        
        # Compare entries
        assert len(original_valid) == len(joined_valid)
        for orig, joined in zip(original_valid, joined_valid):
            assert orig.msgid == joined.msgid
            assert orig.msgstr == joined.msgstr
            assert orig.msgctxt == joined.msgctxt

    def test_file_numbering_with_many_files(self, tmp_path):
        """Test file numbering when creating many split files."""
        # Create a large po file with many entries
        large_po = tmp_path / "huge.po"
        
        # Create content with 1000 entries
        content = """# Test po file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

"""
        
        for i in range(1000):
            content += f"""msgid "Entry {i:04d}"
msgstr "エントリ {i:04d}"

"""
        
        large_po.write_text(content)
        
        # Split with 1 entry per file (will create 1000 files)
        split_dir = tmp_path / "split"
        split_dir.mkdir()
        split_po(str(large_po), str(split_dir), 1)
        
        # Check that files are numbered correctly (1000 content + 1 header = 1001 files)
        split_files = sorted(glob.glob(str(split_dir / "huge_part_*.po")))
        assert len(split_files) == 1001
        
        # Check that numbering uses 4 digits (since we have 1001 files)
        assert split_files[0].endswith("huge_part_0000.po")
        assert split_files[1000].endswith("huge_part_1000.po")
        
        # Test a smaller roundtrip to verify it still works
        # Split first 10 files and join them
        first_10_files = split_files[:10]
        joined_file = tmp_path / "joined_10.po"
        join_po(first_10_files, str(joined_file))
        
        # Check that joined file has 10 entries
        _, entries = parse_po_file(str(joined_file))
        valid_entries = [e for e in entries if not e.is_empty()]
        assert len(valid_entries) == 10