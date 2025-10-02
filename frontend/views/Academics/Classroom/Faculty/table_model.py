"""
Custom QAbstractTableModel implementation with:
- Bulk input support in headers
- Draft/upload status for grades
- Expandable column headers
- FIXED: Better text alignment and display
"""
import os
import sys

# Navigate 5 levels up to get to the project's root directory (MAIN_MODULE2)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

# Add the project root to the system path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# The comment below tells the linter to ignore the "E402: module level import not at top of file" warning.
# We are doing this intentionally and correctly here.
from frontend.model.grades_table_model import GradesTableModel # noqa: E402

from PyQt6.QtWidgets import (
    QTableView, QHeaderView, QStyledItemDelegate, QLineEdit,
    QWidget, QHBoxLayout, QMenu, QToolButton, QLabel, QStyle 
)
from PyQt6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, pyqtSignal, QVariant
)
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush


class BulkInputHeaderView(QHeaderView):
    """
    Custom header with:
    - Expandable indicators
    - Bulk input widgets
    - Draft/upload options menu
    - FIXED: Better text centering and visibility
    """
    
    section_expand_clicked = pyqtSignal(int, dict)  # section, column_info
    bulk_input_changed = pyqtSignal(int, str)  # column, value
    upload_column_clicked = pyqtSignal(int)  # column
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bulk_widgets = {}  # {column: widget}
        self.sectionClicked.connect(self._on_section_clicked)
    
    def _on_section_clicked(self, logical_index):
        """Handle section click for expandable columns"""
        model = self.model()
        if not model:
            return
        
        col_info = model.headerData(logical_index, Qt.Orientation.Horizontal, 
                                     GradesTableModel.ColumnInfoRole)
        
        if col_info and col_info.get('type') in ['expandable_main', 'expandable_component']:
            self.section_expand_clicked.emit(logical_index, col_info)
    
    def paintSection(self, painter, rect, logicalIndex):
        """Custom paint for header sections with FIXED text display"""
        model = self.model()
        if not model:
            super().paintSection(painter, rect, logicalIndex)
            return
        
        col_info = model.headerData(logicalIndex, Qt.Orientation.Horizontal,
                                     GradesTableModel.ColumnInfoRole)
        
        if not col_info:
            super().paintSection(painter, rect, logicalIndex)
            return
        
        col_type = col_info.get('type', '')
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Draw Background Color
        # ═══════════════════════════════════════════════════════════════
        if col_type == 'grade_input':
            bg_color = QColor("#036800")  # Darker green for grade columns
        else:
            bg_color = QColor("#084924")  # Standard green
        
        painter.fillRect(rect, bg_color)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Draw Border
        # ═══════════════════════════════════════════════════════════════
        painter.setPen(QPen(QColor("#0A5A2A"), 1))
        painter.drawLine(rect.topRight(), rect.bottomRight())
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Setup Text Drawing
        # ═══════════════════════════════════════════════════════════════
        painter.setPen(QColor("white"))
        
        # Use slightly smaller font for better fit
        font = QFont()
        font.setPointSize(10)  # Smaller font
        font.setBold(True)
        painter.setFont(font)
        
        # Get the text to display
        text = model.headerData(logicalIndex, Qt.Orientation.Horizontal, 
                                Qt.ItemDataRole.DisplayRole)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Calculate Text Rectangle (FIXED for better visibility)
        # ═══════════════════════════════════════════════════════════════
        if col_type == 'grade_input':
            # For grade columns: leave space at BOTTOM for bulk input widget
            text_rect = rect.adjusted(
                8,      # Left padding: 8px from left edge
                5,      # Top padding: 5px from top
                -8,     # Right padding: 8px from right edge
                -30     # Bottom padding: 30px from bottom (space for bulk widget)
            )
            text_alignment = Qt.AlignmentFlag.AlignCenter
            
        elif col_type in ['expandable_main', 'expandable_component']:
            # For expandable columns: leave space at RIGHT for expand indicator
            text_rect = rect.adjusted(
                8,      # Left padding
                5,      # Top padding
                -25,    # Right padding (more space for indicator)
                -5      # Bottom padding
            )
            text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            
        else:
            # For fixed columns (ID, Name, Final Grade)
            text_rect = rect.adjusted(8, 5, -8, -5)
            
            # Center align for ID and Final Grade, left align for Name
            if logicalIndex == 0 or 'Final Grade' in str(text):
                text_alignment = Qt.AlignmentFlag.AlignCenter
            else:
                text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Draw the Text with Word Wrap
        # ═══════════════════════════════════════════════════════════════
        painter.drawText(
            text_rect,
            text_alignment | Qt.TextFlag.TextWordWrap,  # Enable word wrap
            str(text) if text else ""
        )
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 6: Draw Expand Indicator (for expandable columns)
        # ═══════════════════════════════════════════════════════════════
        if col_type in ['expandable_main', 'expandable_component']:
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            indicator_rect = rect.adjusted(rect.width() - 22, 0, -5, 0)
            painter.drawText(
                indicator_rect,
                Qt.AlignmentFlag.AlignCenter,
                "›"  # Right arrow indicator
            )
    
    def create_bulk_widget(self, column, max_score=40):
        """Create bulk input widget for a grade column"""
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        
        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText("__")
        input_field.setMaximumWidth(45)
        input_field.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        input_field.textChanged.connect(
            lambda text, col=column: self._on_bulk_input_changed(col, text, max_score)
        )
        
        # "out of" label
        out_of_label = QLabel(f"/{max_score}")
        out_of_label.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
        
        # Options button
        options_btn = QToolButton()
        options_btn.setText("⋮")
        options_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QToolButton:hover {
                background: rgba(255,255,255,0.2);
                border-radius: 3px;
            }
        """)
        
        menu = QMenu()
        menu.addAction("Keep as Draft")
        upload_action = menu.addAction("Upload All")
        upload_action.triggered.connect(lambda col=column: self.upload_column_clicked.emit(col))
        
        options_btn.setMenu(menu)
        options_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        layout.addWidget(input_field)
        layout.addWidget(out_of_label)
        layout.addStretch()
        layout.addWidget(options_btn)
        
        return container
    
    def _on_bulk_input_changed(self, column, text, max_score):
        """Handle bulk input change"""
        if text:
            # Format as fraction
            value = f"{text}/{max_score}"
            self.bulk_input_changed.emit(column, value)


class GradeInputDelegate(QStyledItemDelegate):
    """Custom delegate for grade input cells"""
    
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setPlaceholderText("e.g., 35/40")
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.setText(str(value) if value else "")
    
    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.ItemDataRole.EditRole)


class EnhancedGradesTableView(QTableView):
    """
    Main table view with all features integrated
    FIXED: Better text display and column sizing
    """
    
    def __init__(self, data_model, controller, parent=None):
        super().__init__(parent)
        
        self.data_model = data_model
        self.controller = controller
        
        # Setup model
        self.table_model = GradesTableModel(data_model, controller)
        self.setModel(self.table_model)
        
        # Setup custom header
        self.custom_header = BulkInputHeaderView(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self.custom_header)
        
        # Setup delegate
        self.delegate = GradeInputDelegate(self)
        self.setItemDelegate(self.delegate)
        
        # Connect signals
        self.custom_header.section_expand_clicked.connect(self._on_header_expand)
        self.custom_header.bulk_input_changed.connect(self._on_bulk_input)
        self.custom_header.upload_column_clicked.connect(self._on_upload_column)
        
        # ═══════════════════════════════════════════════════════════════
        # TABLE APPEARANCE SETTINGS
        # ═══════════════════════════════════════════════════════════════
        
        # Row settings
        self.setAlternatingRowColors(True)
        self.verticalHeader().setDefaultSectionSize(40)  # Row height
        self.verticalHeader().setVisible(False)  # Hide row numbers
        
        # Selection settings
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # Styling
        self.setStyleSheet("""
            QTableView {
                background-color: white;
                alternate-background-color: #F8F9FA;
                gridline-color: #E0E0E0;
                border: none;
            }
            QTableView::item {
                padding: 8px;
                color: #000000;
            }
            QTableView::item:selected {
                background-color: #E8F5E8;
                color: #000000;
            }
        """)
        
        self.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #084924;
                color: white;
                padding: 8px 4px;
                border: none;
                border-right: 1px solid #0A5A2A;
                font-weight: bold;
                font-size: 11px;
                min-height: 70px;
            }
        """)
        
        # Set minimum height for headers (space for bulk widgets)
        self.horizontalHeader().setMinimumHeight(70)
        
        # Enable word wrap in cells
        self.setWordWrap(True)
    
    def load_data(self, columns_info):
        """
        Load column structure and add bulk widgets
        FIXED: Better column width handling
        """
        self.table_model.setup_columns(columns_info)
        
        # Remove old bulk widgets
        for widget in self.custom_header.bulk_widgets.values():
            widget.deleteLater()
        self.custom_header.bulk_widgets = {}
        
        # ═══════════════════════════════════════════════════════════════
        # SET COLUMN WIDTHS AND ADD BULK WIDGETS
        # ═══════════════════════════════════════════════════════════════
        
        for i, col_info in enumerate(columns_info):
            col_type = col_info.get('type', '')
            width = col_info.get('width', 100)
            
            # Set column width
            self.setColumnWidth(i, width)
            
            # Special handling for different column types
            if col_type == 'fixed':
                # Fixed columns (ID, Name) - set specific widths
                if i == 0:  # ID column
                    self.setColumnWidth(i, 60)
                elif i == 1:  # Name column
                    self.setColumnWidth(i, 220)
            
            elif col_type == 'grade_input':
                # Grade input columns - add bulk widget
                max_score = col_info.get('max_score', 40)
                widget = self.custom_header.create_bulk_widget(i, max_score)
                
                # Position widget at bottom of header
                header_rect = self.custom_header.sectionViewportPosition(i)
                widget.setGeometry(
                    header_rect,
                    self.custom_header.height() - 28,  # Position near bottom
                    width,
                    25  # Height of bulk widget
                )
                widget.show()
                self.custom_header.bulk_widgets[i] = widget
            
            elif col_type in ['expandable_main', 'expandable_component']:
                # Expandable columns - ensure adequate width
                min_width = 140
                if width < min_width:
                    self.setColumnWidth(i, min_width)
            
            elif col_type == 'calculated':
                # Final grade column
                self.setColumnWidth(i, 110)
        
        # ═══════════════════════════════════════════════════════════════
        # OPTIONAL: Auto-resize name column to fill remaining space
        # ═══════════════════════════════════════════════════════════════
        # Uncomment if you want the name column to stretch
        # self.horizontalHeader().setSectionResizeMode(
        #     1, 
        #     QHeaderView.ResizeMode.Stretch
        # )
    
    def _on_header_expand(self, section, col_info):
        """Handle header expand/collapse"""
        self.controller.handle_header_expand_clicked(col_info)
    
    def _on_bulk_input(self, column, value):
        """Handle bulk input for a column"""
        self.table_model.bulk_set_grades(column, value)
    
    def _on_upload_column(self, column):
        """Handle upload column grades"""
        self.table_model.upload_column_grades(column)
    
    def resizeEvent(self, event):
        """Reposition bulk widgets on resize"""
        super().resizeEvent(event)
        for col, widget in self.custom_header.bulk_widgets.items():
            header_pos = self.custom_header.sectionViewportPosition(col)
            width = self.columnWidth(col)
            widget.setGeometry(
                header_pos,
                self.custom_header.height() - 28,
                width,
                25
            )