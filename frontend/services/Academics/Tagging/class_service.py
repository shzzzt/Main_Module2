#  model generated file to work with json data while being ready for django rest calls (gikapoy nako hehe)

import json
import logging
import os
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from copy import deepcopy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassServiceError(Exception):
    """Base exception for class service errors."""
    pass


class ClassNotFoundError(ClassServiceError):
    """Raised when a class is not found."""
    pass


class ClassValidationError(ClassServiceError):
    """Raised when class data fails validation."""
    pass


class ClassStorageError(ClassServiceError):
    """Raised when there's an error reading/writing data."""
    pass


class ScheduleConflictError(ClassServiceError):
    """Raised when schedule conflicts are detected."""
    pass


class ClassService:
    """
    Service layer for class data operations.
    
    Handles classes (courses) with complex scheduling and section relationships.
    Currently implements JSON file storage, designed for Django REST API migration.
    
    Architecture Pattern:
        Controller → Service → Data Store (JSON/API)
    
    Attributes:
        json_file (str): Path to the classes JSON database file
        section_service: Reference to SectionService for validation
        _cache (Dict): In-memory cache of loaded data
        _required_fields (set): Required fields for class validation
    
    Relationships:
        - Each class belongs to one section (many-to-one)
        - Each class can have multiple schedules (one-to-many)
        - Room assignments must be unique per time slot
    """
    
    # Required fields for a valid class
    REQUIRED_FIELDS = {
        'code', 'title', 'units', 'section_id', 
        'schedules', 'room', 'instructor', 'type'
    }
    
    # Schedule required fields
    SCHEDULE_REQUIRED_FIELDS = {'day', 'start_time', 'end_time'}
    
    # Valid values
    VALID_DAYS = {
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
        'Friday', 'Saturday', 'Sunday'
    }
    VALID_CLASS_TYPES = {'Regular', 'Special', 'Makeup', 'Online'}
    
    def __init__(
        self, 
        json_file: str = "data/classes.json",
        section_service=None
    ):
        """
        Initialize the class service.
        
        Args:
            json_file: Path to JSON database file
            section_service: SectionService instance for validation
                           (injected for testing, created if None)
        
        Design Note:
            section_service dependency allows validating that section_id
            references exist. Will remain useful even with Django API.
        """
        self.json_file = json_file
        self._cache: Optional[Dict] = None
        
        # Import here to avoid circular dependency
        if section_service is None:
            from services.section_service import SectionService
            self.section_service = SectionService()
        else:
            self.section_service = section_service
        
        self._ensure_data_file_exists()
        
        # FUTURE: For Django API integration
        # self.api_base_url = api_base_url
        # self.session = requests.Session()
        
        logger.info(f"ClassService initialized with file: {json_file}")
    
    def _ensure_data_file_exists(self) -> None:
        """
        Ensure the JSON data file and directory exist.
        
        Creates empty structure if file doesn't exist.
        
        Raises:
            ClassStorageError: If file/directory cannot be created
        """
        try:
            Path(self.json_file).parent.mkdir(parents=True, exist_ok=True)
            
            if not os.path.exists(self.json_file):
                initial_data = {
                    "metadata": {
                        "last_updated": datetime.now().isoformat(),
                        "version": "1.0",
                        "next_id": 1
                    },
                    "classes": []
                }
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created new classes database: {self.json_file}")
        
        except Exception as e:
            error_msg = f"Failed to initialize data file: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
    
    def _load_data(self) -> Dict:
        """
        Load class data from JSON file with caching.
        
        Returns:
            Dict: Complete JSON structure with metadata and classes
        
        Raises:
            ClassStorageError: If file cannot be read or JSON is invalid
        
        Future Implementation:
            GET request to /api/classes/ with pagination
        """
        if self._cache is not None:
            return deepcopy(self._cache)
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'metadata' not in data or 'classes' not in data:
                raise ClassStorageError("Invalid JSON structure")
            
            self._cache = deepcopy(data)
            logger.debug(f"Loaded {len(data['classes'])} classes from file")
            return deepcopy(data)
        
        except FileNotFoundError:
            error_msg = f"Data file not found: {self.json_file}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
        
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in data file: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
        
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
    
    def _save_data(self, data: Dict) -> None:
        """
        Save class data to JSON file atomically.
        
        Uses atomic write pattern to prevent corruption.
        
        Args:
            data: Complete JSON structure to save
        
        Raises:
            ClassStorageError: If file cannot be written
        """
        temp_file = f"{self.json_file}.tmp"
        
        try:
            data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_file, self.json_file)
            self._cache = None
            
            logger.debug(f"Saved {len(data['classes'])} classes to file")
        
        except Exception as e:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            error_msg = f"Error saving data: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
    
    def _validate_schedule(self, schedule: Dict) -> None:
        """
        Validate a single schedule entry.
        
        Args:
            schedule: Schedule dictionary to validate
        
        Raises:
            ClassValidationError: If schedule is invalid
        
        Validation Rules:
            - Has required fields: day, start_time, end_time
            - Day is valid
            - Times are in correct format (HH:MM AM/PM)
            - End time is after start time
        """
        # Check required fields
        missing = self.SCHEDULE_REQUIRED_FIELDS - set(schedule.keys())
        if missing:
            raise ClassValidationError(
                f"Schedule missing fields: {', '.join(missing)}"
            )
        
        # Validate day
        if schedule['day'] not in self.VALID_DAYS:
            raise ClassValidationError(
                f"Invalid day '{schedule['day']}'. "
                f"Must be one of: {', '.join(self.VALID_DAYS)}"
            )
        
        # Validate time format and logic
        try:
            start = self._parse_time(schedule['start_time'])
            end = self._parse_time(schedule['end_time'])
            
            if end <= start:
                raise ClassValidationError(
                    f"End time ({schedule['end_time']}) must be after "
                    f"start time ({schedule['start_time']})"
                )
        except ValueError as e:
            raise ClassValidationError(f"Invalid time format: {str(e)}")
    
    def _parse_time(self, time_str: str) -> time:
        """
        Parse time string in format "HH:MM AM/PM".
        
        Args:
            time_str: Time string (e.g., "09:00 AM", "02:30 PM")
        
        Returns:
            time: Python time object
        
        Raises:
            ValueError: If format is invalid
        """
        try:
            # Handle formats: "09:00 AM", "9:00 AM", "09:00AM"
            time_str = time_str.strip().upper()
            
            # Add space before AM/PM if missing
            if time_str[-2:] in ['AM', 'PM'] and time_str[-3] != ' ':
                time_str = time_str[:-2] + ' ' + time_str[-2:]
            
            return datetime.strptime(time_str, "%I:%M %p").time()
        except:
            raise ValueError(
                f"Time '{time_str}' must be in format 'HH:MM AM' or 'HH:MM PM'"
            )
    
    def _validate_class_data(
        self, 
        data: Dict, 
        is_update: bool = False
    ) -> None:
        """
        Validate class data at storage level.
        
        Args:
            data: Class data dictionary to validate
            is_update: If True, allows missing fields
        
        Raises:
            ClassValidationError: If validation fails
        
        Validation Rules:
            - Required fields present (unless update)
            - units is integer 1-6
            - section_id references existing section
            - schedules is non-empty list
            - Each schedule is valid
            - type is valid value
            - code and title are non-empty strings
        """
        # Check required fields
        if not is_update:
            missing_fields = self.REQUIRED_FIELDS - set(data.keys())
            if missing_fields:
                raise ClassValidationError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
        
        # Validate units
        if 'units' in data:
            try:
                units = int(data['units'])
                if units < 1 or units > 6:
                    raise ClassValidationError(
                        "Units must be between 1 and 6"
                    )
            except (ValueError, TypeError):
                raise ClassValidationError(
                    "Units must be a valid integer"
                )
        
        # Validate section_id exists
        if 'section_id' in data:
            try:
                section = self.section_service.get_by_id(data['section_id'])
                if section is None:
                    raise ClassValidationError(
                        f"Section with ID {data['section_id']} does not exist"
                    )
            except Exception as e:
                raise ClassValidationError(
                    f"Error validating section_id: {str(e)}"
                )
        
        # Validate schedules
        if 'schedules' in data:
            if not isinstance(data['schedules'], list):
                raise ClassValidationError("Schedules must be a list")
            
            if len(data['schedules']) == 0:
                raise ClassValidationError(
                    "Class must have at least one schedule"
                )
            
            for i, schedule in enumerate(data['schedules']):
                try:
                    self._validate_schedule(schedule)
                except ClassValidationError as e:
                    raise ClassValidationError(
                        f"Schedule {i+1} invalid: {str(e)}"
                    )
        
        # Validate type
        if 'type' in data and data['type'] not in self.VALID_CLASS_TYPES:
            raise ClassValidationError(
                f"Invalid type. Must be one of: "
                f"{', '.join(self.VALID_CLASS_TYPES)}"
            )
        
        # Validate non-empty strings
        string_fields = ['code', 'title', 'instructor', 'room']
        for field in string_fields:
            if field in data:
                if not isinstance(data[field], str) or not data[field].strip():
                    raise ClassValidationError(
                        f"{field.capitalize()} must be a non-empty string"
                    )
    
    def _generate_next_id(self, data: Dict) -> int:
        """
        Generate the next available ID for a new class.
        
        Args:
            data: Current data structure with metadata
        
        Returns:
            int: Next available ID
        """
        next_id = data['metadata']['next_id']
        
        existing_ids = {cls['id'] for cls in data['classes']}
        while next_id in existing_ids:
            next_id += 1
        
        data['metadata']['next_id'] = next_id + 1
        return next_id
    
    def _check_schedule_conflicts(
        self,
        schedules: List[Dict],
        room: str,
        exclude_class_id: int = None
    ) -> List[str]:
        """
        Check for schedule conflicts with other classes.
        
        Conflict occurs when:
        - Same room
        - Same day
        - Overlapping time
        
        Args:
            schedules: List of schedules to check
            room: Room name
            exclude_class_id: Class ID to exclude from check (for updates)
        
        Returns:
            List[str]: List of conflict descriptions (empty if no conflicts)
        
        Example Conflict:
            "Conflict with IT57 in CISC Room 3 on Tuesday 07:00 AM - 08:30 AM"
        """
        conflicts = []
        
        try:
            all_classes = self.get_all()
            
            for existing_class in all_classes:
                # Skip if this is the class being updated
                if exclude_class_id and existing_class['id'] == exclude_class_id:
                    continue
                
                # Only check if same room
                if existing_class['room'] != room:
                    continue
                
                # Check each new schedule against each existing schedule
                for new_schedule in schedules:
                    for existing_schedule in existing_class['schedules']:
                        # Check if same day
                        if new_schedule['day'] != existing_schedule['day']:
                            continue
                        
                        # Check time overlap
                        new_start = self._parse_time(new_schedule['start_time'])
                        new_end = self._parse_time(new_schedule['end_time'])
                        exist_start = self._parse_time(existing_schedule['start_time'])
                        exist_end = self._parse_time(existing_schedule['end_time'])
                        
                        # Times overlap if: new_start < exist_end AND new_end > exist_start
                        if new_start < exist_end and new_end > exist_start:
                            conflict_msg = (
                                f"Conflict with {existing_class['code']} "
                                f"({existing_class['title']}) in {room} "
                                f"on {new_schedule['day']} "
                                f"{existing_schedule['start_time']} - "
                                f"{existing_schedule['end_time']}"
                            )
                            conflicts.append(conflict_msg)
        
        except Exception as e:
            logger.error(f"Error checking conflicts: {str(e)}")
            # Don't fail operation, but log the error
        
        return conflicts
    
    # ========================================================================
    # PUBLIC CRUD METHODS
    # ========================================================================
    
    def get_all(self, token: str = None) -> List[Dict]:
        """
        Retrieve all classes from the database.
        
        Current Implementation:
            Loads from JSON file and returns classes list
        
        Future Implementation:
            GET request to /api/classes/
            Paginated response handling
        
        Args:
            token: Authentication token (for future API calls)
        
        Returns:
            List[Dict]: List of all class dictionaries
        
        Raises:
            ClassStorageError: If data cannot be loaded
        """
        try:
            data = self._load_data()
            logger.info(f"Retrieved {len(data['classes'])} classes")
            return deepcopy(data['classes'])
        
        except Exception as e:
            logger.error(f"Error retrieving classes: {str(e)}")
            raise
    
    def get_by_id(self, class_id: int, token: str = None) -> Optional[Dict]:
        """
        Retrieve a specific class by ID.
        
        Current Implementation:
            Searches through JSON array for matching ID
        
        Future Implementation:
            GET request to /api/classes/{class_id}/
        
        Args:
            class_id: Unique identifier of the class
            token: Authentication token (for future API calls)
        
        Returns:
            Dict: Class data if found, None if not found
        
        Raises:
            ClassStorageError: If data cannot be loaded
        """
        try:
            data = self._load_data()
            for cls in data['classes']:
                if cls['id'] == class_id:
                    logger.debug(f"Found class with ID {class_id}")
                    return deepcopy(cls)
            
            logger.warning(f"Class with ID {class_id} not found")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving class {class_id}: {str(e)}")
            raise
    
    def get_by_section(
        self, 
        section_id: int, 
        token: str = None
    ) -> List[Dict]:
        """
        Retrieve all classes for a specific section.
        
        Args:
            section_id: Section ID to filter by
            token: Authentication token (for future API calls)
        
        Returns:
            List[Dict]: Classes belonging to the section
        
        Future Implementation:
            GET /api/classes/?section_id={section_id}
        """
        try:
            all_classes = self.get_all(token)
            section_classes = [
                cls for cls in all_classes 
                if cls['section_id'] == section_id
            ]
            logger.info(
                f"Found {len(section_classes)} classes for section {section_id}"
            )
            return section_classes
        
        except Exception as e:
            logger.error(f"Error retrieving classes for section: {str(e)}")
            raise
    
    def create(
        self, 
        class_data: Dict, 
        token: str = None,
        check_conflicts: bool = True
    ) -> Dict:
        """
        Create a new class in the database.
        
        Current Implementation:
            1. Validate class data
            2. Check schedule conflicts (optional)
            3. Load current data
            4. Generate new ID
            5. Add timestamps
            6. Append to classes list
            7. Save atomically
            8. Return created class
        
        Future Implementation:
            POST request to /api/classes/
            Server handles conflict checking
        
        Args:
            class_data: Dictionary containing class fields
            token: Authentication token (for future API calls)
            check_conflicts: If True, check for schedule conflicts
        
        Returns:
            Dict: The created class with assigned ID and timestamps
        
        Raises:
            ClassValidationError: If data fails validation
            ScheduleConflictError: If schedule conflicts detected
            ClassStorageError: If class cannot be saved
        
        Example:
            >>> new_class = service.create({
            ...     'code': 'IT58',
            ...     'title': 'Web Development',
            ...     'units': 3,
            ...     'section_id': 1,
            ...     'schedules': [
            ...         {
            ...             'day': 'Monday',
            ...             'start_time': '09:00 AM',
            ...             'end_time': '10:30 AM'
            ...         }
            ...     ],
            ...     'room': 'CISC Lab 1',
            ...     'instructor': 'Jane Smith',
            ...     'type': 'Regular'
            ... })
        """
        try:
            # Validate data
            self._validate_class_data(class_data, is_update=False)
            
            # Check schedule conflicts if requested
            if check_conflicts:
                conflicts = self._check_schedule_conflicts(
                    class_data['schedules'],
                    class_data['room']
                )
                if conflicts:
                    raise ScheduleConflictError(
                        "Schedule conflicts detected:\n" + "\n".join(conflicts)
                    )
            
            # Get section name for denormalized storage
            section = self.section_service.get_by_id(class_data['section_id'])
            section_name = section['section'] if section else 'Unknown'
            
            # Load current data
            data = self._load_data()
            
            # Create new class with metadata
            new_class = deepcopy(class_data)
            new_class['id'] = self._generate_next_id(data)
            new_class['section_name'] = section_name  # Denormalized
            new_class['created_at'] = datetime.now().isoformat()
            new_class['updated_at'] = datetime.now().isoformat()
            
            # Add to classes list
            data['classes'].append(new_class)
            
            # Save atomically
            self._save_data(data)
            
            logger.info(f"Created class: {new_class['code']} "
                       f"(ID: {new_class['id']})")
            
            return deepcopy(new_class)
        
        except (ClassValidationError, ScheduleConflictError, ClassStorageError):
            raise
        
        except Exception as e:
            error_msg = f"Unexpected error creating class: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
    
    def update(
        self,
        class_id: int,
        class_data: Dict,
        token: str = None,
        check_conflicts: bool = True
    ) -> Dict:
        """
        Update an existing class.
        
        Args:
            class_id: ID of class to update
            class_data: Dictionary with fields to update
            token: Authentication token (for future API calls)
            check_conflicts: If True, check for schedule conflicts
        
        Returns:
            Dict: Updated class data
        
        Raises:
            ClassNotFoundError: If class doesn't exist
            ClassValidationError: If data fails validation
            ScheduleConflictError: If schedule conflicts detected
            ClassStorageError: If class cannot be saved
        """
        try:
            # Validate update data
            self._validate_class_data(class_data, is_update=True)
            
            # Load current data
            data = self._load_data()
            
            # Find class to update
            class_index = None
            for i, cls in enumerate(data['classes']):
                if cls['id'] == class_id:
                    class_index = i
                    break
            
            if class_index is None:
                raise ClassNotFoundError(
                    f"Class with ID {class_id} not found"
                )
            
            existing_class = data['classes'][class_index]
            
            # Check schedule conflicts if schedules or room updated
            if check_conflicts:
                schedules_to_check = class_data.get(
                    'schedules', 
                    existing_class['schedules']
                )
                room_to_check = class_data.get('room', existing_class['room'])
                
                conflicts = self._check_schedule_conflicts(
                    schedules_to_check,
                    room_to_check,
                    exclude_class_id=class_id
                )
                if conflicts:
                    raise ScheduleConflictError(
                        "Schedule conflicts detected:\n" + "\n".join(conflicts)
                    )
            
            # Update section_name if section_id changed
            if 'section_id' in class_data:
                section = self.section_service.get_by_id(class_data['section_id'])
                class_data['section_name'] = section['section'] if section else 'Unknown'
            
            # Update class data
            existing_class.update(class_data)
            existing_class['updated_at'] = datetime.now().isoformat()
            
            # Protect immutable fields
            existing_class['id'] = class_id
            if 'created_at' not in existing_class:
                existing_class['created_at'] = datetime.now().isoformat()
            
            # Save atomically
            self._save_data(data)
            
            logger.info(f"Updated class ID {class_id}")
            
            return deepcopy(existing_class)
        
        except (ClassNotFoundError, ClassValidationError, 
                ScheduleConflictError, ClassStorageError):
            raise
        
        except Exception as e:
            error_msg = f"Unexpected error updating class: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
    
    def delete(self, class_id: int, token: str = None) -> bool:
        """
        Delete a class from the database.
        
        Current Implementation:
            Hard delete - permanently removes class
        
        Future Implementation:
            DELETE request to /api/classes/{class_id}/
            Consider soft delete option
        
        Args:
            class_id: ID of class to delete
            token: Authentication token (for future API calls)
        
        Returns:
            bool: True if deleted, False if not found
        
        Raises:
            ClassStorageError: If deletion fails
        """
        try:
            data = self._load_data()
            
            original_count = len(data['classes'])
            data['classes'] = [
                cls for cls in data['classes'] if cls['id'] != class_id
            ]
            
            if len(data['classes']) == original_count:
                logger.warning(f"Class with ID {class_id} not found")
                return False
            
            self._save_data(data)
            
            logger.info(f"Deleted class ID {class_id}")
            return True
        
        except Exception as e:
            error_msg = f"Error deleting class {class_id}: {str(e)}"
            logger.error(error_msg)
            raise ClassStorageError(error_msg)
    
    def search(self, filters: Dict, token: str = None) -> List[Dict]:
        """
        Search classes by multiple criteria.
        
        Args:
            filters: Dictionary of field:value pairs to match
            token: Authentication token (for future API calls)
        
        Returns:
            List[Dict]: Matching classes
        
        Example:
            >>> results = service.search({
            ...     'section_id': 1,
            ...     'instructor': 'John Doe'
            ... })
        """
        try:
            all_classes = self.get_all(token)
            
            if not filters:
                return all_classes
            
            results = []
            for cls in all_classes:
                match = True
                for key, value in filters.items():
                    if key not in cls or cls[key] != value:
                        match = False
                        break
                if match:
                    results.append(cls)
            
            logger.info(f"Search found {len(results)} classes")
            return results
        
        except Exception as e:
            logger.error(f"Error searching classes: {str(e)}")
            raise