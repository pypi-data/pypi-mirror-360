"""
pypinindia - Indian Pincodes and related Information

A modern Python library for Indian pincode lookup and geographical information.

This library provides comprehensive pincode data lookup functionality for:
- State, district, and taluk information
- Office names and types
- Delivery status information
- Search and filtering capabilities

Usage:
    from pinin import get_pincode_info, get_state, PincodeData
    
    # Quick pincode lookup
    info = get_pincode_info("110001")
    state = get_state("110001")
    
    # Using PincodeData class
    pincode_data = PincodeData()
    district = pincode_data.get_district("110001")
"""

from .core import (
    PincodeData,
    get_pincode_info,
    get_state,
    get_district,
    get_taluk,
    get_offices,
    search_by_state,
    search_by_district,
    get_states,
    get_districts,
)
from .exceptions import (
    PininError,
    InvalidPincodeError,
    DataNotFoundError,
    DataLoadError,
)

__version__ = "0.1.4"
__author__ = "Raja CSP Raman"
__email__ = "raja.csp@gmail.com"

__all__ = [
    "PincodeData",
    "get_pincode_info",
    "get_state",
    "get_district",
    "get_taluk",
    "get_offices",
    "search_by_state",
    "search_by_district",
    "get_states",
    "get_districts",
    "PininError",
    "InvalidPincodeError",
    "DataNotFoundError",
    "DataLoadError",
]
