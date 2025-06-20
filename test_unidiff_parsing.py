#!/usr/bin/env python3
"""
Tests for git patch parsing with unidiff library.
Part of project resonantrabbit.
"""

import os
import subprocess
import tempfile

import pytest
import unidiff


class TestUnidiffParsing:
    """Test suite for unidiff patch parsing."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            subprocess.run(
                ["git", "init"], cwd=temp_dir, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=temp_dir,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True
            )

            yield temp_dir

    @pytest.fixture
    def sample_files_repo(self, temp_git_repo):
        """Create a git repo with sample files for testing."""
        repo_dir = temp_git_repo

        # Create initial files
        example_py = os.path.join(repo_dir, "example.py")
        with open(example_py, "w") as f:
            f.write("""def hello():
    print("Hello, World!")
def goodbye():
    print("Goodbye!")

def main():
    hello()
    goodbye()
""")

        config_txt = os.path.join(repo_dir, "config.txt")
        with open(config_txt, "w") as f:
            f.write("""# Configuration file
setting1=value1

setting2=value2

setting3=value3
""")

        # Add and commit initial files
        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True
        )

        return repo_dir

    def test_patch_parsing_basic(self):
        """Test basic patch parsing functionality."""
        patch_file = os.path.join("testdata", "empty_lines.patch")

        # Ensure patch file exists
        assert os.path.exists(patch_file), f"Patch file {patch_file} not found"

        # Parse the patch
        patch_set = unidiff.PatchSet.from_filename(patch_file, encoding="utf-8")

        # Basic assertions
        assert len(patch_set) > 0, "Patch should contain at least one file"

        # Check that we can iterate through files
        for file_patch in patch_set:
            assert hasattr(file_patch, "path")
            assert hasattr(file_patch, "added")
            assert hasattr(file_patch, "removed")

    def test_empty_line_detection(self):
        """Test detection of empty line additions and removals."""
        patch_file = os.path.join("testdata", "empty_lines.patch")
        patch_set = unidiff.PatchSet.from_filename(patch_file, encoding="utf-8")

        empty_lines_added = 0
        empty_lines_removed = 0

        for file_patch in patch_set:
            for hunk in file_patch:
                for line in hunk:
                    if line.value.strip() == "":  # Empty or whitespace-only line
                        if line.is_added:
                            empty_lines_added += 1
                        elif line.is_removed:
                            empty_lines_removed += 1

        # We expect to find both empty line additions and removals in our test patch
        assert empty_lines_added > 0, "Should detect empty line additions"
        assert empty_lines_removed > 0, "Should detect empty line removals"

    def test_git_apply_integration(self, sample_files_repo):
        """Test that patches parsed by unidiff can be successfully applied with git apply."""
        repo_dir = sample_files_repo

        # Create modifications to generate a patch
        example_py = os.path.join(repo_dir, "example.py")
        with open(example_py, "w") as f:
            f.write("""def hello():
    print("Hello, World!")

def goodbye():
    print("Goodbye!")
    
    # Added some spacing
def main():
    hello() 
    goodbye()
""")

        config_txt = os.path.join(repo_dir, "config.txt")
        with open(config_txt, "w") as f:
            f.write("""# Configuration file
setting1=value1
setting2=value2
setting3=value3
""")

        # Create new file
        newfile_md = os.path.join(repo_dir, "newfile.md")
        with open(newfile_md, "w") as f:
            f.write("""# New File

This is a new markdown file.

It has some empty lines.
""")

        subprocess.run(["git", "add", "newfile.md"], cwd=repo_dir, check=True)

        # Generate patch
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        patch_content = result.stdout

        # Save patch to testdata
        os.makedirs("testdata", exist_ok=True)
        patch_file = os.path.join("testdata", "generated_test.patch")
        with open(patch_file, "w") as f:
            f.write(patch_content)

        # Parse patch with unidiff
        patch_set = unidiff.PatchSet(patch_content.splitlines(keepends=True))

        # Verify we can parse it
        assert len(patch_set) >= 2, "Should have at least 2 modified files"

        # Reset repo to clean state
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=repo_dir, check=True)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, check=True)

        # Apply the patch using git apply
        with open(patch_file, "r") as f:
            subprocess.run(
                ["git", "apply"], cwd=repo_dir, input=f.read(), text=True, check=True
            )

        # Verify the files were modified correctly
        with open(example_py, "r") as f:
            content = f.read()
            assert "# Added some spacing" in content
            assert content.count("\n\n") > 0  # Should have empty lines

        with open(config_txt, "r") as f:
            content = f.read()
            # The empty lines should be removed
            lines = content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]
            assert len(non_empty_lines) == 4  # Comment + 3 settings

        assert os.path.exists(newfile_md), "New file should be created"

    def test_patch_reconstruction(self):
        """Test that parsed patches can be reconstructed back to original format."""
        patch_file = os.path.join("testdata", "empty_lines.patch")

        # Parse the patch
        patch_set = unidiff.PatchSet.from_filename(patch_file, encoding="utf-8")

        # Reconstruct the patch
        reconstructed = str(patch_set)

        # The reconstructed patch should be parseable again
        patch_set_2 = unidiff.PatchSet(reconstructed.splitlines(keepends=True))

        # Should have same number of files
        assert len(patch_set) == len(patch_set_2)

        # Compare file paths
        original_paths = [f.path for f in patch_set]
        reconstructed_paths = [f.path for f in patch_set_2]
        assert original_paths == reconstructed_paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
