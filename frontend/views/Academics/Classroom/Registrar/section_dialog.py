# views/create_section_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout

class CreateSectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Section")

        self.section_input = QLineEdit()
        self.program_input = QComboBox()
        self.curriculum_input = QComboBox()
        self.year_input = QComboBox()
        self.capacity_input = QLineEdit()
        self.type_input = QComboBox()

        # Populate dropdowns for demo
        self.program_input.addItems(["BSIT", "BSCS"])
        self.curriculum_input.addItems(["2021", "2022"])
        self.year_input.addItems(["1", "2", "3", "4"])
        self.type_input.addItems(["Lecture", "Lab"])

        self.create_btn = QPushButton("Create")
        self.cancel_btn = QPushButton("Cancel")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.create_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.section_input)
        layout.addWidget(self.program_input)
        layout.addWidget(self.curriculum_input)
        layout.addWidget(self.year_input)
        layout.addWidget(self.capacity_input)
        layout.addWidget(self.type_input)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self.accept)

    def get_form_data(self):
        return {
            "section": self.section_input.text(),
            "program": self.program_input.currentText(),
            "curriculum": self.curriculum_input.currentText(),
            "year": self.year_input.currentText(),
            "capacity": self.capacity_input.text(),
            "type": self.type_input.currentText(),
            "remarks": "Regular"  # default for demo
        }
