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
from frontend.model.Academics.Tagging.section_table_model import SectionTableModel
from frontend.views.Academics.Tagging.create_section_dialog import CreateSectionDialog
from frontend.controller.Academics.Tagging.sections_controller import SectionsController

class SectionsPage(QWidget):
    """
    Complete sections management page with full CRUD functionality.

    Flow:
    User interacts with this page
        → Page calls Controller methods
        → Controller calls Service methods
        → Controller updates Model
        → Model notifies View (automatic Qt signals)
        → View refreshes display
    """

    def __init__(self):
        super().__init__()

        self.controller = SectionsController(parent_widget=self) 
        self.model = SectionTableModel()
        self.controller.set_model(self.model)
        
        self.init_ui()
        self.controller.load_sections()
    
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

        self.edit_btn = QPushButton("Edit Section")
        self.edit_btn.setFixedHeight(40)
        self.edit_btn.setStyleSheet("""
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

        self.delete_btn = QPushButton("Delete Section")
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setStyleSheet("""
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

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedHeight(40)
        self.refresh_btn.setStyleSheet("""
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
        header_layout.addWidget(self.edit_btn)
        header_layout.addWidget(self.delete_btn)
        header_layout.addWidget(self.refresh_btn)
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

        # connect signals to slots
        self._connect_signals()

    def _connect_signals(self) -> None:
        """
        Connect page signals to its appropriate slots.
        """
        self.add_btn.clicked.connect(self.handle_add)
        self.edit_btn.clicked.connect(self.handle_edit)
        self.delete_btn.clicked.connect(self.handle_delete)
        self.refresh_btn.clicked.connect(self.handle_refresh)

    def load_sections(self):
        pass 

    # =========================================================================
    # CRUD OPERATIONS  
    # =========================================================================

    def handle_add(self) -> None:
        """
        Handle add button click.
        
        Data Flow:
        1. Open CreateSectionDialog
        2. If user clicks Create:
           → Get data from dialog
           → Pass to controller
           → Controller validates and calls service
           → Controller updates model
           → View automatically refreshes
        """
        dialog = CreateSectionDialog(self)

        if dialog.exec():
            success = self.controller.handle_create_section(dialog)

            # if success:
            #     self.load_sections() # reload to show new section

                # last_row = self.model.rowCount() - 1
                # if last_row >= 0:
                #     self.table.selectRow(last_row)



    def handle_edit(self):
        pass 

    def handle_delete(self):
        pass

    def handle_refresh(self):
        pass 