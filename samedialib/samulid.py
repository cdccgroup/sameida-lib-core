"""samedialib.samulid.py

Ulid features of synesthetic aesthetic media.
"""
import ulid
import time
from dataclasses import dataclass, field
from typing import Any, AnyStr, Union


def new_sam_ulid(ts_in: float=time.time()):
    """Return a ulid value seeded with timestamp"""
    sam_ulid = ulid.from_timestamp(ts_in)
    return sam_ulid


@dataclass
class SAMUlid:
    """A class encapsulating the synesthetic aesthetic media ulid

    The SAMUlid is an immutable class that stores a unique ulid value.

    :param sam_ulid.
    :Type seed: Union[ulid, str(26)]
    """
    sam_ulid: ulid
    sam_ulid_sub_dir: field(init=False,compare=False)
    sam_ulid_seed_time: field(init=False,compare=False)


    
