"""
Custom QAbstractTableModel implementation with:
- Bulk input support in headers
- Draft/upload status for grades
- Expandable column headers
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


# class GradesTableModel(QAbstractTableModel):
#     """
#     Table model for grades with draft/upload status support.
#     """
    
#     # Custom roles
#     IsDraftRole = Qt.ItemDataRole.UserRole + 1
#     ComponentKeyRole = Qt.ItemDataRole.UserRole + 2
#     ColumnInfoRole = Qt.ItemDataRole.UserRole + 3
    
#     def __init__(self, data_model, controller, parent=None):
#         super().__init__(parent)
#         self.data_model = data_model
#         self.controller = controller
#         self.columns = []  # List of column info dicts
        
#     def setup_columns(self, columns_info):
#         """Setup columns based on rubric configuration"""
#         self.beginResetModel()
#         self.columns = columns_info
#         self.endResetModel()
    
#     def rowCount(self, parent=QModelIndex()):
#         return len(self.data_model.students)
    
#     def columnCount(self, parent=QModelIndex()):
#         return len(self.columns)
    
#     def data(self, index, role=Qt.ItemDataRole.DisplayRole):
#         if not index.isValid():
#             return QVariant()
        
#         row, col = index.row(), index.column()
#         if col >= len(self.columns):
#             return QVariant()
            
#         col_info = self.columns[col]
#         col_type = col_info.get('type', '')
#         student = self.data_model.students[row]
        
#         # Student ID column
#         if col == 0:
#             if role == Qt.ItemDataRole.DisplayRole:
#                 return student['id']
#             elif role == Qt.ItemDataRole.TextAlignmentRole:
#                 return Qt.AlignmentFlag.AlignCenter
        
#         # Student Name column
#         elif col == 1:
#             if role == Qt.ItemDataRole.DisplayRole:
#                 return student['name']
#             elif role == Qt.ItemDataRole.TextAlignmentRole:
#                 return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
#         # Grade input columns
#         elif col_type == 'grade_input':
#             component_key = col_info.get('component_key', '')
#             grade_item = self.data_model.get_grade(student['id'], component_key)
            
#             if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
#                 return grade_item.value
#             elif role == self.IsDraftRole:
#                 return grade_item.is_draft
#             elif role == Qt.ItemDataRole.BackgroundRole:
#                 if grade_item.is_draft and grade_item.value:
#                     return QBrush(QColor("#FFF9E6"))  # Yellow for draft
#                 elif grade_item.value:
#                     return QBrush(QColor("#E8F5E9"))  # Green for uploaded
#                 return QBrush(QColor("#FFFFFF"))  # White for empty
#             elif role == Qt.ItemDataRole.TextAlignmentRole:
#                 return Qt.AlignmentFlag.AlignCenter
        
#         # Calculated columns (averages, final grade)
#         elif col_type in ['calculated', 'expandable_main', 'expandable_component']:
#             if role == Qt.ItemDataRole.DisplayRole:
#                 return self._calculate_display_value(row, col_info)
#             elif role == Qt.ItemDataRole.TextAlignmentRole:
#                 return Qt.AlignmentFlag.AlignCenter
#             elif role == Qt.ItemDataRole.BackgroundRole:
#                 return QBrush(QColor("#F8F9FA"))
#             elif role == Qt.ItemDataRole.FontRole:
#                 font = QFont()
#                 font.setBold(True)
#                 return font
        
#         # Store column info for header
#         if role == self.ColumnInfoRole:
#             return col_info
        
#         return QVariant()
    
#     def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
#         if not index.isValid():
#             return False
        
#         row, col = index.row(), index.column()
#         col_info = self.columns[col]
        
#         if col_info.get('type') == 'grade_input':
#             component_key = col_info.get('component_key', '')
#             student_id = self.data_model.students[row]['id']
            
#             if role == Qt.ItemDataRole.EditRole:
#                 self.data_model.set_grade(student_id, component_key, value, is_draft=True)
#                 self.dataChanged.emit(index, index)
#                 # Emit changes for calculated columns
#                 self._emit_calculated_changes(row)
#                 return True
        
#         return False
    
#     def flags(self, index):
#         if not index.isValid():
#             return Qt.ItemFlag.NoItemFlags
        
#         col_info = self.columns[index.column()]
#         if col_info.get('type') == 'grade_input':
#             return (Qt.ItemFlag.ItemIsEnabled | 
#                     Qt.ItemFlag.ItemIsSelectable | 
#                     Qt.ItemFlag.ItemIsEditable)
        
#         return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
#     def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
#         if orientation == Qt.Orientation.Horizontal:
#             if role == Qt.ItemDataRole.DisplayRole:
#                 if section < len(self.columns):
#                     return self.columns[section].get('name', '')
#             elif role == self.ColumnInfoRole:
#                 if section < len(self.columns):
#                     return self.columns[section]
#         return QVariant()
    
#     def _calculate_display_value(self, row, col_info):
#         """Calculate display value for calculated columns"""
#         col_name = col_info.get('name', '')
#         student_id = self.data_model.students[row]['id']
#         calculated = self.controller.calculate_grades_for_student(student_id)
        
#         if 'Midterm Grade' in col_name:
#             return calculated['midterm_avg']
#         elif 'Final Term Grade' in col_name:
#             return calculated['finalterm_avg']
#         elif 'Final Grade' in col_name:
#             return calculated['final_grade']
        
#         return "0.00"
    
#     def _emit_calculated_changes(self, row):
#         """Emit dataChanged for all calculated columns in a row"""
#         for col, col_info in enumerate(self.columns):
#             if col_info.get('type') in ['calculated', 'expandable_main', 'expandable_component']:
#                 index = self.index(row, col)
#                 self.dataChanged.emit(index, index)
    
#     def bulk_set_grades(self, col, value):
#         """Set grade value for all students in a column"""
#         col_info = self.columns[col]
#         if col_info.get('type') != 'grade_input':
#             return
        
#         component_key = col_info.get('component_key', '')
#         self.data_model.bulk_set_grades(component_key, value)
        
#         # Emit changes for entire column
#         top_left = self.index(0, col)
#         bottom_right = self.index(self.rowCount() - 1, col)
#         self.dataChanged.emit(top_left, bottom_right)
        
#         # Update calculated columns
#         for row in range(self.rowCount()):
#             self._emit_calculated_changes(row)
    
#     def upload_column_grades(self, col):
#         """Mark all grades in column as uploaded"""
#         col_info = self.columns[col]
#         if col_info.get('type') != 'grade_input':
#             return
        
#         component_key = col_info.get('component_key', '')
#         self.data_model.upload_grades(component_key)
        
#         # Emit changes for entire column
#         top_left = self.index(0, col)
#         bottom_right = self.index(self.rowCount() - 1, col)
#         self.dataChanged.emit(top_left, bottom_right)


class BulkInputHeaderView(QHeaderView):
    """
    Custom header with:
    - Expandable indicators
    - Bulk input widgets
    - Draft/upload options menu
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
        """Custom paint for header sections"""
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
        
        # Background color
        if col_type == 'grade_input':
            bg_color = QColor("#036800")
        else:
            bg_color = QColor("#084924")
        
        painter.fillRect(rect, bg_color)
        
        # Border
        painter.setPen(QPen(QColor("#0A5A2A"), 1))
        painter.drawLine(rect.topRight(), rect.bottomRight())
        
        # Text
        painter.setPen(QColor("white"))
        painter.setFont(self.font())
        text = model.headerData(logicalIndex, Qt.Orientation.Horizontal, 
                                Qt.ItemDataRole.DisplayRole)
        
        # Reserve space for bulk input widget if grade_input column
        if col_type == 'grade_input':
            text_rect = rect.adjusted(4, 0, -4, -25)  # Leave space at bottom
        else:
            text_rect = rect.adjusted(4, 0, -30, 0)  # Leave space for expand indicator
        
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 
                        str(text) if text else "")
        
        # Expand indicator
        if col_type in ['expandable_main', 'expandable_component']:
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            indicator_rect = rect.adjusted(rect.width() - 20, 0, -5, 0)
            painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, " >")
    
    def create_bulk_widget(self, column, max_score=40):
        """Create bulk input widget for a grade column"""
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText("__")
        input_field.setMaximumWidth(40)
        input_field.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #ccc;
                border-radius: 2px;
                padding: 2px;
                font-size: 10px;
            }
        """)
        input_field.textChanged.connect(
            lambda text, col=column: self._on_bulk_input_changed(col, text, max_score)
        )
        
        # "out of" label
        out_of_label = QLabel(f"/{max_score}")
        out_of_label.setStyleSheet("color: white; font-size: 10px;")
        
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
        
        # Table settings
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        
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
                min-height: 60px;
            }
        """)
        
        # Set minimum height for headers to accommodate bulk widgets
        self.horizontalHeader().setMinimumHeight(60)
    
    def load_data(self, columns_info):
        """Load column structure and add bulk widgets"""
        self.table_model.setup_columns(columns_info)
        
        # Remove old bulk widgets
        for widget in self.custom_header.bulk_widgets.values():
            widget.deleteLater()
        self.custom_header.bulk_widgets = {}
        
        # Set column widths and add bulk widgets for grade input columns
        for i, col_info in enumerate(columns_info):
            width = col_info.get('width', 100)
            self.setColumnWidth(i, width)
            
            # Add bulk input widget for grade columns
            if col_info.get('type') == 'grade_input':
                # Get max score from component configuration
                # Default to 40 for now, can be configured per component
                max_score = 40
                widget = self.custom_header.create_bulk_widget(i, max_score)
                
                # Position widget at bottom of header
                header_rect = self.custom_header.sectionViewportPosition(i)
                widget.setGeometry(
                    header_rect,
                    self.custom_header.height() - 25,
                    width,
                    23
                )
                widget.show()
                self.custom_header.bulk_widgets[i] = widget
    
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
                self.custom_header.height() - 25,
                width,
                23
            )