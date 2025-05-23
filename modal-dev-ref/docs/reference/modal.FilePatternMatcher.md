# modal.FilePatternMatcher

    
    
    class FilePatternMatcher(modal.file_pattern_matcher._AbstractPatternMatcher)

Copy

Allows matching file Path objects against a list of patterns.

**Usage:**

    
    
    from pathlib import Path
    from modal import FilePatternMatcher
    
    matcher = FilePatternMatcher("*.py")
    
    assert matcher(Path("foo.py"))
    
    # You can also negate the matcher.
    negated_matcher = ~matcher
    
    assert not negated_matcher(Path("foo.py"))

Copy

    
    
    def __init__(self, *pattern: str) -> None:

Copy

Initialize a new FilePatternMatcher instance.

Args: pattern (str): One or more pattern strings.

Raises: ValueError: If an illegal exclusion pattern is provided.

## from_file

    
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "FilePatternMatcher":

Copy

Initialize a new FilePatternMatcher instance from a file.

The patterns in the file will be read lazily when the matcher is first used.

Args: file_path (Path): The path to the file containing patterns.

**Usage:**

    
    
    from modal import FilePatternMatcher
    
    matcher = FilePatternMatcher.from_file("/path/to/ignorefile")

Copy

