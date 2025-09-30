from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableView,
                             QStackedWidget, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QFont, QIcon, QColor
from .sections_table_model import SectionsTableModel
from .create_section_dialog import CreateSectionDialog

class SectionsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with title and add button
        header_layout = QHBoxLayout()
        title = QLabel("Sections")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #2d2d2d;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("Add Section")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e5631;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d5a3d;
            }
        """)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Table
        table = QTableView()
        table.setObjectName("sectionsTable")
        
        # Sample data
        data = [
            {'no': 1, 'section': 'A', 'program': 'BS Computer Science', 
             'year': 1, 'type': 'Lecture', 'capacity': 40, 'remarks': 'Regular'},
            {'no': 2, 'section': 'B', 'program': 'BS Information Technology', 
             'year': 2, 'type': 'Lecture', 'capacity': 50, 'remarks': 'Regular'}
        ]
        
        model = SectionsTableModel(data)
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
        # table.setSelectionBehavior(QTableView.SelectionBehavior.)
        # table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # Set reasonable column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 60)  # No.
        table.setColumnWidth(1, 80)  # Section
        table.setColumnWidth(2, 200) # Program
        table.setColumnWidth(3, 60)  # Year
        table.setColumnWidth(4, 100) # Type
        table.setColumnWidth(5, 80)  # Capacity
        
        layout.addWidget(table)
        self.setLayout(layout)

        add_btn.clicked.connect(lambda: CreateSectionDialog(self).exec())