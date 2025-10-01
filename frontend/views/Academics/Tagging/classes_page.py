from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableView,
                             QStackedWidget, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QFont, QIcon, QColor
from .classes_table_model import ClassesTableModel
from .create_class_dialog import CreateClassDialog

class ClassesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        title = QLabel("Classes")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #2d2d2d;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Sort by dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort by", "Code", "Title", "Section"])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e5631;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                min-width: 100px;
            }
            QComboBox:hover {
                background-color: #2d5a3d;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        header_layout.addWidget(self.sort_combo)
        
        # Add Class button
        self.add_btn = QPushButton("Add Class")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #2d2d2d;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ffcd38;
            }
        """)
        header_layout.addWidget(self.add_btn)
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableView()
        self.table.setObjectName("classesTable")
        
        # Sample data
        data = [
            {'no': 1, 'code': 'IT57', 'title': 'Fundamentals of Database', 
             'units': 3, 'section': '3A', 'schedule': 'TTH 7:00 - 7:30 AM',
             'room': 'CISC Room 3', 'instructor': 'Juan Dela Cruz', 'type': 'Regular'},
            {'no': 2, 'code': 'CS101', 'title': 'Introduction to Programming', 
             'units': 3, 'section': '1A', 'schedule': 'MW 9:00 - 10:30 AM',
             'room': 'CISC Room 1', 'instructor': 'Maria Santos', 'type': 'Regular'}
        ]
        
        model = ClassesTableModel(data)
        self.table.setModel(model)
        
        # Table styling
        self.table.setStyleSheet("""
            QTableView {
                background-color: white;
                border-radius: 8px;
                gridline-color: #e0e0e0;
                selection-background-color: #1e5631;
                selection-color: white;
            }
            QTableView::item {
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableView::item:alternate {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #1e5631;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableView.SelectionMode.NoSelection)

        
        # Set reasonable column widths
        header = self.table.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)

        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 10)  # No.
        self.table.setColumnWidth(1, 60)  # Code
        self.table.setColumnWidth(2, 200) # Title
        self.table.setColumnWidth(3, 30)  # Units
        self.table.setColumnWidth(4, 60)  # Section
        self.table.setColumnWidth(5, 120) # Schedule
        self.table.setColumnWidth(6, 60) # Room
        self.table.setColumnWidth(7, 150) # Instructor
        self.table.setColumnWidth(8, 80) # Type
        self.table.setColumnWidth(9, 80)  # Edit button
        
        # Add Edit buttons to last column
        for row in range(model.rowCount()):
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: #2d2d2d;
                    padding: 4px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #ffcd38;
                }
            """)
            self.table.setIndexWidget(model.index(row, 9), edit_btn)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.add_btn.clicked.connect(lambda: CreateClassDialog(self).exec())
