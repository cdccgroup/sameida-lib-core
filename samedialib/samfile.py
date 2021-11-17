"""samedia_lib_core.samutils.samfile.py

This module contains utility functions and classes used during
file manipulation by synesthetic aesthetic media processes.
"""

from os import EX_CANTCREAT, path, stat, stat_result
from dataclasses import dataclass, field
from dateutil.parser import parse
from typing import Any, AnyStr, Union, Dict
import mimetypes
import datetime
import time

ENV_DATE_RANGE_LOW = datetime.datetime(2019,12,31,11,59,59).timestamp()


def validate_path(path_in):
    """Check if path_in exists and return bool"""
    return path.exists(path_in)


def get_timestamp_from_string(string_in: str):
    """Parse arg string_in and return any matching date value as timestamp"""
    try: 
        res = parse(string_in, fuzzy_with_tokens=True)
        if valid_timestamp(res[0].timestamp()):
            return res[0].timestamp()

    except ValueError:
        return False

    return False


def valid_timestamp(ts_in: float=False, low: float=0, high: float=time.time()):
    """Test if ts_in is a valid float, and if it is in range [default: low=0, high=current timestamp]"""
    
    """If arg ts_in does not represent a float, return False."""
    try:
        float(ts_in)
    except ValueError:
        return False

    """Ensure ts_in is within the valid range."""
    try:
        if low <= ts_in <= high:
            return f"{ts_in}"
    except Exception:
        return False

    return False


def get_floor_value_key(**kwargs):
    """Return the key cooresponding with the lowest value in kwargs"""
    try:
        min_key = kwargs[min(kwargs.keys(), key=(lambda k: kwargs[k]))]
        return min_key
    except Exception:
        return False


@dataclass
class FileName:
    """A class that represents a file name.
    
    Given string (basename) get details about the filename:
    (name with no extension, extension, mime_type)

    :param basename: A file name (file name. eg. "foo.bar")
    :type basename: str
    """

    basename: str
    no_ext: str = field(init=False,compare=False)
    ext: str = field(init=False,compare=False)
    mime_type: str = field(init=False)

    def __post_init__(self):
        """Using required basename, determine secondary attributes"""

        self._analyze()

    def _analyze(self):
        """Determine secondary attributes"""

        self.no_ext, self.ext = path.splitext(self.basename)
        self.mime_type = mimetypes.guess_type(self.basename)

    def set_basename(self, new_basename: str):
        """Set basename attribute and determine secondary attributes"""

        self.basename = new_basename
        self._analyze()        



@dataclass
class FilePath:
    """A class that represents a file path.
    
    Given a file path string, the class will validate
    the path and gather relevant information about the
    path.

    Param: path = str 
    Attributes:
      - path
      - path_type
      - folder
      - file_name
    """

    path: str
    path_type: str = field(default=None,init=False)
    folder: str = field(init=False,compare=False)
    file_name: FileName = field(default=None,init=False)
    _is_valid: bool = field(default=False,init=False)
    _is_file: bool = field(default=False,init=False)
    _is_dir: bool = field(default=False,init=False)
    

    def __post_init__(self):
        """Parse input arg path and populate secondary attributes."""

        self.path_type = self._parse_path()

    
    def _parse_path(self) -> str:
        """From path determine if path points to a valid resource,
        split filename and instantiate FileName object, determine 
        if path is a file or directory and get file_stats
        """

        self._is_valid = path.exists(self.path)
        if not self._is_valid:
            return "ERR_INVALID_PATH"

        self._is_dir = path.isdir(self.path)
        if self._is_dir:
            self.folder = self.path
            return "FOLDER"

        self._is_file = path.isfile(self.path)
        if not self._is_file:
            return "ERR_FILE_NOT_FOUND"
        
        fn = ""
        self.folder, fn = path.split(self.path)
        if len(fn) < 1:
            return "ERR_FILENAME"
            
        self.file_name = FileName(fn)
        return "FILE"


@dataclass
class SAMLocalFile:
    """Base class for synesthetic aesthetic media digital files.

    Base class representing the attributes of a digital file.

    param: path_in: path to a file
    Type: path_in: str
    """

    _file_path_in: str
    file_path: Any=field(default=None,init=False) 
    file_stats: stat_result=field(default=None,init=False)
    file_times: Dict=field(default=None,init=False)
    file_floor_time: float=field(default=None, init=False)
    file_metadata: AnyStr=field(default=None,init=False,compare=False)
    
    def __post_init__(self):
        """Instantiate FilePath object, get secondary information."""
        try:
            self.file_path = FilePath(self._file_path_in)
        except Exception:
            return False
        
        self.process_stats()

        
    def process_stats(self):
        """given a valid file path, get stat_result and set secondary attributes.
        
        If the path returns a stat_result, set:
        - file_stats
        - floor_time
        - file_size
        """

        try:
            date_in_name = get_timestamp_from_string(self.file_path.file_name)
        except Exception:
            date_in_name = False
        
        self.file_stats = stat(self.path)
        self.set_file_times(date_in_name)
        self.file_floor_time = self.file_times[get_floor_value_key(**self.file_times)]
        self.file_metadata = {"metadata": "Goes Here"}


    def set_file_times(self, date_in_name=False):
        t = {}
        if self.file_stats.st_atime_ns: t["atime"] = self.file_stats.st_atime_ns
        if self.file_stats.st_ctime_ns: t["ctime"] = self.file_stats.st_ctime_ns
        if self.file_stats.st_mtime_ns: t["mtime"] = self.file_stats.st_mtime_ns
        if date_in_name: t["name_time"] = date_in_name
        t["process_time"] = time.time()

        self.file_times = t
