import logging
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

from frontend.model.Academics.Tagging.classes_table_model import ClassesTableModel
from frontend.services.Academics.Tagging.class_service import ClassService
from frontend.services.Academics.Tagging.section_service import SectionService
from frontend.views.Academics.Tagging.create_class_dialog import CreateClassDialog

logger = logging.getLogger(__name__)

class ClassesController(QObject):
    class_created = pyqtSignal(dict)
    class_updated = pyqtSignal(dict)
    class_deleted = pyqtSignal(int)

    def __init__(self, parent_widget: Optional[QWidget] = None):
        super().__init__()
        self.parent = parent_widget
        self.service = ClassService()
        self.section_service = SectionService()
        self.model = None # will be set by view

        logger.info("ClassesController initialized")

    def set_model(self, model: ClassesTableModel) -> None:
        """
        Set the table model for updating display.

        Args:
            model: ClassesTableModel instance
        """

        self.model = model
        logger.info(f"Entered set_model method. model = {self.model}")

    def load_classes(self) -> bool:
        """
        Loads all classes from data store.
        """
        try:
            classes = self.service.get_all()
            if self.model:
                self.model.set_classes(classes)
                return True

        except Exception as e:
            logger.exception(f"{e}")

        return False

    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================

    def handle_create_class(self, dialog: CreateClassDialog) -> bool:
        try:
            logger.info("Entered handle_create_class method.")
            class_data = dialog.get_data()
            logger.info(f"class_data = {class_data}")
            # some kind of validation here before proceeding to next line
            created_class = self.service.create(class_data)
            self.model.add_class(created_class)

            self.class_created.emit(class_data)
            return True

        except Exception as e:
            logger.exception(f"{e}")

        return False


