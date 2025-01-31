"""
This module provides utility functions for loading and caching JSON data, 
designed to read JSON files, and store their contents.
It is intended for use across multiple modules 
to ensure efficient loading and retrieval of JSON data.

### Key Features:
- **JSON Loading and Caching**:
    - Loads JSON data from files and stores it in an internal cache for reuse.
    - Returns cached data if the same file is requested again, preventing multiple reads.
  
- **Error Handling**:
    - Handles `FileNotFoundError` and `JSONDecodeError` exceptions, ensuring the program 
      continues running even if a file is missing or corrupted.

- **Cache Management**:
    - Provides a method to clear the cache for specific files or clear the entire cache.

### Classes:
- **`JsonLoader`**:
    A class for loading and caching JSON files with error handling. 

### Dependencies:
- **`json`**: For parsing JSON data from files.
- **`typing`**: For type hinting and function signatures.
"""



import json

from typing import Optional



class JsonLoader:
    """
    A utility class for loading and caching JSON files with error handling.
    This class helps optimize the loading of JSON files by caching their contents.

    Attributes:
    -----------
        _cache : dict[str, dict]
            Stores the cached JSON data.
    """
    _cache: dict[str, dict] = {}
    
    @classmethod
    def load_json(cls, filename: str) -> dict[str, str]:
        """
        Loads JSON data from the specified file and caches it for future use.

        This method checks if the JSON data for the given filename is already in the cache.
        If not, it attempts to load the file and parse its contents. If successful, the data 
        is stored in the cache. If the file cannot be found or is invalid, an empty dictionary 
        is returned.

        Params:
        -------
            filename : str
                The path to the JSON file to load.
        """
        if filename not in cls._cache:
            try:
                with open(filename, "r") as f:
                    cls._cache[filename] = json.load(f)
            except FileNotFoundError:
                cls._cache[filename] = {}
                print(f"Unable to find file")
            except json.JSONDecodeError:
                cls._cache[filename] = {}
                print(f"Unable to load file")

        return cls._cache[filename]

    @classmethod
    def clear_cache(cls, filename: Optional[str]=None):
        """
        Clears the cache for a specific file or clears the entire cache if no filename is provided.

        Params:
            filename : str
                The filename for which the cache should be cleared. 
                If no filename is provided, all cache data is cleared.
        """
        if filename:
            cls._cache.pop(filename, None)
        else:
            cls._cache.clear()
