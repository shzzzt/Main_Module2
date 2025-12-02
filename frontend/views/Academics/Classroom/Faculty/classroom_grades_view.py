"""
Faculty Grades View - Full grade management interface
Features: bulk input, draft/upload status, expandable columns, grading system management
INTEGRATED WITH DJANGO BACKEND: Loads rubrics, students, and grades from Django API
"""
import os
import sys
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QPushButton, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.services.Academics.model.Academics.Classroom.grade_data_model import GradeDataModel      # noqa: E402
from frontend.controller.Academics.Classroom.grade_controller import GradeController  # noqa: E402

# Import local modules
try:
    from frontend.services.Academics.model.Academics.Classroom.grade_data_model import GradeDataModel
    from frontend.controller.Academics.Classroom.grade_controller import GradeController
    from frontend.views.Academics.Classroom.Faculty.table_model import EnhancedGradesTableView
except ImportError:
    from frontend.services.Academics.model import GradeDataModel
    from .....controller.Academics.Classroom.grade_controller import GradeController
    from .table_model import EnhancedGradesTableView

# Import grading dialog if available
try:
    from frontend.views.Academics.Classroom.Faculty.grading_system_dialog import connect_grading_button
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
        self.api_base_url = "http://127.0.0.1:8000/api/academics"

        self.setMinimumSize(940, 530)
        
        # Initialize models and controllers with class ID
        class_id = cls.get('id', 1)
        self.grade_model = GradeDataModel(class_id=class_id)
        self.grade_controller = GradeController(self.grade_model)
        
        # Set current user context
        self.grade_model.set_current_user(username, {'roles': roles, 'primary_role': primary_role})
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.grade_controller.columns_changed.connect(self.rebuild_table)
        
        # Load data from backend
        self.load_rubrics_from_backend()
        self.load_students_from_backend()
        self.rebuild_table()
    
    def load_rubrics_from_backend(self):
        """Load grading rubrics from Django backend API"""
        print(f"[FACULTY GRADES] Loading rubrics for class {self.cls.get('id')}")
        
        if not self.token:
            print("[FACULTY GRADES] No token available, using default rubrics")
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            url = f"{self.api_base_url}/classes/{self.cls['id']}/grading-rubrics/"
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                rubrics_data = response.json()
                print(f"[FACULTY GRADES] Loaded {len(rubrics_data)} rubrics from backend")
                
                # Parse rubrics and update grade model
                self._parse_and_apply_rubrics(rubrics_data)
            elif response.status_code == 404:
                print("[FACULTY GRADES] No rubrics found, using defaults")
            else:
                print(f"[FACULTY GRADES] API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[FACULTY GRADES] Failed to load rubrics: {e}")
    
    def _parse_and_apply_rubrics(self, rubrics_data):
        """Parse rubrics from Django API and apply to grade model"""
        rubric_config = {
            'midterm': {
                'term_percentage': 33,
                'components': []
            },
            'final': {
                'term_percentage': 67,
                'components': []
            }
        }
        
        for rubric in rubrics_data:
            academic_period = rubric.get('academic_period', '')
            term_percentage = float(rubric.get('term_percentage', 0))
            components = rubric.get('components', [])
            
            if academic_period == 'midterm':
                rubric_config['midterm']['term_percentage'] = int(term_percentage)
                rubric_config['midterm']['components'] = [
                    {
                        'id': comp['id'],
                        'name': comp['name'],
                        'percentage': int(float(comp['percentage']))
                    }
                    for comp in components
                ]
            elif academic_period == 'finals':
                rubric_config['final']['term_percentage'] = int(term_percentage)
                rubric_config['final']['components'] = [
                    {
                        'id': comp['id'],
                        'name': comp['name'],
                        'percentage': int(float(comp['percentage']))
                    }
                    for comp in components
                ]
        
        # Update grade model with parsed rubrics
        self.grade_model.update_rubric_config(rubric_config)
        print(f"[FACULTY GRADES] Applied rubrics - Midterm: {len(rubric_config['midterm']['components'])} components, Final: {len(rubric_config['final']['components'])} components")
    
    def load_students_from_backend(self):
        """Load students from Django backend API"""
        print(f"[FACULTY GRADES] Loading students for class {self.cls.get('id')}")
        
        if not self.token:
            print("[FACULTY GRADES] No token available, trying fallback methods")
            self._try_fallback_loading()
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            url = f"{self.api_base_url}/classes/{self.cls['id']}/students/"
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                students_data = response.json()
                print(f"[FACULTY GRADES] Loaded {students_data.get('count', 0)} students from backend")
                
                # Load students into model
                self.grade_model.load_students_from_django_api(students_data)
                
                # Log loaded students
                for student in self.grade_model.students:
                    print(f"  - {student['name']} (ID: {student['id']}, Username: {student.get('username', 'N/A')})")
            else:
                print(f"[FACULTY GRADES] API error: {response.status_code}, trying fallback")
                self._try_fallback_loading()
                
        except requests.exceptions.RequestException as e:
            print(f"[FACULTY GRADES] Failed to load students: {e}, trying fallback")
            self._try_fallback_loading()
    
    def _try_fallback_loading(self):
        """Try fallback loading methods (JSON file, then sample data)"""
        if self._try_load_from_json():
            print("[FACULTY GRADES] Successfully loaded from JSON file")
        else:
            print("[FACULTY GRADES] Using sample data (fallback)")
            self.grade_model.load_sample_data()
    
    def _try_load_from_json(self):
        """Try to load students from JSON file"""
        try:
            json_paths = [
                'data/users_data.json',
                '../data/users_data.json',
                '../../data/users_data.json',
                os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'users_data.json')
            ]
            
            for json_path in json_paths:
                if os.path.exists(json_path):
                    print(f"[FACULTY GRADES] Found JSON file at: {json_path}")
                    self.grade_model.load_students_from_json(json_path)
                    return True
            
            print("[FACULTY GRADES] No JSON file found in expected locations")
            return False
            
        except Exception as e:
            print(f"[FACULTY GRADES] JSON load failed: {e}")
            return False
    
    def setup_ui(self):
        """Setup the faculty interface"""
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("white"))
        self.setPalette(pal)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        header_layout = self._create_header()
        
        self.grades_table = EnhancedGradesTableView(
            self.grade_model,
            self.grade_controller
        )
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.grades_table)
        
        self.setLayout(main_layout)
    
    def _create_header(self):
        """Create header with faculty controls"""
        header_layout = QHBoxLayout()
        
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
        
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
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
        
        # Connect grading button with class_id and token
        self._connect_grading_button_with_backend()
        
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
        
        header_layout.addWidget(self.rubrics_combo)
        header_layout.addItem(spacer)
        header_layout.addWidget(self.grading_label)
        header_layout.addWidget(download_button)
        
        return header_layout
    
    def _connect_grading_button_with_backend(self):
        """Connect grading button with backend integration"""
        def on_grading_click(event):
            from frontend.views.Academics.Classroom.Faculty.grading_system_dialog import show_grading_dialog
            
            # Show dialog with class_id and token for backend integration
            dialog = show_grading_dialog(
                self,
                class_id=self.cls.get('id'),
                token=self.token
            )
            
            # If rubric was saved, reload rubrics and rebuild table
            if dialog.result() == dialog.DialogCode.Accepted:
                print("[FACULTY GRADES] Rubric saved, reloading...")
                self.load_rubrics_from_backend()
                self.rebuild_table()
        
        self.grading_label.mousePressEvent = on_grading_click
    
    def rebuild_table(self):
        """Rebuild table structure based on current rubrics"""
        columns_info = self._build_columns_info()
        self.grades_table.load_data(columns_info)
    
    def _build_columns_info(self):
        """Build column information based on rubric configuration"""
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
    window.setWindowTitle("Faculty Grades View Test")
    window.setGeometry(100, 100, 1000, 700)
    
    mock_cls = {
        'id': 1,
        'name': 'Desktop Application Development',
        'section': 'BSCS-3C'
    }
    
    widget = FacultyGradesView(
        cls=mock_cls,
        username='admin',
        roles=['faculty'],
        primary_role='faculty',
        token='test_token'
    )
    
    window.setCentralWidget(widget)
    window.show()
    
    sys.exit(app.exec())