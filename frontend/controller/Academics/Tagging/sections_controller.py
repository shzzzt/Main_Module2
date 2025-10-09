import logging
from typing import Optional, Dict, List
from PyQt6.QtWidgets import QWidget

from frontend.services.Academics.Tagging.section_service import SectionService
from frontend.views.Academics.Classroom.Registrar.example import SectionsTableModel
from frontend.views.Academics.Tagging.create_section_dialog import CreateSectionDialog

logger = logging.getLogger(__name__)

class SectionsController:
    """
    Controller for section operations.
    
    Orchestrates all CRUD operations for sections, enforcing business rules
    and coordinating between views and services.
    
    Attributes:
        service: SectionService instance for data operations
        model: SectionsTableModel for displaying data
        parent_widget: Parent widget for message boxes
    """

    def __init__(self, parent_widget: Optional[QWidget] = None):
        """
        Initialize the sections controller.

        Args:
            parent_widget: Parent widget for dialogs (optional) 
        """
        self.service = SectionService()
        self.parent = parent_widget 
        self.model = None # will be set by view 

        logger.info("SectionsController initialized")

    def set_model(self, model: SectionsTableModel) -> None:
        """
        Set the table model for updating display.
        
        Args:
            model: SectionsTableModel instance
        """
        
        self.model = model 
        logger.info(f"Entered set_model method. model = {self.model}")

    def load_sections(self) -> bool:
        """
        Loads all sections from data store. 
        """
        try:
            sections = self.service.get_all()
            if self.model:
                self.model.set_sections(sections)
                return True

        except Exception as e:
            logger.exception(f"{e}")

        return False

    # ================================================= 
    # CREATE OPERATION
    # =================================================   

    def handle_create_section(self, dialog: CreateSectionDialog) -> bool:
        """
        Handle section creation from dialog. 

        Args:
            dialog: CreateSectionDialog instance
        
        Returns:
            bool: True if section created successfully, False otherwise
        """
        try:
            section_data = dialog.get_data() 
            logger.info(f"Attempting to create section: {section_data.get('section')}")

            if self._validate_unique_section_data(section_data):
                created_section = self.service.create(section_data)

                # update the table model
                logger.info(f"Before self.model add_section method")
                self.model.add_section(created_section) 
                logger.info(f"After self.model add_section method")

                logger.info(f"Successfully created section ID {created_section['id']}") 
                return True
        
        except Exception as e:
            logger.exception(f"An error occured while creating a section: {e}")
            return False 
        
        logger.info(f"Unable to create section. Check whether duplicate section already exists or SectionController.model has been set.")
        return False 


    def _validate_unique_section_data(self, section_data: Dict) -> bool:
        """
        Business rule validation of duplicate sections. Sections cannot have the same name, program, year, curriculum and type.

        Args:
            section_data: Section data to validate

        Returns:
            bool: True if section_data passes validation, False otherwise
        """
        existing_sections = self.service.get_all() 

        for existing in existing_sections:
            if (
                existing['section'] == section_data['section'] and
                existing['program'] == section_data['program'] and 
                existing['year'] == section_data['year'] and 
                existing['curriculum'] == section_data['curriculum'] and
                existing['type'] == section_data['type']
            ): 
                logger.error(f"Duplicate section data. Section {section_data['section']} already exists.")
                return False
            
        return True 
