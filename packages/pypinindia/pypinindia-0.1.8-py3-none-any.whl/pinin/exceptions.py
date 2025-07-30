"""
Custom exceptions for the pypinindia library.
"""

from typing import List, Optional


class PininError(Exception):
    """Base exception class for pypinindia library."""
    pass


class InvalidPincodeError(PininError):
    """Raised when an invalid pincode is provided."""
    
    def __init__(self, pincode: str, message: Optional[str] = None):
        self.pincode = pincode
        
        if message:
            full_message = message
        else:
            full_message = f"Invalid pincode: '{pincode}'. Pincode must be a 6-digit number."
        
        super().__init__(full_message)


class DataNotFoundError(PininError):
    """Raised when pincode data is not found."""
    
    def __init__(self, pincode: str, message: Optional[str] = None):
        self.pincode = pincode
        
        if message:
            full_message = message
        else:
            full_message = f"No data found for pincode: '{pincode}'"
        
        super().__init__(full_message)


class DataLoadError(PininError):
    """Raised when pincode data fails to load."""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        
        full_message = f"Failed to load pincode data: {message}"
        if file_path:
            full_message += f" (file: {file_path})"
        
        super().__init__(full_message)
