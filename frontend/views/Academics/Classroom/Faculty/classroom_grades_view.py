"""
Complete classroom grades application with QAbstractTableModel.
Features: bulk input, draft/upload status, expandable columns.
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
from frontend.model.grade_data_model import GradeDataModel      # noqa: E402
from frontend.controller.grade_controller import GradeController  # noqa: E402
    
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QSpacerItem, QSizePolicy) # noqa: E402
from PyQt6.QtCore import Qt, QSize # noqa: E402
from PyQt6.QtGui import QColor, QPalette # noqa: E402

from table_model import EnhancedGradesTableView # noqa: E402

# Import grading dialog if available
try:
    from grading_system_dialog import connect_grading_button
except ImportError:
    def connect_grading_button(window, label):
        label.setEnabled(False)
        print("Warning: grading_system_dialog.py not found")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Classroom Grades - Enhanced")
        self.setAutoFillBackground(True)
        self.setFixedSize(QSize(1200, 600))
        
        # Initialize models and controllers
        self.grade_model = GradeDataModel()
        self.grade_controller = GradeController(self.grade_model)
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.grade_controller.columns_changed.connect(self.rebuild_table)
        
        # Load sample data
        self.grade_model.load_sample_data()
        self.rebuild_table()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        container = QWidget()
        container.setAutoFillBackground(True)
        pal = container.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("white"))
        container.setPalette(pal)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header layout
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
        # Connect to grading dialog
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
        
        # Add to header layout
        header_layout.addWidget(self.rubrics_combo)
        header_layout.addItem(spacer)
        header_layout.addWidget(self.grading_label)
        header_layout.addWidget(download_button)
        
        # Create enhanced grades table
        self.grades_table = EnhancedGradesTableView(
            self.grade_model,
            self.grade_controller
        )
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.grades_table)
        
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def rebuild_table(self):
        """Rebuild table structure based on current rubric configuration"""
        columns_info = self._build_columns_info()
        self.grades_table.load_data(columns_info)
    
    def _build_columns_info(self):
        """Build column information based on rubric configuration"""
        columns = [
            {'name': 'No.', 'type': 'fixed', 'width': 50},
            {'name': 'Sort by Last Name', 'type': 'fixed', 'width': 200}
        ]
        
        # MIDTERM SECTION
        columns.append({
            'name': 'Midterm Grade',
            'type': 'expandable_main',
            'width': 120,
            'target': 'midterm'
        })
        
        if self.grade_model.get_column_state('midterm_expanded'):
            # Get components from rubric for midterm
            for comp_name in self.grade_model.get_rubric_components('midterm'):
                comp_key = comp_name.replace(' ', '_')
                comp_display_name = comp_name.title()
                
                # Add expandable component header
                columns.append({
                    'name': comp_display_name,
                    'type': 'expandable_component',
                    'width': 120,
                    'term': 'midterm',
                    'component': comp_key
                })
                
                # If this component is expanded, add its sub-items
                state_key = f'{comp_key}_midterm_expanded'
                if self.grade_model.get_column_state(state_key):
                    type_key = self.grade_model.get_component_type_key(comp_name)
                    sub_items = self.grade_model.get_component_items_with_scores(type_key)
                    
                    for item in sub_items:
                        item_name = item['name']
                        max_score = item['max_score']
                        columns.append({
                            'name': f'{item_name} (M)',
                            'type': 'grade_input',
                            'width': 120,
                            'term': 'midterm',
                            'component': comp_key,
                            'component_key': f"{item_name.lower().replace(' ', '')}_midterm",
                            'max_score': max_score  # Pass max_score to column info
                        })
        
        # FINAL TERM SECTION
        columns.append({
            'name': 'Final Term Grade',
            'type': 'expandable_main',
            'width': 130,
            'target': 'finalterm'
        })
        
        if self.grade_model.get_column_state('finalterm_expanded'):
            # Get components from rubric for final term
            for comp_name in self.grade_model.get_rubric_components('final'):
                comp_key = comp_name.replace(' ', '_')
                comp_display_name = comp_name.title()
                
                # Add expandable component header
                columns.append({
                    'name': comp_display_name,
                    'type': 'expandable_component',
                    'width': 120,
                    'term': 'finalterm',
                    'component': comp_key
                })
                
                # If this component is expanded, add its sub-items
                state_key = f'{comp_key}_finalterm_expanded'
                if self.grade_model.get_column_state(state_key):
                    type_key = self.grade_model.get_component_type_key(comp_name)
                    sub_items = self.grade_model.components.get(type_key, [])
                    
                    for sub_item in sub_items:
                        columns.append({
                            'name': f'{sub_item} (F)',
                            'type': 'grade_input',
                            'width': 120,
                            'term': 'finalterm',
                            'component': comp_key,
                            'component_key': f"{sub_item.lower().replace(' ', '')}_finalterm"
                        })
        
        # FINAL GRADE
        columns.append({'name': 'Final Grade', 'type': 'calculated', 'width': 100})
        
        return columns


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())