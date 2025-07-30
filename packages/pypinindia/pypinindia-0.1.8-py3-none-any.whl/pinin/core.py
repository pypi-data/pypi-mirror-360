"""
Core functionality for Indian pincode data lookup and management.
"""

import os
import re
from functools import lru_cache
from typing import Dict, List, Optional, Union, Any
import pandas as pd

from .exceptions import InvalidPincodeError, DataNotFoundError, DataLoadError


class PincodeData:
    """
    A class for managing and querying Indian pincode data.
    
    Provides functionality to lookup pincode information including:
    - State, district, taluk information
    - Office names and types
    - Delivery status
    - Regional and divisional information
    """
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the PincodeData with CSV data.
        
        Args:
            data_file: Path to CSV file containing pincode data.
                      If None, uses the default bundled data file.
        
        Raises:
            DataLoadError: If the data file cannot be loaded
        """
        self.data: Optional[pd.DataFrame] = None
        self._data_file = data_file or self._get_default_data_file()
        self._load_data()
    
    def _get_default_data_file(self) -> str:
        """Get the path to the default bundled data file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "All_India_pincode_data.csv")
    
    def _load_data(self) -> None:
        """Load pincode data from CSV file."""
        try:
            if not os.path.exists(self._data_file):
                raise DataLoadError(f"Data file not found: {self._data_file}")
            
            # Try different encodings to handle various CSV file formats
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.data = pd.read_csv(self._data_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise DataLoadError("Could not decode CSV file with any supported encoding")
            
            # Validate required columns
            required_columns = [
                'pincode', 'officename', 'statename', 'districtname', 
                'taluk', 'officetype', 'Deliverystatus'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            if missing_columns:
                raise DataLoadError(f"Missing required columns: {missing_columns}")
            
            # Convert pincode to string for consistent handling
            self.data['pincode'] = self.data['pincode'].astype(str)
            
        except pd.errors.EmptyDataError:
            raise DataLoadError("Data file is empty", self._data_file)
        except pd.errors.ParserError as e:
            raise DataLoadError(f"Failed to parse CSV file: {str(e)}", self._data_file)
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading data: {str(e)}", self._data_file)
    
    def _validate_pincode(self, pincode: Union[str, int]) -> str:
        """
        Validate and normalize pincode format.
        
        Args:
            pincode: The pincode to validate (string or integer)
            
        Returns:
            Normalized pincode as string
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
        """
        # Convert to string and remove any whitespace
        pincode_str = str(pincode).strip()
        
        # Check if it's a valid 6-digit pincode
        if not re.match(r'^\d{6}$', pincode_str):
            raise InvalidPincodeError(pincode_str)
        
        return pincode_str
    
    def _get_info_field(self, pincode: Union[str, int], field_name: str) -> Union[str, List[str]]:
        """
        Helper to get a specific field or list of fields for a pincode.
        """
        info = self.get_pincode_info(pincode)
        if field_name == 'officename':
            return [str(office[field_name]) for office in info]
        return str(info[0][field_name])

    def get_pincode_info(self, pincode: Union[str, int]) -> List[Dict[str, Any]]:
        """
        Get complete information for a pincode.
        
        Args:
            pincode: The pincode to lookup
            
        Returns:
            List of dictionaries containing pincode information.
            Multiple entries may exist for a single pincode.
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If no data found for the pincode
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        pincode_str = self._validate_pincode(pincode)
        
        # Filter data for the given pincode
        filtered_data = self.data[self.data['pincode'] == pincode_str]
        
        if filtered_data.empty:
            raise DataNotFoundError(pincode_str)
        
        # Convert to list of dictionaries
        return filtered_data.to_dict('records')  # type: ignore
    
    def get_state(self, pincode: Union[str, int]) -> str:
        """
        Get the state name for a pincode.
        
        Args:
            pincode: The pincode to lookup
            
        Returns:
            State name
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If no data found for the pincode
        """
        return str(self._get_info_field(pincode, 'statename'))
    
    def get_district(self, pincode: Union[str, int]) -> str:
        """
        Get the district name for a pincode.
        
        Args:
            pincode: The pincode to lookup
            
        Returns:
            District name
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If no data found for the pincode
        """
        return str(self._get_info_field(pincode, 'districtname'))
    
    def get_taluk(self, pincode: Union[str, int]) -> str:
        """
        Get the taluk name for a pincode.
        
        Args:
            pincode: The pincode to lookup
            
        Returns:
            Taluk name
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If no data found for the pincode
        """
        return str(self._get_info_field(pincode, 'taluk'))
    
    def get_offices(self, pincode: Union[str, int]) -> List[str]:
        """
        Get all office names for a pincode.
        
        Args:
            pincode: The pincode to lookup
            
        Returns:
            List of office names
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If no data found for the pincode
        """
        return self._get_info_field(pincode, 'officename') # type: ignore
    
    def search_by_state(self, state_name: str) -> List[str]:
        """
        Get all pincodes for a given state.
        
        Args:
            state_name: Name of the state (case-insensitive)
            
        Returns:
            List of unique pincodes in the state
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        # Case-insensitive search
        filtered_data = self.data[
            self.data['statename'].str.upper() == state_name.upper()
        ]
        
        return sorted(filtered_data['pincode'].unique().tolist())
    
    def search_by_district(self, district_name: str, state_name: Optional[str] = None) -> List[str]:
        """
        Get all pincodes for a given district.
        
        Args:
            district_name: Name of the district (case-insensitive)
            state_name: Optional state name to narrow down search
            
        Returns:
            List of unique pincodes in the district
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        # Case-insensitive search
        filtered_data = self.data[
            self.data['districtname'].str.upper() == district_name.upper()
        ]
        
        if state_name:
            filtered_data = filtered_data[
                filtered_data['statename'].str.upper() == state_name.upper()
            ]
        
        return sorted(filtered_data['pincode'].unique().tolist())
    
    def search_by_office(self, office_name: str) -> List[Dict[str, Any]]:
        """
        Search for pincodes by office name (partial match).
        
        Args:
            office_name: Office name to search for (case-insensitive, partial match)
            
        Returns:
            List of dictionaries containing matching office information
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        # Case-insensitive partial match
        filtered_data = self.data[
            self.data['officename'].str.upper().str.contains(office_name.upper(), na=False)
        ]
        
        return filtered_data.to_dict('records')  # type: ignore
    
    def get_states(self) -> List[str]:
        """
        Get list of all states in the dataset.
        
        Returns:
            Sorted list of unique state names
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        return sorted(self.data['statename'].unique().tolist())
    
    def get_districts(self, state_name: Optional[str] = None) -> List[str]:
        """
        Get list of all districts, optionally filtered by state.
        
        Args:
            state_name: Optional state name to filter districts
            
        Returns:
            Sorted list of unique district names
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        if state_name:
            filtered_data = self.data[
                self.data['statename'].str.upper() == state_name.upper()
            ]
            return sorted(filtered_data['districtname'].unique().tolist())
        
        return sorted(self.data['districtname'].unique().tolist())
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get basic statistics about the pincode dataset.
        
        Returns:
            Dictionary containing dataset statistics
        """
        if self.data is None:
            raise DataLoadError("Data not loaded")
        
        return {
            'total_records': len(self.data),
            'unique_pincodes': self.data['pincode'].nunique(),
            'unique_states': self.data['statename'].nunique(),
            'unique_districts': self.data['districtname'].nunique(),
            'unique_offices': self.data['officename'].nunique(),
        }


@lru_cache(maxsize=1)
def _get_default_instance() -> PincodeData:
    """Get or create the default PincodeData instance."""
    return PincodeData()


# Convenience functions
def get_pincode_info(pincode: Union[str, int]) -> List[Dict[str, Any]]:
    """
    Convenience function to get complete pincode information.
    
    Args:
        pincode: The pincode to lookup
        
    Returns:
        List of dictionaries containing pincode information
    """
    return _get_default_instance().get_pincode_info(pincode)


def get_state(pincode: Union[str, int]) -> str:
    """
    Convenience function to get state name for a pincode.
    
    Args:
        pincode: The pincode to lookup
        
    Returns:
        State name
    """
    return _get_default_instance().get_state(pincode)


def get_district(pincode: Union[str, int]) -> str:
    """
    Convenience function to get district name for a pincode.
    
    Args:
        pincode: The pincode to lookup
        
    Returns:
        District name
    """
    return _get_default_instance().get_district(pincode)


def get_taluk(pincode: Union[str, int]) -> str:
    """
    Convenience function to get taluk name for a pincode.
    
    Args:
        pincode: The pincode to lookup
        
    Returns:
        Taluk name
    """
    return _get_default_instance().get_taluk(pincode)


def get_offices(pincode: Union[str, int]) -> List[str]:
    """
    Convenience function to get office names for a pincode.
    
    Args:
        pincode: The pincode to lookup
        
    Returns:
        List of office names
    """
    return _get_default_instance().get_offices(pincode)


def search_by_state(state_name: str) -> List[str]:
    """
    Convenience function to search pincodes by state.
    
    Args:
        state_name: Name of the state
        
    Returns:
        List of pincodes in the state
    """
    return _get_default_instance().search_by_state(state_name)


def search_by_district(district_name: str, state_name: Optional[str] = None) -> List[str]:
    """
    Convenience function to search pincodes by district.
    
    Args:
        district_name: Name of the district
        state_name: Optional state name to narrow search
        
    Returns:
        List of pincodes in the district
    """
    return _get_default_instance().search_by_district(district_name, state_name)


def get_states() -> List[str]:
    """
    Convenience function to get all states.
    
    Returns:
        List of all state names
    """
    return _get_default_instance().get_states()


def get_districts(state_name: Optional[str] = None) -> List[str]:
    """
    Convenience function to get all districts.
    
    Args:
        state_name: Optional state name to filter districts
        
    Returns:
        List of district names
    """
    return _get_default_instance().get_districts(state_name)
