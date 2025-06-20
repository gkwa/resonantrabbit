#!/usr/bin/env python3
"""
Example demonstrating unidiff library parsing git patches including empty line handling.
Part of project resonantrabbit.
"""

import unidiff
import os

def analyze_patch(patch_set):
    """Analyze the patch set and print detailed information."""
    print(f"PatchSet contains {len(patch_set)} files:")
    print()
    
    for file_patch in patch_set:
        print(f"File: {file_patch.path}")
        print(f"  Source file: {file_patch.source_file}")
        print(f"  Target file: {file_patch.target_file}")
        print(f"  Is added file: {file_patch.is_added_file}")
        print(f"  Is removed file: {file_patch.is_removed_file}")
        print(f"  Is modified file: {file_patch.is_modified_file}")
        print(f"  Added lines: {file_patch.added}")
        print(f"  Removed lines: {file_patch.removed}")
        print(f"  Number of hunks: {len(file_patch)}")
        print()
        
        # Analyze each hunk
        for i, hunk in enumerate(file_patch):
            print(f"  Hunk {i + 1}:")
            print(f"    Source start: {hunk.source_start}, length: {hunk.source_length}")
            print(f"    Target start: {hunk.target_start}, length: {hunk.target_length}")
            print(f"    Section header: {hunk.section_header}")
            print()
            
            # Analyze individual lines in the hunk
            empty_line_changes = []
            for line in hunk:
                if line.value.strip() == "":  # This is an empty line or whitespace-only
                    if line.is_added:
                        empty_line_changes.append(f"    + Added empty line at target line {line.target_line_no}")
                    elif line.is_removed:
                        empty_line_changes.append(f"    - Removed empty line from source line {line.source_line_no}")
                    elif line.is_context:
                        empty_line_changes.append(f"    = Context empty line")
            
            if empty_line_changes:
                print("    Empty line changes detected:")
                for change in empty_line_changes:
                    print(change)
                print()
            
            # Show first few lines of the hunk for context
            print("    Sample lines from hunk:")
            for j, line in enumerate(hunk):
                if j >= 5:  # Limit output
                    print("    ... (more lines)")
                    break
                line_type = "+" if line.is_added else "-" if line.is_removed else " "
                line_repr = repr(line.value) if line.value.strip() == "" else line.value.rstrip()
                print(f"    {line_type} {line_repr}")
            print()

def demonstrate_empty_line_detection(patch_set):
    """Specifically demonstrate detection of empty line additions and removals."""
    print("=== Empty Line Change Analysis ===")
    print()
    
    total_empty_added = 0
    total_empty_removed = 0
    
    for file_patch in patch_set:
        file_empty_added = 0
        file_empty_removed = 0
        
        for hunk in file_patch:
            for line in hunk:
                if line.value.strip() == "":  # Empty or whitespace-only line
                    if line.is_added:
                        file_empty_added += 1
                        total_empty_added += 1
                    elif line.is_removed:
                        file_empty_removed += 1
                        total_empty_removed += 1
        
        if file_empty_added > 0 or file_empty_removed > 0:
            print(f"File {file_patch.path}:")
            print(f"  Empty lines added: {file_empty_added}")
            print(f"  Empty lines removed: {file_empty_removed}")
            print()
    
    print(f"Total across all files:")
    print(f"  Empty lines added: {total_empty_added}")
    print(f"  Empty lines removed: {total_empty_removed}")
    print()

def load_patch_from_file(patch_file_path):
    """Load a patch from a file."""
    return unidiff.PatchSet.from_filename(patch_file_path, encoding='utf-8')

def main():
    """Main function to demonstrate unidiff parsing."""
    print("=== Git Patch Parsing with Unidiff ===")
    print()
    
    # Load patch from testdata
    patch_file = os.path.join("testdata", "sample.patch")
    if os.path.exists(patch_file):
        patch_set = load_patch_from_file(patch_file)
        
        # Analyze the patch
        analyze_patch(patch_set)
        
        # Demonstrate empty line detection
        demonstrate_empty_line_detection(patch_set)
    else:
        print(f"Patch file not found: {patch_file}")
        print("Please run the tests to generate sample patch files.")

if __name__ == "__main__":
    main()
