from PyQt6.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QWidget, 
                             QVBoxLayout, 
                             QHBoxLayout, 
                             QPushButton, 
                             QLabel, 
                             QTableView,
                             QHeaderView)
from PyQt6.QtGui import QFont
from .sections_table_model import SectionsTableModel
from .create_section_dialog import CreateSectionDialog
from ....controller.Academics.Tagging.sections_controller import SectionController

class SectionsPage(QWidget):
    def __init__(self):
        super().__init__()

        

        self.model = SectionsTableModel()
        self.controller = SectionController(self, self.model) 
        
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
        
        self.add_btn = QPushButton("Add Section")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setStyleSheet("""
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
        header_layout.addWidget(self.add_btn)
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableView()
        self.table.setObjectName("sectionsTable")
        
        # Sample data
        
        
        
        self.table.setModel(self.model)
        
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        # table.setSelectionBehavior(QTableView.SelectionBehavior.)
        # table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # Set reasonable column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)  # No.
        self.table.setColumnWidth(1, 80)  # Section
        self.table.setColumnWidth(2, 200) # Program
        self.table.setColumnWidth(3, 60)  # Year
        self.table.setColumnWidth(4, 100) # Type
        self.table.setColumnWidth(5, 80)  # Capacity
        
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.add_btn.clicked.connect(self.controller.open_dialog)