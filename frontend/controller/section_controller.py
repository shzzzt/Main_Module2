# controllers/section_controller.py
from PyQt6.QtWidgets import QWidget
from ..views.default.Academics.Classroom.Registrar.sections_view import SectionView
from ..model.section_table_model import SectionTableModel
from ..services.section_service import MockService
from ..views.default.Academics.Classroom.Registrar.section_dialog import CreateSectionDialog

class SectionController:
    def __init__(self):
        self.service = MockService()
        self.view = SectionView()
        self.model = SectionTableModel(self.service)

        self.view.table.setModel(self.model)

        self.view.add_button.clicked.connect(self.open_create_dialog)

        self.refresh_table()

    def refresh_table(self):
        self.model.load_data()

    def open_create_dialog(self):
        dialog = CreateSectionDialog(self.view)
        if dialog.exec():
            data = dialog.get_form_data()
            self.service.create_section(data)
            self.refresh_table()
