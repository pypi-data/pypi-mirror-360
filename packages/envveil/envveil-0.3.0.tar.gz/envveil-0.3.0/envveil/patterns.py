import glob
import os
from typing import List, Set

def find_files_by_patterns(patterns: List[str]) -> Set[str]:
    """
    Given a list of glob patterns, return a set of matching file paths.
    Patterns can include wildcards and recursive globs (e.g., '**/*.py').
    """
    matched_files = set()
    for pattern in patterns:
        expanded_pattern = os.path.expandvars(os.path.expanduser(pattern))
        recursive = '**' in expanded_pattern
        for path in glob.glob(expanded_pattern, recursive=recursive):
            if os.path.isfile(path):
                matched_files.add(path)
    return matched_files 