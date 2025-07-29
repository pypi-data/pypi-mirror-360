"""Test split/join functionality with real sample po files."""

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


class TestRealSamples:
    """Test split/join functionality with real sample po files."""

    @pytest.mark.parametrize("sample_file", [
        "stdtypes.po",
        "concurrent.po", 
        "pathlib.po"
    ])
    def test_real_sample_roundtrip_100_entries(self, tmp_path, sample_file):
        """Test roundtrip with real sample files using 100 entries per split."""
        # Use the real sample file
        original_file = Path(__file__).parent / "samples" / sample_file
        assert original_file.exists(), f"Sample file {sample_file} not found"
        
        # Create working directory
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        
        # Split the file with 100 entries per file
        split_dir = work_dir / "split"
        split_dir.mkdir()
        split_po(str(original_file), str(split_dir), 100)
        
        # Find split files
        base_name = original_file.stem
        split_files = sorted(glob.glob(str(split_dir / f"{base_name}_part_*.po")))
        assert len(split_files) > 0, f"No split files created for {sample_file}"
        
        # Join the files back
        joined_file = work_dir / "joined.po"
        join_po(split_files, str(joined_file))
        
        # Compare original and joined file contents directly
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(joined_file, 'r', encoding='utf-8') as f:
            joined_content = f.read()
        
        # Normalize line endings and compare
        original_normalized = original_content.strip()
        joined_normalized = joined_content.strip()
        
        assert original_normalized == joined_normalized, f"File content mismatch for {sample_file}"

    @pytest.mark.parametrize("sample_file,chunk_size", [
        ("stdtypes.po", 50),
        ("concurrent.po", 25),
        ("pathlib.po", 75),
        ("stdtypes.po", 200),
        ("concurrent.po", 150),
        ("pathlib.po", 300)
    ])
    def test_real_sample_different_chunk_sizes(self, tmp_path, sample_file, chunk_size):
        """Test roundtrip with real sample files using different chunk sizes."""
        # Use the real sample file
        original_file = Path(__file__).parent / "samples" / sample_file
        assert original_file.exists(), f"Sample file {sample_file} not found"
        
        # Create working directory
        work_dir = tmp_path / f"work_{chunk_size}"
        work_dir.mkdir()
        
        # Split the file
        split_dir = work_dir / "split"
        split_dir.mkdir()
        split_po(str(original_file), str(split_dir), chunk_size)
        
        # Find split files
        base_name = original_file.stem
        split_files = sorted(glob.glob(str(split_dir / f"{base_name}_part_*.po")))
        assert len(split_files) > 0, f"No split files created for {sample_file} with chunk size {chunk_size}"
        
        # Join the files back
        joined_file = work_dir / "joined.po"
        join_po(split_files, str(joined_file))
        
        # Compare original and joined file contents directly
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(joined_file, 'r', encoding='utf-8') as f:
            joined_content = f.read()
        
        # Normalize line endings and compare
        original_normalized = original_content.strip()
        joined_normalized = joined_content.strip()
        
        assert original_normalized == joined_normalized, f"File content mismatch for {sample_file} (chunk_size={chunk_size})"

    def test_all_real_samples_file_counts(self, tmp_path):
        """Test that split files are created with correct counts for all real samples."""
        sample_files = ["stdtypes.po", "concurrent.po", "pathlib.po"]
        
        for sample_file in sample_files:
            # Use the real sample file
            original_file = Path(__file__).parent / "samples" / sample_file
            assert original_file.exists(), f"Sample file {sample_file} not found"
            
            # Count original entries
            _, original_entries = parse_po_file(str(original_file))
            original_count = len([e for e in original_entries if not e.is_empty()])
            
            if original_count == 0:
                continue  # Skip files with no valid entries
            
            # Create working directory
            work_dir = tmp_path / f"count_test_{sample_file.replace('.', '_')}"
            work_dir.mkdir()
            
            # Test with chunk size that will create multiple files
            chunk_size = max(1, original_count // 3)  # Ensure at least 2-3 files
            
            # Split the file
            split_dir = work_dir / "split"
            split_dir.mkdir()
            split_po(str(original_file), str(split_dir), chunk_size)
            
            # Find split files
            base_name = original_file.stem
            split_files = sorted(glob.glob(str(split_dir / f"{base_name}_part_*.po")))
            
            # Calculate expected number of files
            expected_files = (original_count + chunk_size - 1) // chunk_size
            
            assert len(split_files) == expected_files, f"Expected {expected_files} files for {sample_file}, got {len(split_files)}"
            
            # Verify total entry count across all split files
            total_split_entries = 0
            for split_file in split_files:
                _, entries = parse_po_file(split_file)
                total_split_entries += len([e for e in entries if not e.is_empty()])
            
            assert total_split_entries == original_count, f"Total entries mismatch for {sample_file}: {total_split_entries} != {original_count}"

    def test_real_samples_preserve_structure(self, tmp_path):
        """Test that real sample files preserve their structure through split/join."""
        sample_files = ["stdtypes.po", "concurrent.po", "pathlib.po"]
        
        for sample_file in sample_files:
            # Use the real sample file
            original_file = Path(__file__).parent / "samples" / sample_file
            assert original_file.exists(), f"Sample file {sample_file} not found"
            
            # Create working directory  
            work_dir = tmp_path / f"structure_test_{sample_file.replace('.', '_')}"
            work_dir.mkdir()
            
            # Split the file (use large chunk size to minimize fragmentation)
            split_dir = work_dir / "split"
            split_dir.mkdir()
            split_po(str(original_file), str(split_dir), 1000)
            
            # Find split files
            base_name = original_file.stem
            split_files = sorted(glob.glob(str(split_dir / f"{base_name}_part_*.po")))
            
            # Join the files back
            joined_file = work_dir / "joined.po"
            join_po(split_files, str(joined_file))
            
            # Compare original and joined file contents directly
            with open(original_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            with open(joined_file, 'r', encoding='utf-8') as f:
                joined_content = f.read()
            
            # Normalize line endings and compare
            original_normalized = original_content.strip()
            joined_normalized = joined_content.strip()
            
            assert original_normalized == joined_normalized, f"File content mismatch for {sample_file}"