"""
Faculty Grades View - Full grade management interface
Features: bulk input, draft/upload status, expandable columns, grading system management
UPDATED: Correct exam handling (1 for midterm, 2 for final)
"""
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.model.grade_data_model import GradeDataModel      # noqa: E402
from frontend.controller.grade_controller import GradeController  # noqa: E402
    
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QPushButton, QSpacerItem, QSizePolicy
) # noqa: E402
from PyQt6.QtCore import Qt # noqa: E402
from PyQt6.QtGui import QColor, QPalette # noqa: E402

from table_model import EnhancedGradesTableView # noqa: E402

# Import grading dialog if available
try:
    from grading_system_dialog import connect_grading_button
except ImportError:
    def connect_grading_button(window, label):
        label.setEnabled(False)
        print("Warning: grading_system_dialog.py not found")


class FacultyGradesView(QWidget):
    
    def __init__(self, cls, username, roles, primary_role, token, parent=None):
        super().__init__(parent)
        
        self.cls = cls
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token

        self.setMinimumSize(940, 530)
        
        # Initialize models and controllers
        self.grade_model = GradeDataModel()
        self.grade_controller = GradeController(self.grade_model)
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.grade_controller.columns_changed.connect(self.rebuild_table)
        
        # Load data
        self.grade_model.load_sample_data()
        self.rebuild_table()
    
    def setup_ui(self):
        """Setup the faculty interface"""
        # Set background
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("white"))
        self.setPalette(pal)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header with controls
        header_layout = self._create_header()
        
        # Create grades table
        self.grades_table = EnhancedGradesTableView(
            self.grade_model,
            self.grade_controller
        )
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.grades_table)
        
        self.setLayout(main_layout)
    
    def _create_header(self):
        """Create header with faculty controls"""
        header_layout = QHBoxLayout()
        
        # Rubrics combo
        self.rubrics_combo = QComboBox()
        self.rubrics_combo.addItems(["Overall Lecture", "Performance Task", "Quiz", "Exam"])
        self.rubrics_combo.setFixedWidth(150)
        self.rubrics_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                font-size: 12px;
                color: #084924;
                background-color: white;
                font-weight: bold;
            }
            QComboBox:focus {
                border: 2px solid #084924;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #084924;
                selection-background-color: #E8F5E8;
            }
        """)
        
        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Grading System button
        self.grading_label = QLabel("Grading System")
        self.grading_label.setStyleSheet("""
            QLabel {
                background-color: #FDC601;
                color: white;
                border-radius: 3px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QLabel:hover {
                background-color: #E5B200;
            }
        """)
        self.grading_label.setCursor(Qt.CursorShape.PointingHandCursor)
        connect_grading_button(self, self.grading_label)
        
        # Download button
        download_button = QPushButton("📥 Download")
        download_button.setStyleSheet("""
            QPushButton {
                background-color: #084924;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0A5A2A;
            }
        """)
        
        # Add to layout
        header_layout.addWidget(self.rubrics_combo)
        header_layout.addItem(spacer)
        header_layout.addWidget(self.grading_label)
        header_layout.addWidget(download_button)
        
        return header_layout
    
    def rebuild_table(self):
        """Rebuild table structure"""
        columns_info = self._build_columns_info()
        self.grades_table.load_data(columns_info)
    
    def _build_columns_info(self):
        """Build column information"""
        columns = [
            {'name': 'No.', 'type': 'fixed', 'width': 60},
            {'name': 'Sort by Last Name', 'type': 'fixed', 'width': 220}
        ]
        
        # MIDTERM SECTION
        columns.append({
            'name': 'Midterm Grade',
            'type': 'expandable_main',
            'width': 140,
            'target': 'midterm'
        })
        
        if self.grade_model.get_column_state('midterm_expanded'):
            for comp_name in self.grade_model.get_rubric_components('midterm'):
                comp_key = comp_name.replace(' ', '_')
                comp_display_name = comp_name.title()
                
                columns.append({
                    'name': comp_display_name,
                    'type': 'expandable_component',
                    'width': 150,
                    'term': 'midterm',
                    'component': comp_key
                })
                
                state_key = f'{comp_key}_midterm_expanded'
                if self.grade_model.get_column_state(state_key):
                    # Get the correct type key based on component name and term
                    type_key = self.grade_model.get_component_type_key(comp_name, 'midterm')
                    sub_items = self.grade_model.get_component_items_with_scores(type_key)
                    
                    for item in sub_items:
                        item_name = item['name']
                        max_score = item['max_score']
                        columns.append({
                            'name': f'{item_name} (M)',
                            'type': 'grade_input',
                            'width': 130,
                            'term': 'midterm',
                            'component': comp_key,
                            'component_key': f"{item_name.lower().replace(' ', '')}_midterm",
                            'max_score': max_score
                        })
        
        # FINAL TERM SECTION
        columns.append({
            'name': 'Final Term Grade',
            'type': 'expandable_main',
            'width': 150,
            'target': 'finalterm'
        })
        
        if self.grade_model.get_column_state('finalterm_expanded'):
            for comp_name in self.grade_model.get_rubric_components('final'):
                comp_key = comp_name.replace(' ', '_')
                comp_display_name = comp_name.title()
                
                columns.append({
                    'name': comp_display_name,
                    'type': 'expandable_component',
                    'width': 150,
                    'term': 'finalterm',
                    'component': comp_key
                })
                
                state_key = f'{comp_key}_finalterm_expanded'
                if self.grade_model.get_column_state(state_key):
                    # Get the correct type key based on component name and term
                    type_key = self.grade_model.get_component_type_key(comp_name, 'finalterm')
                    sub_items = self.grade_model.get_component_items_with_scores(type_key)
                    
                    for item in sub_items:
                        item_name = item['name']
                        max_score = item['max_score']
                        columns.append({
                            'name': f'{item_name} (F)',
                            'type': 'grade_input',
                            'width': 130,
                            'term': 'finalterm',
                            'component': comp_key,
                            'component_key': f"{item_name.lower().replace(' ', '')}_finalterm",
                            'max_score': max_score
                        })
        
        # FINAL GRADE
        columns.append({
            'name': 'Final Grade',
            'type': 'calculated',
            'width': 110
        })
        
        return columns
    
    def clear(self):
        """Clear the view"""
        pass


# Test runner
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Student Grades View Test")
    window.setGeometry(100, 100, 1000, 700)
    
    # Mock student data
    mock_cls = {
        'id': 'CS101',
        'name': 'Introduction to Computer Science',
        'section': 'A'
    }
    
    widget = FacultyGradesView(
        cls=mock_cls,
        username='john.doe',
        roles=['faculty'],
        primary_role='faculty',
        token='test_token'
    )
    
    window.setCentralWidget(widget)
    window.show()
    
    sys.exit(app.exec())