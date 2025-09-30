from PyQt6.QtCore import QObject, pyqtSignal
from .grade_item import GradeItem

class GradeDataModel(QObject):
    """
    Main data model holding all application data.
    Single source of truth for students, grades, and rubric configuration.
    """
    data_reset = pyqtSignal()
    data_updated = pyqtSignal()
    columns_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.students = []
        
        # Component types with sub-items
        self.components = {
            'performance_tasks': ['PT1', 'PT2', 'PT3'],
            'quizzes': ['Quiz 1', 'Quiz 2', 'Quiz 3', 'Quiz 4'],
            'exams': ['Prelim Exam', 'Final Exam']
        }
        
        # Max scores for each component type
        self.component_max_scores = {
            'performance_tasks': 50,
            'quizzes': 40,
            'exams': 100
        }
        
        # Rubric configuration
        self.rubric_config = {
            'midterm': {
                'term_percentage': 33,
                'components': {
                    'performance task': 20,
                    'quiz': 30,
                    'exam': 50
                }
            },
            'final': {
                'term_percentage': 67,
                'components': {
                    'performance task': 20,
                    'quiz': 30,
                    'exam': 50
                }
            }
        }
        
        # Component type mapping
        self.component_type_mapping = {
            'performance task': 'performance_tasks',
            'quiz': 'quizzes',
            'exam': 'exams'
        }
        
        # Column expansion states
        self.column_states = {
            'midterm_expanded': False,
            'finalterm_expanded': False,
        }
        self._initialize_component_states()
        
        # Grade storage: {student_id: {component_key: GradeItem}}
        self.grades = {}

    def _initialize_component_states(self):
        """Initialize column states for all component types"""
        for term in ['midterm', 'finalterm']:
            term_key = 'midterm' if term == 'midterm' else 'final'
            for comp_name in self.rubric_config[term_key]['components'].keys():
                comp_key = comp_name.replace(' ', '_')
                state_key = f'{comp_key}_{term}_expanded'
                if state_key not in self.column_states:
                    self.column_states[state_key] = False

    def load_sample_data(self):
        """Load sample student data"""
        self.students = [
            {'id': '101', 'name': "Castro, Carlos Fidel"},
            {'id': '102', 'name': "Santos, Maria Elena"},
            {'id': '103', 'name': "Garcia, Juan Pablo"},
            {'id': '104', 'name': "Rodriguez, Ana Sofia"}
        ]
        for student in self.students:
            self.grades[student['id']] = {}
        self.data_reset.emit()

    def get_column_state(self, key):
        """Get column expansion state"""
        return self.column_states.get(key, False)

    def set_column_state(self, key, value):
        """Set column expansion state"""
        if self.column_states.get(key) != value:
            self.column_states[key] = value
            self.columns_changed.emit()

    def set_grade(self, student_id, component_key, value, is_draft=True):
        """Set grade for a student's component"""
        if student_id not in self.grades:
            self.grades[student_id] = {}
        
        if component_key not in self.grades[student_id]:
            self.grades[student_id][component_key] = GradeItem()
        
        self.grades[student_id][component_key].value = value
        self.grades[student_id][component_key].is_draft = is_draft
        self.data_updated.emit()

    def get_grade(self, student_id, component_key):
        """Get grade item for a student's component"""
        if student_id in self.grades and component_key in self.grades[student_id]:
            return self.grades[student_id][component_key]
        return GradeItem()

    def bulk_set_grades(self, component_key, value):
        """Set grade value for all students in a component"""
        for student_id in self.grades.keys():
            self.set_grade(student_id, component_key, value, is_draft=True)

    def upload_grades(self, component_key):
        """Mark grades as uploaded (not draft) for a component"""
        for student_id in self.grades.keys():
            if component_key in self.grades[student_id]:
                self.grades[student_id][component_key].is_draft = False
        self.data_updated.emit()

    def get_component_type_key(self, component_name):
        """Get the component type key for a component name"""
        comp_name_lower = component_name.lower()
        return self.component_type_mapping.get(comp_name_lower, 'performance_tasks')

    def get_rubric_components(self, term):
        """Get list of component names for a term"""
        term_key = 'midterm' if term == 'midterm' else 'final'
        return list(self.rubric_config[term_key]['components'].keys())

    def get_component_percentage(self, component_name, term):
        """Get percentage for a component in a term"""
        term_key = 'midterm' if term == 'midterm' else 'final'
        comp_name_lower = component_name.lower()
        return self.rubric_config[term_key]['components'].get(comp_name_lower, 0)

    def get_component_items_with_scores(self, type_key):
        """
        Get list of component items with their max scores.
        Returns list of dicts with 'name' and 'max_score' keys.
        """
        items = self.components.get(type_key, [])
        max_score = self.component_max_scores.get(type_key, 40)
        
        return [{'name': item, 'max_score': max_score} for item in items]

    def update_rubric_config(self, rubric_data):
        """Update rubric configuration from grading system dialog"""
        # Update rubric config
        self.rubric_config = {
            'midterm': {
                'term_percentage': rubric_data['midterm']['term_percentage'],
                'components': {}
            },
            'final': {
                'term_percentage': rubric_data['final']['term_percentage'],
                'components': {}
            }
        }
        
        # Map component names and percentages
        for comp in rubric_data['midterm']['components']:
            comp_name = comp['name'].lower()
            self.rubric_config['midterm']['components'][comp_name] = comp['percentage']
        
        for comp in rubric_data['final']['components']:
            comp_name = comp['name'].lower()
            self.rubric_config['final']['components'][comp_name] = comp['percentage']
        
        # Update component type mapping
        self.component_type_mapping = {}
        all_component_names = set()
        for term_key in ['midterm', 'final']:
            for comp in rubric_data[term_key]['components']:
                comp_name = comp['name'].lower()
                all_component_names.add(comp_name)
        
        for comp_name in all_component_names:
            if 'task' in comp_name or 'pt' in comp_name or 'performance' in comp_name:
                self.component_type_mapping[comp_name] = 'performance_tasks'
            elif 'quiz' in comp_name:
                self.component_type_mapping[comp_name] = 'quizzes'
            elif 'exam' in comp_name:
                self.component_type_mapping[comp_name] = 'exams'
            else:
                self.component_type_mapping[comp_name] = 'performance_tasks'
        
        # Reinitialize column states
        self._initialize_component_states()
        self.columns_changed.emit()