import re
from typing import List, Tuple, Optional

class RangeFilter:
    def __init__(self, hyb_range: str, regex_pattern: str):
        self.hyb_range = hyb_range
        self.regex = re.compile(regex_pattern)
        self.start_pattern, self.end_pattern = self.hyb_range.split(':')

        # Parse start and end patterns
        self.start_parts = self._parse_pattern(self.start_pattern)
        self.end_parts = self._parse_pattern(self.end_pattern)

    def _parse_pattern(self, pattern: str) -> Optional[Tuple]:
        """Parse a pattern using the regex to extract components"""
        match = self.regex.match(pattern)
        if match:
            return match.groups()
        return None

    def _extract_numeric_part(self, text: str) -> int:
        """Extract numeric part from text like 'H1' -> 1"""
        match = re.search(r'\d+', text)
        return int(match.group()) if match else 0

    def _compare_patterns(self, file_parts: Tuple, start_parts: Tuple, end_parts: Tuple) -> bool:
        """
        Compare if file_parts falls within the range defined by start_parts and end_parts
        Based on your regex: ([A-z]+)(\d+)_(.+)_set(\d+)(.*)
        Groups: (prefix, number, middle, set_number, suffix)
        """
        if not all([file_parts, start_parts, end_parts]):
            return False

        # Extract components
        file_prefix, file_num, file_middle, file_set, file_suffix = file_parts
        start_prefix, start_num, start_middle, start_set, start_suffix = start_parts
        end_prefix, end_num, end_middle, end_set, end_suffix = end_parts

        # Convert to integers for comparison
        file_num = int(file_num)
        file_set = int(file_set)
        start_num = int(start_num)
        start_set = int(start_set)
        end_num = int(end_num)
        end_set = int(end_set)

        # Check if middle part matches (e.g., 'AER')
        if file_middle != start_middle or file_middle != end_middle:
            return False

        # Check if prefix matches
        if file_prefix != start_prefix or file_prefix != end_prefix:
            return False

        # Range logic: file falls within range if:
        # 1. Number is within start_num to end_num range
        # 2. Set number is within start_set to end_set range

        # For your example: H1_AER_set1:H3_AER_set2
        # This should include H1-H3 with sets 1-2

        num_in_range = start_num <= file_num <= end_num
        set_in_range = start_set <= file_set <= end_set

        return num_in_range and set_in_range

    def isin(self, text: str) -> bool:
        """Check if a single text/filename falls within the specified range"""
        file_parts = self._parse_pattern(text)
        if not file_parts:
            return False
        return self._compare_patterns(file_parts, self.start_parts, self.end_parts)

    def filter_files(self, filenames: List[str]) -> List[str]:
        """Filter filenames that fall within the specified range"""
        matching_files = []

        for filename in filenames:
            if self.isin(filename):
                matching_files.append(filename)

        return matching_files

# Example usage
if __name__ == "__main__":
    # Your example data
    hyb_range = 'H1_AER_set1:H3_AER_set2'
    regex = r'([A-z]+)(\d+)_(.+)_set(\d+)(.*)'
    
    # Test filenames
    test_files = [
        'H1_AER_set1',
        'H2_AER_set1', 
        'H3_AER_set1',
        'H1_AER_set2',
        'H1_MER_set2',
        'H2_AER_set2',
        'H3_AER_set2',
        'H4_AER_set1',  # Outside range (H4 > H3)
        'H1_AER_set3',  # Outside range (set3 > set2)
        'H0_AER_set1',  # Outside range (H0 < H1)
    ]
    
    # Create filter and test
    range_filter = RangeFilter(hyb_range, regex)
    matching_files = range_filter.filter_files(test_files)
    
    print(f"Range: {hyb_range}")
    print(f"Matching files: {matching_files}")
    
    # Expected output should include H1-H3 with sets 1-2
    # H1_AER_set1, H2_AER_set1, H3_AER_set1, H1_AER_set2, H2_AER_set2, H3_AER_set2
