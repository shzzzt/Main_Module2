from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QGridLayout, QLineEdit, QTimeEdit)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont

class CreateClassDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Class")
        self.setStyleSheet("""
            QLabel {
                color: #2d2d2d;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QTimeEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
                min-width: 140px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QPushButton {
                background-color: #1e5631;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2d5a3d;
            }
        """)

        # Main layout as an instance variable
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(5)

        # Title
        title = QLabel("Create Class")
        title.setFont(QFont("Segoe UI", 40, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e5631;")
        self.main_layout.addWidget(title)

        # Section dropdown
        section_label = QLabel("Section")
        self.section_combo = QComboBox()
        self.section_combo.addItems(["1A", "1B", "2A", "2B", "3A", "3B"])
        self.main_layout.addWidget(section_label)
        self.main_layout.addWidget(self.section_combo)

        # Code dropdown
        code_label = QLabel("Code")
        self.code_combo = QComboBox()
        self.code_combo.addItems(["CS101", "IT57", "SE201", "CS202"])
        self.main_layout.addWidget(code_label)
        self.main_layout.addWidget(self.code_combo)

        # Schedule section with Add button
        schedule_layout = QHBoxLayout()
        schedule_label = QLabel("Schedule")
        self.add_schedule_btn = QPushButton("+ Add")
        self.add_schedule_btn.setStyleSheet("min-width: 60px;")
        self.add_schedule_btn.clicked.connect(self.add_new_schedule)
        schedule_layout.addWidget(schedule_label)
        schedule_layout.addWidget(self.add_schedule_btn)
        self.main_layout.addLayout(schedule_layout)

        # List to store schedule grids
        self.schedule_grids = []
        # Add initial schedule grid after layout is set
        self.setLayout(self.main_layout)  # Set layout before adding initial schedule
        self.add_new_schedule()

        # Grid layout for Room and Instructor
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(15)

        room_label = QLabel("Room")
        self.room_input = QLineEdit()
        grid_layout.addWidget(room_label, 0, 0)
        grid_layout.addWidget(self.room_input, 1, 0)

        instructor_label = QLabel("Instructor")
        self.instructor_input = QLineEdit()
        grid_layout.addWidget(instructor_label, 0, 1)
        grid_layout.addWidget(self.instructor_input, 1, 1)

        self.main_layout.addLayout(grid_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        create_btn = QPushButton("Create")
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(create_btn)
        self.main_layout.addLayout(buttons_layout)

        # Connect signals
        cancel_btn.clicked.connect(self.reject)
        create_btn.clicked.connect(self.accept)

    def add_new_schedule(self):
        # Create a new QGridLayout for the schedule
        new_grid = QGridLayout()
        new_grid.setHorizontalSpacing(20)
        new_grid.setVerticalSpacing(5)

        # Day selection
        day_label = QLabel("Day")
        day_combo = QComboBox()
        day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        new_grid.addWidget(day_label, 0, 0)
        new_grid.addWidget(day_combo, 1, 0)

        # Start Time
        start_time_label = QLabel("Start Time")
        start_time_edit = QTimeEdit(QTime(21, 20))  # 09:20 PM PST on Sep 30, 2025
        start_time_edit.setDisplayFormat("hh:mm AP")  # e.g., "09:20 PM"
        new_grid.addWidget(start_time_label, 0, 1)
        new_grid.addWidget(start_time_edit, 1, 1)

        # End Time
        end_time_label = QLabel("End Time")
        end_time_edit = QTimeEdit(QTime(21, 20).addSecs(3600))  # 10:20 PM
        end_time_edit.setDisplayFormat("hh:mm AP")  # e.g., "10:20 PM"
        new_grid.addWidget(end_time_label, 0, 2)
        new_grid.addWidget(end_time_edit, 1, 2)

        if self.main_layout.count() == 6: 
            # Add the new grid to the main layout
            self.main_layout.insertLayout(self.main_layout.count(), new_grid)  # Insert before buttons
        else: 
             self.main_layout.insertLayout(self.main_layout.count() - 2, new_grid)

        
        # Store the grid and its widgets for potential removal or data access
        self.schedule_grids.append({
            "grid": new_grid,
            "day_combo": day_combo,
            "start_time_edit": start_time_edit,
            "end_time_edit": end_time_edit
        })

        # Disable Add button if maximum schedules reached (e.g., 5)
        if len(self.schedule_grids) >= 5:
            self.add_schedule_btn.setEnabled(False)

    def get_schedule_data(self):
        # Method to retrieve data from all schedules (for use in accept slot if needed)
        schedules = []
        for schedule in self.schedule_grids:
            day = schedule["day_combo"].currentText()
            start_time = schedule["start_time_edit"].time().toString("hh:mm AP")
            end_time = schedule["end_time_edit"].time().toString("hh:mm AP")
            schedules.append(f"{day} {start_time} - {end_time}")
        return schedules

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = CreateClassDialog()
    dialog.exec()
    sys.exit(app.exec())