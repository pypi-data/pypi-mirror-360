import re
from typing import List, Union, Optional


class GenericUtils:
    @staticmethod
    def string_to_string_list(value: Union[str, List[str]], delimiter: str = ",") -> List[str]:
        """
        Convert a string of values (comma-separated or custom delimiter) into a list of strings.
        """
        if isinstance(value, list):
            return [str(v).strip() for v in value]
        if not isinstance(value, str):
            return []
        return [v.strip() for v in value.split(delimiter) if v.strip()]

    @staticmethod
    def string_to_int_list(value: Union[str, List[Union[str, int]]], delimiter: str = ",") -> List[int]:
        """
        Convert a string of numbers into a list of integers.
        Supports ranges like "1,2,5-8".
        """
        if isinstance(value, list):
            return [int(v) for v in value if str(v).isdigit()]

        result = []
        for part in value.split(delimiter):
            part = part.strip()
            if "-" in part:
                try:
                    start, end = map(int, part.split("-", 1))
                    result.extend(range(start, end + 1))
                except ValueError:
                    continue
            elif part.isdigit():
                result.append(int(part))
        return result

    @staticmethod
    def expand_range(value: str) -> List[int]:
        """
        Expand a single range string like '100-6500' or '80,443,1000-1010'.
        """
        return GenericUtils.string_to_int_list(value)

    @staticmethod
    def is_numeric(value: Union[str, int, float]) -> bool:
        """
        Check if the value is numeric (int/float or digit string).
        """
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            return bool(re.match(r"^-?\d+(\.\d+)?$", value.strip()))
        return False

    @staticmethod
    def flatten(nested_list: List[Union[List, tuple, str]]) -> List:
        """
        Flattens a list of lists/tuples into a single list.
        """
        result = []
        for item in nested_list:
            if isinstance(item, (list, tuple)):
                result.extend(GenericUtils.flatten(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def unique(items: List) -> List:
        """
        Return a list with unique elements (preserves order).
        """
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def chunk_list(items: List, size: int) -> List[List]:
        """
        Split a list into chunks of a given size.
        """
        return [items[i:i + size] for i in range(0, len(items), size)]

    @staticmethod
    def safe_cast(value: any, to_type: type, default: any = None):
        """
        Safely cast a value to a given type or return default.
        """
        try:
            return to_type(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def normalize_list_str(values: List[Union[str, int, float]]) -> List[str]:
        """
        Converts all values in a list to trimmed strings.
        """
        return [str(v).strip() for v in values if str(v).strip()]

    @staticmethod
    def validate_range(value: str) -> bool:
        """
        Validate string range like '100-6500' or '22,80,443-445'
        """
        if not isinstance(value, str):
            return False
        return bool(re.fullmatch(r"^(\d+(-\d+)?)(,\d+(-\d+)?)*$", value.strip()))