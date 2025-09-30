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
        sort_combo = QComboBox()
        sort_combo.addItems(["Sort by", "Code", "Title", "Section"])
        sort_combo.setStyleSheet("""
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
        header_layout.addWidget(sort_combo)
        
        # Add Class button
        add_btn = QPushButton("Add Class")
        add_btn.setStyleSheet("""
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
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Table
        table = QTableView()
        table.setObjectName("classesTable")
        
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
        table.setModel(model)
        
        # Table styling
        table.setStyleSheet("""
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
        
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().setMinimumSectionSize(100)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        # table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableView.SelectionMode.NoSelection)

        
        # Set reasonable column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 60)  # No.
        table.setColumnWidth(1, 80)  # Code
        table.setColumnWidth(2, 200) # Title
        table.setColumnWidth(3, 60)  # Units
        table.setColumnWidth(4, 80)  # Section
        table.setColumnWidth(5, 120) # Schedule
        table.setColumnWidth(6, 100) # Room
        table.setColumnWidth(7, 150) # Instructor
        table.setColumnWidth(8, 100) # Type
        table.setColumnWidth(9, 80)  # Edit button
        
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
            table.setIndexWidget(model.index(row, 9), edit_btn)
        
        layout.addWidget(table)
        self.setLayout(layout)

        add_btn.clicked.connect(lambda: CreateClassDialog(self).exec())
