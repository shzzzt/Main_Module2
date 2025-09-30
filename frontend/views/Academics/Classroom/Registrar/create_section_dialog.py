from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGridLayout, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys


class CreateSectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Section")
        # self.setFixedSize(480, 400)  # Larger height to avoid overlap
        self.setStyleSheet("""
            QDialog {
  
                border: 2px solid #1e5631;
                border-radius: 10px;
            }
            QLabel {
                color: #2d2d2d;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 6px 10px;
                background-color: #f9f9f9;
                min-width: 300px;
                min-height: 30px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QPushButton {
                background-color: #1e5631;
                color: white;
                padding: 8px 18px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                min-width: 100px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2d5a3d;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(5)

        # Title
        title = QLabel("Create Section")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e5631; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Section input
        section_label = QLabel("Section")
        self.section_input = QLineEdit()
        main_layout.addWidget(section_label)
        main_layout.addWidget(self.section_input)

        # Program Title dropdown
        program_label = QLabel("Program Title")
        self.program_combo = QComboBox()
        self.program_combo.addItems([
            "BS Computer Science",
            "BS Information Technology",
            "BS Software Engineering"
        ])
        main_layout.addWidget(program_label)
        main_layout.addWidget(self.program_combo)

        # Curriculum dropdown
        curriculum_label = QLabel("Curriculum")
        self.curriculum_combo = QComboBox()
        self.curriculum_combo.addItems(["2023-2024", "2022-2023", "2021-2022"])
        main_layout.addWidget(curriculum_label)
        main_layout.addWidget(self.curriculum_combo)

        # Grid layout for Year, Capacity, and Lecture
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        year_label = QLabel("Year")
        self.year_combo = QComboBox()
        self.year_combo.addItems(["1", "2", "3", "4"])
        self.year_combo.setMaximumWidth(20)  # Different width for grid combobox
        grid_layout.addWidget(year_label, 0, 0)
        grid_layout.addWidget(self.year_combo, 1, 0)

        capacity_label = QLabel("Capacity")
        self.capacity_combo = QComboBox()
        self.capacity_combo.addItems(["30", "40", "50", "60"])
        self.capacity_combo.setMaximumWidth(20)  # Different width for grid combobox
        grid_layout.addWidget(capacity_label, 0, 1)
        grid_layout.addWidget(self.capacity_combo, 1, 1)

        lecture_label = QLabel("Type")
        self.lecture_combo = QComboBox()
        self.lecture_combo.addItems(["Lecture", "Laboratory"])
        self.lecture_combo.setMaximumWidth(40)  # Different width for grid combobox
        grid_layout.addWidget(lecture_label, 0, 2)
        grid_layout.addWidget(self.lecture_combo, 1, 2)

        main_layout.addLayout(grid_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        create_btn = QPushButton("Create")
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(create_btn)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Connect signals
        cancel_btn.clicked.connect(self.reject)
        create_btn.clicked.connect(self.accept)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = CreateSectionDialog()
    dialog.exec()
    sys.exit(app.exec())
