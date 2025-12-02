from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QCheckBox, QComboBox,
                             QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class AttendanceTableWidget(QWidget):
    """
    Attendance Table Widget for tracking student attendance
    
    This widget displays a table with:
    - Student list with avatars
    - Multiple date columns for attendance tracking
    - Present/Absent marking system with checkboxes
    - Accumulated absences row
    
    INTEGRATION GUIDE FOR FRONTEND:
    ================================
    1. Import this class: from attendance_table import AttendanceTableWidget
    2. Create instance: attendance_widget = AttendanceTableWidget()
    3. Load your data using: attendance_widget.load_data(students, dates)
    4. Get attendance data: attendance_widget.get_attendance_data()
    
    Data Format:
    - students: List of tuples [(name, number), ...]
    - dates: List of tuples [(date_string, initial_mode), ...]
      Example: [("August 18", "Present"), ("August 22", "Absent")]
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attendance_data = {}  # Store attendance state per student per date
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #1b5e20;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        # Enable horizontal scrolling for many date columns
        # In PyQt6, use ScrollMode instead of setHorizontalScrollMode
        self.table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        layout.addWidget(self.table)
        
    def load_data(self, students, dates):
        """
        Load student and date data into the table
        
        FRONTEND INTEGRATION POINT:
        ===========================
        Call this method to populate the table with your data.
        
        Parameters:
        -----------
        students : list of tuples
            Format: [(student_name, student_number), ...]
            Example: [("Castro, Carlos Fidel", 2), ("Doe, John", 3), ...]
            
        dates : list of tuples
            Format: [(date_string, initial_mode), ...]
            Example: [("August 18", "Present"), ("August 22", "Absent"), ...]
            initial_mode can be "Present" or "Absent"
        """
        
        # Clear existing data
        self.table.clear()
        self.attendance_data = {}
        
        num_students = len(students)
        num_date_columns = len(dates)
        
        # Setup table structure
        # Columns: No | Student Name | Absences | Date1 | Date2 | ... | DateN
        total_columns = 3 + num_date_columns
        self.table.setColumnCount(total_columns)
        self.table.setRowCount(num_students + 1)  # +1 for accumulated absences row
        
        # Set headers
        headers = ["No", "Sort by Last Name", "No. of Absences"]
        for date, mode in dates:
            headers.append(f"Mark by {mode}\n{date}")
        
        self.table.setHorizontalHeaderLabels(headers)
        
        # Configure header column widths and resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Fixed width for No column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Stretch for student name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Fixed width for absences
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(2, 150)
        
        # Set fixed width for date columns to enable horizontal scrolling
        for i in range(num_date_columns):
            header.setSectionResizeMode(3 + i, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(3 + i, 180)
        
        # Hide vertical header (row numbers)
        self.table.verticalHeader().setVisible(False)
        
        # Add accumulated absences row (row 0)
        item = QTableWidgetItem("Accumulated Absences")
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(0, 1, item)
        self.table.setSpan(0, 1, 1, 2)  # Span across name and absences columns
        
        # Add all students to the table
        for idx, (name, num) in enumerate(students):
            row = idx + 1  # +1 because row 0 is accumulated absences
            
            # Add student number
            num_item = QTableWidgetItem(str(num))
            num_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, num_item)
            
            # Add student name with avatar
            name_widget = self.create_student_name_widget(name)
            self.table.setCellWidget(row, 1, name_widget)
            
            # Add absences count column (initially empty)
            absences_item = QTableWidgetItem("0")
            absences_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            absences_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, absences_item)
            
            # Initialize attendance data for this student
            if row not in self.attendance_data:
                self.attendance_data[row] = {}
        
        # Add all date columns with dropdowns and checkboxes
        for col_idx, (date, initial_mode) in enumerate(dates):
            date_col = 3 + col_idx  # +3 for No, Name, Absences columns
            
            # Add dropdown widget in accumulated absences row (row 0)
            dropdown_widget = self.create_dropdown_widget(date, date_col, initial_mode)
            self.table.setCellWidget(0, date_col, dropdown_widget)
            
            # Add checkboxes for each student in this date column
            for student_idx in range(num_students):
                row = student_idx + 1
                checkbox_widget = self.create_checkbox_widget(row, date_col, initial_mode)
                self.table.setCellWidget(row, date_col, checkbox_widget)
                
                # Initialize attendance state for this student on this date
                if date_col not in self.attendance_data[row]:
                    self.attendance_data[row][date_col] = {
                        'checked': False,  # Initially unchecked
                        'mode': initial_mode  # Present or Absent
                    }
        
        # Set row heights
        self.table.setRowHeight(0, 60)  # Accumulated absences row
        for i in range(1, num_students + 1):
            self.table.setRowHeight(i, 60)  # Student rows
        
        # Update absence counts
        self.update_absence_counts()
        
    def create_student_name_widget(self, name):
        """
        Create a widget for displaying student name with avatar
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Avatar placeholder
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("""
            background-color: #FFB74D;
            border-radius: 16px;
        """)
        
        layout.addWidget(avatar)
        
        # Student name label
        name_label = QLabel(name)
        layout.addWidget(name_label)
        layout.addStretch()
        
        return widget
        
    def create_dropdown_widget(self, date, col_idx, initial_mode):
        """
        Create a dropdown widget for the accumulated absences row
        """
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Mode selection dropdown
        dropdown = QComboBox()
        dropdown.addItems(["Present", "Absent"])
        dropdown.setCurrentText(initial_mode)
        dropdown.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #e8f5e9;
                color: #333;
                border: 1px solid #ddd;
            }
        """)
        
        # Connect dropdown change event to update all students in this column
        dropdown.currentTextChanged.connect(
            lambda text, c=col_idx: self.on_mode_changed(c, text)
        )
        
        layout.addWidget(dropdown)
        layout.addStretch()
        
        return widget
        
    def create_checkbox_widget(self, row, col, mode):
        """
        Create a checkbox widget for marking attendance
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        checkbox = QCheckBox()
        label = QLabel(mode)
        
        # Apply initial styling (unchecked state)
        self.update_checkbox_style(checkbox, label, mode, False)
        
        # Connect checkbox state change to update attendance data
        checkbox.stateChanged.connect(
            lambda state, r=row, c=col, cb=checkbox, lbl=label: 
            self.on_checkbox_changed(r, c, state, cb, lbl)
        )
        
        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()
        
        return widget
        
    def update_checkbox_style(self, checkbox, label, mode, is_checked):
        """
        Update checkbox and label styling based on mode and checked state
        """
        if mode == "Present":
            label.setText("Present")
            if is_checked:
                # Student is marked as present (checked in Present mode)
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 2px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #1b5e20;
                        border: 2px solid #1b5e20;
                        image: url(none);
                    }
                """)
                label.setStyleSheet("color: #333; font-weight: normal;")
            else:
                # Student is not marked (unchecked in Present mode = absent)
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 2px;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: white;
                        border: 2px solid #999;
                    }
                """)
                label.setStyleSheet("color: #666; font-weight: normal;")
        else:  # Absent mode
            label.setText("Absent")
            if is_checked:
                # Student is marked as absent (checked in Absent mode)
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 2px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #e57373;
                        border: 2px solid #e57373;
                        image: url(none);
                    }
                """)
                label.setStyleSheet("color: #333; font-weight: normal;")
            else:
                # Student is not marked (unchecked in Absent mode = present)
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 2px;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: white;
                        border: 2px solid #ef9a9a;
                    }
                """)
                label.setStyleSheet("color: #666; font-weight: normal;")
        
    def on_checkbox_changed(self, row, col, state, checkbox, label):
        """
        Handle checkbox state change event
        """
        is_checked = state == Qt.CheckState.Checked
        mode = self.attendance_data[row][col]['mode']
        
        # Update attendance data
        self.attendance_data[row][col]['checked'] = is_checked
        
        # Update visual styling
        self.update_checkbox_style(checkbox, label, mode, is_checked)
        
        # Update the absence count for this student
        self.update_absence_counts()
        
    def on_mode_changed(self, col, mode_text):
        """
        Handle dropdown mode change for a date column
        """
        new_mode = mode_text
        num_students = self.table.rowCount() - 1
        
        # Update all student rows in this date column
        for student_idx in range(num_students):
            row = student_idx + 1
            
            # Get current checkbox state
            was_checked = self.attendance_data[row][col]['checked']
            
            # Update mode in data
            self.attendance_data[row][col]['mode'] = new_mode
            
            # INVERT the checkbox state when switching modes
            new_checked_state = not was_checked
            self.attendance_data[row][col]['checked'] = new_checked_state
            
            # Update the UI checkbox and label
            cell_widget = self.table.cellWidget(row, col)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                label = cell_widget.findChild(QLabel)
                
                if checkbox and label:
                    checkbox.blockSignals(True)
                    checkbox.setChecked(new_checked_state)
                    checkbox.blockSignals(False)
                    
                    self.update_checkbox_style(checkbox, label, new_mode, new_checked_state)
        
        # Update absence counts after mode change
        self.update_absence_counts()
    
    def update_absence_counts(self):
        """
        Update the "No. of Absences" column for all students
        """
        num_students = self.table.rowCount() - 1
        num_dates = self.table.columnCount() - 3
        
        for student_idx in range(num_students):
            row = student_idx + 1
            absence_count = 0
            
            # Count absences across all date columns
            for date_idx in range(num_dates):
                col = 3 + date_idx
                
                if col in self.attendance_data.get(row, {}):
                    mode = self.attendance_data[row][col]['mode']
                    is_checked = self.attendance_data[row][col]['checked']
                    
                    # Student is absent if:
                    if (mode == "Present" and not is_checked) or (mode == "Absent" and is_checked):
                        absence_count += 1
            
            # Update the absences column
            absences_item = self.table.item(row, 2)
            if absences_item:
                absences_item.setText(str(absence_count))
    
    def get_attendance_data(self):
        """
        Get the current attendance data
        """
        result = {}
        for row, dates in self.attendance_data.items():
            result[row] = {}
            for col, data in dates.items():
                result[row][col] = data.copy()
                # Calculate if student is absent
                mode = data['mode']
                is_checked = data['checked']
                result[row][col]['is_absent'] = (
                    (mode == "Present" and not is_checked) or 
                    (mode == "Absent" and is_checked)
                )
        return result
    
    def set_attendance_data(self, attendance_data):
        """
        Set attendance data (for loading from database)
        """
        self.attendance_data = attendance_data
        
        # Update all checkbox widgets to reflect the loaded data
        for row, dates in attendance_data.items():
            for col, data in dates.items():
                cell_widget = self.table.cellWidget(row, col)
                if cell_widget:
                    checkbox = cell_widget.findChild(QCheckBox)
                    label = cell_widget.findChild(QLabel)
                    
                    if checkbox and label:
                        mode = data['mode']
                        is_checked = data['checked']
                        
                        checkbox.blockSignals(True)
                        checkbox.setChecked(is_checked)
                        checkbox.blockSignals(False)
                        
                        self.update_checkbox_style(checkbox, label, mode, is_checked)
        
        self.update_absence_counts()


# Test the widget
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = AttendanceTableWidget()
    
    students = [
        ("Castro, Carlos Fidel", 2),
        ("Doe, John Michael", 3),
        ("Smith, Jane Elizabeth", 4),
        ("Johnson, Robert James", 5),
        ("Williams, Mary Patricia", 6),
        ("Brown, David Richard", 7),
        ("Jones, Jennifer Linda", 8),
        ("Garcia, Michael Thomas", 9),
        ("Martinez, Sarah Barbara", 10),
        ("Davis, Christopher Nancy", 11),
    ]
    
    dates = [
        ("August 18", "Present"),
        ("August 22", "Present"),
        ("August 25", "Absent"),
        ("August 29", "Present"),
        ("September 1", "Present"),
        ("September 5", "Present"),
        ("September 8", "Absent"),
    ]
    
    widget.load_data(students, dates)
    widget.setGeometry(100, 100, 1400, 700)
    widget.show()
    
    sys.exit(app.exec())