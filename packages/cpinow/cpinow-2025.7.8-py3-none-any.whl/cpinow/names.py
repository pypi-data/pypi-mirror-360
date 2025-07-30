# -*- coding: utf-8 -*-
"""Names for the CPI Latam package."""

from enum import Enum


class CPIColumns(Enum):
    """Enum for the CPI columns."""

    DATE = "date"
    CPI = "cpi"
    REFERENCE_DATE = "reference_date"


class Countries(Enum):
    """Enum for the Countries columns."""

    COLOMBIA = "Colombia"
