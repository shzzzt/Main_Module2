import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSpacerItem, QSizePolicy, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette


class Create_Section_Dialog(QDialog):
    section_created = pyqtSignal(dict)

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Section")
        self.setFixedSize(400,450)
        self.setModal(True)


        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20, 10)
        layout.setSpacing(10)
        self.setAutoFillBackground(True)
        self.setStyleSheet(
            "background-color: white;"
        )
        

        title_label = QLabel("Create Section")
        title_font = QFont("Poppins", 16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("""
            color: #084924;     
            margin-bottom: 5px;
        """)
        layout.addWidget(title_label)

        self.section_name = QLineEdit()
        self.section_name.setPlaceholderText("Section")
        self.section_name.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                font-size: 12px;
                color: #084294;
            }
            QLineEdit:focus {
                border: 2px solid #084924;
            }
        """
        )
        layout.addWidget(self.section_name)

        self.program_combo = QComboBox()
        self.program_combo.setPlaceholderText("Program Title")
        self.program_combo.addItems([
            "BS Information Technology",
            "BS Data Science", 
            "BS Information Systems"
        ])
        self.program_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                font-size: 12px;
                color: #084924;
            }
            QComboBox:focus {
                border: 2px solid #084924;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                color: #084294;
                selection-background-color: #E8F5E8;
                selection-color: #084294;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #666666;
                width: 8px;
                height: 8px;
                border-top: none;
                border-left: none;
                margin: 4px;
                color: #084924;
            }
        """)
        layout.addWidget(self.program_combo)

        self.curriculum_combo = QComboBox()
        self.curriculum_combo.setPlaceholderText("Curriculum")
        self.curriculum_combo.addItems(["Dummy 1", "Dummy 2"])
        self.curriculum_combo.setStyleSheet(self.program_combo.styleSheet())
        layout.addWidget(self.curriculum_combo)

        bottom_layout = QHBoxLayout()

        self.year = QComboBox()
        self.year.setPlaceholderText("Year")
        self.year.addItems(["1st Year", "2nd Year", "3rd Year", "4th Year"])
        self.year.setStyleSheet(self.program_combo.styleSheet())
        bottom_layout.addWidget(self.year)

        self.capacity = QComboBox()
        self.capacity.setPlaceholderText("Capacity")
        self.capacity.addItems(["50", "45"])
        self.capacity.setStyleSheet(self.program_combo.styleSheet())
        bottom_layout.addWidget(self.capacity)

        self.class_type = QComboBox()
        self.class_type.setPlaceholderText("Type")
        self.class_type.addItems(["Regular", "Irregular", "Petition"])
        self.class_type.setStyleSheet(self.program_combo.styleSheet())
        bottom_layout.addWidget(self.class_type)

        layout.addLayout(bottom_layout)

        layout.addSpacing(10)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
                QPushButton{
                        background-color: #E0E0E0;
                        color: #666666;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-weight: bold;
                }
                QPushButton:hover {
                background-color: #CCCCCC;
                }
                QPushButton:pressed {
                    background-color: #B0B0B0;
                }
        """)
        cancel_button.clicked.connect(self.reject)

        create_button = QPushButton("Create")
        create_button.setStyleSheet("""
                QPushButton {
                background-color: #084924;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0A5A2A;
                }
                QPushButton:pressed {
                    background-color: #063018;
                }
        """)
        create_button.clicked.connect(self.create_section)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(create_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def show_warning(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #084924;
            }
            QMessageBox QLabel {
                color: #084924;
                font-size: 12px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                background-color: #084924;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0A5A2A;
            }
            QMessageBox QPushButton:pressed {
                background-color: #063018;
            }
        """)
        
        msg_box.exec()
    
    def create_section(self):
        section_name = self.section_name.text().strip()
        
        if not section_name:
            self.show_warning("Validation Error", "Please enter a section name.")
            return
        
        if self.program_combo.currentText() not in [
            "BS Information Technology",
            "BS Data Science", 
            "BS Information Systems"
        ]:
            self.show_warning("Validation Error", "Please select a program.")
            return
            
        if self.curriculum_combo.currentText() not in  ["Dummy 1", "Dummy 2"]:
            self.show_warning("Validation Error", "Please select a curriculum.")
            return
            
        if self.year.currentText() not in ["1st Year", "2nd Year", "3rd Year", "4th Year"]:
            self.show_warning("Validation Error", "Please select a year.")
            return
            
        if self.capacity.currentText() not in ["50", "45"]:
            self.show_warning("Validation Error", "Please select a capacity.")
            return
            
        if self.class_type.currentText() not in ["Regular", "Irregular", "Petition"]:
            self.show_warning("Validation Error", "Please select a class type.")
            return
            

        section_data = {
            'section': self.section_name,
            'program': self.program_combo.currentText(),
            'curriculum': self.curriculum_combo.currentText(),
            'year': self.year.currentText(),
            'capacity': self.capacity.currentText(),
            'type': self.class_type.currentText(),
            'remarks': self.class_type.currentText()
        }
        
        self.section_created.emit(section_data)
        
        self.accept()

    