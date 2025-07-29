"""Common types & data used by other modules within the jetto_tools package"""

import dataclasses
import enum


@dataclasses.dataclass()
class TimeConfig:
    """Time configuration for a JETTO run"""
    start_time: float
    end_time: float
    n_esco_times: int
    n_output_profile_times: int


class Driver(enum.Enum):
    """Type representing the driver used to run JETTO

    Mimics the 'Driver type' drop-down box in the JETTO 'Job Process' panel in JAMS
    """
    Std = 'Standard, native I/O only'
    IMAS = 'IMAS(Python), native + IDS I/O'


@dataclasses.dataclass
class IMASDB:
    """Type representing a reference to an IMAS run DB"""
    user: str
    machine: str
    shot: int
    run: int


@dataclasses.dataclass
class CatalogueId:
    """Type representing a reference to a catalogue entry"""
    owner: str
    code: str
    machine: str
    shot: int
    date: str
    seq: int
