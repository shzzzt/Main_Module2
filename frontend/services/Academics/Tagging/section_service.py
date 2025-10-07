#  model generated file to work with json data while being ready for django rest calls (gikapoy nako hehe)

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from copy import deepcopy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectionServiceError(Exception):
    """Base exception for section service errors."""
    pass


class SectionNotFoundError(SectionServiceError):
    """Raised when a section is not found."""
    pass


class SectionValidationError(SectionServiceError):
    """Raised when section data fails validation."""
    pass


class SectionStorageError(SectionServiceError):
    """Raised when there's an error reading/writing data."""
    pass


class SectionService:
    """
    Service layer for section data operations.
    
    This class abstracts data persistence operations for sections. Currently
    implements JSON file storage, but designed for easy migration to Django
    REST API integration.
    
    Architecture Pattern:
        Controller → Service → Data Store (JSON/API)
    
    Attributes:
        json_file (str): Path to the JSON database file
        _cache (Dict): In-memory cache of loaded data (future: Redis)
        _required_fields (set): Required fields for section validation
    """
    
    # Required fields for a valid section
    REQUIRED_FIELDS = {
        'section', 'program', 'curriculum', 'year', 
        'capacity', 'type', 'remarks'
    }
    
    # Valid values for certain fields
    VALID_TYPES = {'Lecture', 'Laboratory', 'Hybrid'}
    VALID_YEARS = {'1st', '2nd', '3rd', '4th', '5th'}
    
    def __init__(self, json_file: str = "data/sections.json"):
        """
        Initialize the section service.
        
        Args:
            json_file: Path to JSON database file (default: data/sections.json)
                      Future: Will become API base URL
        
        Design Note:
            The json_file parameter will be replaced with api_base_url when
            migrating to Django backend. Method signatures remain unchanged.
        """
        self.json_file = json_file
        self._cache: Optional[Dict] = None
        self._ensure_data_file_exists()
        
        # FUTURE: For Django API integration
        # self.api_base_url = api_base_url
        # self.session = requests.Session()
        # self.session.headers.update({'Content-Type': 'application/json'})
        
        logger.info(f"SectionService initialized with file: {json_file}")
    
    def _ensure_data_file_exists(self) -> None:
        """
        Ensure the JSON data file and directory exist.
        
        Creates the data directory and initializes an empty JSON structure
        if the file doesn't exist.
        
        Raises:
            SectionStorageError: If file/directory cannot be created
        """
        try:
            # Create directory if it doesn't exist
            Path(self.json_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty file structure if file doesn't exist
            if not os.path.exists(self.json_file):
                initial_data = {
                    "metadata": {
                        "last_updated": datetime.now().isoformat(),
                        "version": "1.0",
                        "next_id": 1
                    },
                    "sections": []
                }
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created new sections database: {self.json_file}")
        
        except Exception as e:
            error_msg = f"Failed to initialize data file: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
    
    def _load_data(self) -> Dict:
        """
        Load section data from JSON file.
        
        Implements caching to reduce file I/O operations. Cache is invalidated
        after write operations.
        
        Returns:
            Dict: Complete JSON structure with metadata and sections
        
        Raises:
            SectionStorageError: If file cannot be read or JSON is invalid
        
        Future Implementation:
            Will be replaced with GET request to /api/sections/
            Cache will use Redis with TTL
        """
        # Return cached data if available
        if self._cache is not None:
            return deepcopy(self._cache)
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate basic structure
            if 'metadata' not in data or 'sections' not in data:
                raise SectionStorageError("Invalid JSON structure")
            
            # Cache the loaded data
            self._cache = deepcopy(data)
            logger.debug(f"Loaded {len(data['sections'])} sections from file")
            return deepcopy(data)
        
        except FileNotFoundError:
            error_msg = f"Data file not found: {self.json_file}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
        
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in data file: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
        
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
    
    def _save_data(self, data: Dict) -> None:
        """
        Save section data to JSON file atomically.
        
        Uses atomic write pattern (write to temp file, then rename) to prevent
        data corruption if the operation is interrupted.
        
        Args:
            data: Complete JSON structure to save
        
        Raises:
            SectionStorageError: If file cannot be written
        
        Implementation Details:
            1. Write to temporary file
            2. Sync to disk (flush)
            3. Atomically rename temp file to actual file
            4. Invalidate cache
        
        Future Implementation:
            Will be replaced with POST/PUT/DELETE requests to Django API
            Cache invalidation will notify Redis
        """
        temp_file = f"{self.json_file}.tmp"
        
        try:
            # Update metadata timestamp
            data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Write to temporary file
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Ensure written to disk
            
            # Atomic rename
            os.replace(temp_file, self.json_file)
            
            # Invalidate cache
            self._cache = None
            
            logger.debug(f"Saved {len(data['sections'])} sections to file")
        
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            error_msg = f"Error saving data: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
    
    def _validate_section_data(self, data: Dict, is_update: bool = False) -> None:
        """
        Validate section data at storage level.
        
        Checks data integrity, required fields, data types, and value ranges.
        This is storage-level validation; business rule validation happens
        in the controller layer.
        
        Args:
            data: Section data dictionary to validate
            is_update: If True, allows missing fields (partial updates)
        
        Raises:
            SectionValidationError: If validation fails with specific reason
        
        Validation Rules:
            - Required fields present (unless is_update=True)
            - capacity is positive integer
            - type is valid value
            - year is valid value
            - String fields are non-empty
        """
        # Check required fields
        if not is_update:
            missing_fields = self.REQUIRED_FIELDS - set(data.keys())
            if missing_fields:
                raise SectionValidationError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
        
        # Validate capacity
        if 'capacity' in data:
            try:
                capacity = int(data['capacity'])
                if capacity <= 0:
                    raise SectionValidationError(
                        "Capacity must be a positive integer"
                    )
            except (ValueError, TypeError):
                raise SectionValidationError(
                    "Capacity must be a valid integer"
                )
        
        # Validate type
        if 'type' in data and data['type'] not in self.VALID_TYPES:
            raise SectionValidationError(
                f"Invalid type. Must be one of: {', '.join(self.VALID_TYPES)}"
            )
        
        # Validate year
        if 'year' in data and data['year'] not in self.VALID_YEARS:
            raise SectionValidationError(
                f"Invalid year. Must be one of: {', '.join(self.VALID_YEARS)}"
            )
        
        # Validate non-empty strings
        string_fields = ['section', 'program', 'curriculum']
        for field in string_fields:
            if field in data:
                if not isinstance(data[field], str) or not data[field].strip():
                    raise SectionValidationError(
                        f"{field.capitalize()} must be a non-empty string"
                    )
    
    def _generate_next_id(self, data: Dict) -> int:
        """
        Generate the next available ID for a new section.
        
        Uses metadata.next_id and increments it. Also validates that the
        generated ID doesn't already exist (defensive programming).
        
        Args:
            data: Current data structure with metadata
        
        Returns:
            int: Next available ID
        
        Future Implementation:
            Not needed - Django will auto-generate IDs via database
        """
        next_id = data['metadata']['next_id']
        
        # Defensive check: ensure ID doesn't already exist
        existing_ids = {section['id'] for section in data['sections']}
        while next_id in existing_ids:
            next_id += 1
        
        data['metadata']['next_id'] = next_id + 1
        return next_id
    
    # ========================================================================
    # PUBLIC CRUD METHODS
    # ========================================================================
    
    def get_all(self, token: str = None) -> List[Dict]:
        """
        Retrieve all sections from the database.
        
        Current Implementation:
            Loads from JSON file and returns sections list
        
        Future Implementation:
            GET request to /api/sections/
            Headers: {'Authorization': f'Bearer {token}'}
            Response: Paginated list of sections
        
        Args:
            token: Authentication token (unused in current implementation,
                   required for future API calls)
        
        Returns:
            List[Dict]: List of all section dictionaries, each containing:
                - id (int): Unique identifier
                - section (str): Section name (e.g., "3A")
                - program (str): Program name
                - curriculum (str): Curriculum year
                - year (str): Year level
                - capacity (int): Maximum students
                - type (str): Section type
                - remarks (str): Additional notes
                - created_at (str): ISO timestamp
                - updated_at (str): ISO timestamp
        
        Raises:
            SectionStorageError: If data cannot be loaded
        
        Example:
            >>> service = SectionService()
            >>> sections = service.get_all()
            >>> print(f"Found {len(sections)} sections")
            Found 5 sections
        """
        try:
            data = self._load_data()
            logger.info(f"Retrieved {len(data['sections'])} sections")
            return deepcopy(data['sections'])
        
        except Exception as e:
            logger.error(f"Error retrieving sections: {str(e)}")
            raise
    
    def get_by_id(self, section_id: int, token: str = None) -> Optional[Dict]:
        """
        Retrieve a specific section by ID.
        
        Current Implementation:
            Searches through JSON array for matching ID
        
        Future Implementation:
            GET request to /api/sections/{section_id}/
            Headers: {'Authorization': f'Bearer {token}'}
        
        Args:
            section_id: Unique identifier of the section
            token: Authentication token (for future API calls)
        
        Returns:
            Dict: Section data if found, None if not found
        
        Raises:
            SectionStorageError: If data cannot be loaded
        
        Example:
            >>> section = service.get_by_id(1)
            >>> if section:
            ...     print(f"Section: {section['section']}")
            Section: 3A
        """
        try:
            data = self._load_data()
            for section in data['sections']:
                if section['id'] == section_id:
                    logger.debug(f"Found section with ID {section_id}")
                    return deepcopy(section)
            
            logger.warning(f"Section with ID {section_id} not found")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving section {section_id}: {str(e)}")
            raise
    
    def create(self, section_data: Dict, token: str = None) -> Dict:
        """
        Create a new section in the database.
        
        Current Implementation:
            1. Load current data from JSON
            2. Validate section data
            3. Generate new ID
            4. Add timestamps
            5. Append to sections list
            6. Save atomically to JSON file
            7. Return created section with ID
        
        Future Implementation:
            POST request to /api/sections/
            Headers: {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            Body: section_data (JSON)
            Response: Created section with server-generated ID
        
        Data Flow:
            Controller validates business rules
                ↓
            Service validates data integrity
                ↓
            Generate ID and timestamps
                ↓
            Atomic file write
                ↓
            Return created section
        
        Args:
            section_data: Dictionary containing section fields:
                - section (str): Section name (required)
                - program (str): Program name (required)
                - curriculum (str): Curriculum year (required)
                - year (str): Year level (required)
                - capacity (int): Maximum capacity (required)
                - type (str): Section type (required)
                - remarks (str): Additional notes (required)
            token: Authentication token (for future API calls)
        
        Returns:
            Dict: The created section with assigned ID and timestamps
        
        Raises:
            SectionValidationError: If data fails validation
            SectionStorageError: If section cannot be saved
        
        Example:
            >>> new_section = service.create({
            ...     'section': '4B',
            ...     'program': 'BS Information Technology',
            ...     'curriculum': '2023-2024',
            ...     'year': '4th',
            ...     'capacity': 35,
            ...     'type': 'Lecture',
            ...     'remarks': 'Regular'
            ... })
            >>> print(f"Created section with ID: {new_section['id']}")
            Created section with ID: 6
        """
        try:
            # Validate data
            self._validate_section_data(section_data, is_update=False)
            
            # Load current data
            data = self._load_data()
            
            # Create new section with metadata
            new_section = deepcopy(section_data)
            new_section['id'] = self._generate_next_id(data)
            new_section['created_at'] = datetime.now().isoformat()
            new_section['updated_at'] = datetime.now().isoformat()
            
            # Add to sections list
            data['sections'].append(new_section)
            
            # Save atomically
            self._save_data(data)
            
            logger.info(f"Created section: {new_section['section']} "
                       f"(ID: {new_section['id']})")
            
            return deepcopy(new_section)
        
        except (SectionValidationError, SectionStorageError):
            raise
        
        except Exception as e:
            error_msg = f"Unexpected error creating section: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
    
    def update(self, section_id: int, section_data: Dict, 
               token: str = None) -> Dict:
        """
        Update an existing section.
        
        Current Implementation:
            1. Load current data
            2. Find section by ID
            3. Validate update data (allows partial updates)
            4. Merge new data with existing data
            5. Update timestamp
            6. Save atomically
            7. Return updated section
        
        Future Implementation:
            PUT request to /api/sections/{section_id}/
            or PATCH for partial updates
        
        Args:
            section_id: ID of section to update
            section_data: Dictionary with fields to update (partial OK)
            token: Authentication token (for future API calls)
        
        Returns:
            Dict: Updated section data
        
        Raises:
            SectionNotFoundError: If section doesn't exist
            SectionValidationError: If data fails validation
            SectionStorageError: If section cannot be saved
        
        Example:
            >>> updated = service.update(1, {'capacity': 45})
            >>> print(f"New capacity: {updated['capacity']}")
            New capacity: 45
        """
        try:
            # Validate update data
            self._validate_section_data(section_data, is_update=True)
            
            # Load current data
            data = self._load_data()
            
            # Find section to update
            section_index = None
            for i, section in enumerate(data['sections']):
                if section['id'] == section_id:
                    section_index = i
                    break
            
            if section_index is None:
                raise SectionNotFoundError(
                    f"Section with ID {section_id} not found"
                )
            
            # Update section data
            existing_section = data['sections'][section_index]
            existing_section.update(section_data)
            existing_section['updated_at'] = datetime.now().isoformat()
            
            # Don't allow ID or created_at to be changed
            existing_section['id'] = section_id
            if 'created_at' not in existing_section:
                existing_section['created_at'] = datetime.now().isoformat()
            
            # Save atomically
            self._save_data(data)
            
            logger.info(f"Updated section ID {section_id}")
            
            return deepcopy(existing_section)
        
        except (SectionNotFoundError, SectionValidationError, 
                SectionStorageError):
            raise
        
        except Exception as e:
            error_msg = f"Unexpected error updating section: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
    
    def delete(self, section_id: int, token: str = None) -> bool:
        """
        Delete a section from the database.
        
        Current Implementation:
            1. Load current data
            2. Find and remove section
            3. Save atomically
            4. Return success status
        
        Future Implementation:
            DELETE request to /api/sections/{section_id}/
            Consider soft delete (archive) vs hard delete
        
        WARNING:
            This performs a hard delete. Controller should check for
            related classes before calling this method.
        
        Args:
            section_id: ID of section to delete
            token: Authentication token (for future API calls)
        
        Returns:
            bool: True if deleted, False if not found
        
        Raises:
            SectionStorageError: If deletion fails
        
        Example:
            >>> if service.delete(5):
            ...     print("Section deleted")
            ... else:
            ...     print("Section not found")
            Section deleted
        """
        try:
            # Load current data
            data = self._load_data()
            
            # Find section to delete
            original_count = len(data['sections'])
            data['sections'] = [
                s for s in data['sections'] if s['id'] != section_id
            ]
            
            # Check if anything was deleted
            if len(data['sections']) == original_count:
                logger.warning(f"Section with ID {section_id} not found")
                return False
            
            # Save atomically
            self._save_data(data)
            
            logger.info(f"Deleted section ID {section_id}")
            return True
        
        except Exception as e:
            error_msg = f"Error deleting section {section_id}: {str(e)}"
            logger.error(error_msg)
            raise SectionStorageError(error_msg)
    
    def search(self, filters: Dict, token: str = None) -> List[Dict]:
        """
        Search sections by multiple criteria.
        
        Current Implementation:
            Filters sections in memory based on provided criteria
        
        Future Implementation:
            GET request to /api/sections/?program=...&year=...
            Server-side filtering with database queries
        
        Args:
            filters: Dictionary of field:value pairs to match
            token: Authentication token (for future API calls)
        
        Returns:
            List[Dict]: Matching sections
        
        Example:
            >>> results = service.search({
            ...     'program': 'BS Computer Science',
            ...     'year': '3rd'
            ... })
            >>> print(f"Found {len(results)} matching sections")
        """
        try:
            all_sections = self.get_all(token)
            
            if not filters:
                return all_sections
            
            # Filter sections
            results = []
            for section in all_sections:
                match = True
                for key, value in filters.items():
                    if key not in section or section[key] != value:
                        match = False
                        break
                if match:
                    results.append(section)
            
            logger.info(f"Search found {len(results)} sections")
            return results
        
        except Exception as e:
            logger.error(f"Error searching sections: {str(e)}")
            raise