import os
from enum import Enum, unique


@unique
class Modality(Enum):
    T1 = "T1"
    T2 = "T2"
    PD = "PD"
    fMRI = "fMRI"
    dMRI = "DWI"
    DTI = "DTI"
    HARDI = "HARDI"
    DSI = "DSI"
    ASL = "ASL"
    SCALAR = "SCALAR"
    T2_star = "T2-star"
    MRS = "MRS"
    SWI = "SWI"
    MRA = "MRA"
    CT = "CT"
    PET = "PET"
    EP = "EP"
    none = ""


class Tag(str):
    """Tag class to distinguish from regular expression in file filter.
    This class acts like a string"""

    def __init__(self, string_tag):
        self._iwd = os.getcwd()
        self._tag = string_tag

    def __str__(self):
        return self._tag

    def __repr__(self):
        return repr(self._tag)
