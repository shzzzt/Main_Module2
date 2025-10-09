"""
Student Grades View - Read-only view showing student's own grades
"""

import os
import sys
    
from PyQt6.QtWidgets import ( QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame ) # noqa: E402
from PyQt6.QtCore import Qt # noqa: E402
from PyQt6.QtGui import QColor, QPalette, QFont # noqa: E402
# Navigate 5 levels up to get to the project's root directory
# i dont know unsaon pagpa work using frontend....... dili ga work sa akoa basin naa lang ems mali na type
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

# # Add the project root to the system path
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

# from frontend.model.grade_data_model import GradeDataModel      # noqa: E402
# from frontend.controller.grade_controller import GradeController  # noqa: E402

try:
    from frontend.model.grade_data_model import GradeDataModel
    from frontend.controller.grade_controller import GradeController
except ImportError:
    # Fallback for development
    from ....model.grade_data_model import GradeDataModel
    from ....controller.grade_controller import GradeController



class ExpandableGradeRow(QWidget):
    
    def __init__(self, title, score, max_score, percentage, bg_color="#084924", has_arrow=True, parent=None):
        super().__init__(parent)
        self.is_expanded = False
        self.bg_color = bg_color
        self.sub_items = []
        self.has_arrow = has_arrow
        
        # Main layout - no margins, no spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header row
        self.header = QWidget()
        self.header.setFixedHeight(45)
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
            }}
        """)
        if has_arrow:
            self.header.setCursor(Qt.CursorShape.PointingHandCursor)
            self.header.mousePressEvent = self.toggle_expand
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setSpacing(10)
        
        # Arrow indicator (only if has_arrow is True)
        if has_arrow:
            self.arrow_label = QLabel(">")
            self.arrow_label.setStyleSheet("""
                color: white;
                font-size: 16px;
                font-weight: bold;
            """)
            self.arrow_label.setFixedWidth(15)
            header_layout.addWidget(self.arrow_label)
        else:
            # Add empty space where arrow would be
            arrow_spacer = QWidget()
            arrow_spacer.setFixedWidth(15)
            header_layout.addWidget(arrow_spacer)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: normal;
        """)
        
        # Spacer
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Score display
        score_label = QLabel(f"{score}/{max_score}")
        score_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
        """)
        score_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(score_label)
        
        main_layout.addWidget(self.header)
        
        # Content container (hidden by default, only if has_arrow is True)
        self.content_container = QWidget()
        self.content_container.setVisible(False)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        if has_arrow:
            main_layout.addWidget(self.content_container)
    
    def add_sub_item(self, name, score, row_index=0):
        """Add a sub-item row with alternating background colors"""
        sub_row = QWidget()
        sub_row.setFixedHeight(40)
        
        # Alternate between #FFFFFF and #E0E0E0
        bg_color = "#FFFFFF" if row_index % 2 == 0 else "#E0E0E0"
        sub_row.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
            }}
        """)
        
        sub_layout = QHBoxLayout(sub_row)
        sub_layout.setContentsMargins(50, 0, 15, 0)  # Indent for sub-items
        sub_layout.setSpacing(10)
        
        # Item name
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            color: #333333;
            font-size: 12px;
        """)
        
        sub_layout.addWidget(name_label)
        sub_layout.addStretch()
        
        # Score
        score_label = QLabel(score)
        score_label.setStyleSheet("""
            color: #333333;
            font-size: 12px;
        """)
        score_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        sub_layout.addWidget(score_label)
        
        self.content_layout.addWidget(sub_row)
        self.sub_items.append(sub_row)
    
    def toggle_expand(self, event):
        """Toggle expansion state"""
        if not self.has_arrow:
            return
            
        self.is_expanded = not self.is_expanded
        self.content_container.setVisible(self.is_expanded)
        
        # Update arrow: > when collapsed, ∨ when expanded
        if self.is_expanded:
            self.arrow_label.setText("⌄")

        else:
            self.arrow_label.setText(">")


class StudentGradesView(QWidget):
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
        
        # Load student's data
        self.load_student_grades()
    
    def setup_ui(self):
        self.setMinimumSize(300,300)
        # White background
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        self.setPalette(pal)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Top header with student info and overall grade
        header_row = self._create_header_row()
        main_layout.addWidget(header_row)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #E0E0E0; max-height: 1px;")
        main_layout.addWidget(separator)
        
        # Filter button - narrow width as in Figma
        filter_btn = QPushButton("Overall Laboratory")
        filter_btn.setFixedHeight(35)
        filter_btn.setFixedWidth(150)  # Narrow width
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
                color: #333333;
            }
            QPushButton:hover {
                border-color: #084924;
            }
        """)
        main_layout.addWidget(filter_btn)
        
        # Scroll area for grade rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Container for all grade rows
        self.grades_container = QWidget()
        self.grades_layout = QVBoxLayout(self.grades_container)
        self.grades_layout.setContentsMargins(0, 0, 0, 0)
        self.grades_layout.setSpacing(0)  # NO spacing between rows
        
        scroll.setWidget(self.grades_container)
        main_layout.addWidget(scroll)
    
    def _create_header_row(self):
        """Create header with student name and overall grade"""
        header = QWidget()
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # Avatar icon
        avatar = QLabel("👤")
        avatar.setStyleSheet("""
            QLabel {
                background-color: #E8F5E9;
                border-radius: 20px;
                font-size: 18px;
            }
        """)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Student name
        name_label = QLabel(self.username)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        
        layout.addWidget(avatar)
        layout.addWidget(name_label)
        layout.addStretch()
        
        # Overall grade (right side)
        grade_container = QWidget()
        grade_layout = QVBoxLayout(grade_container)
        grade_layout.setContentsMargins(0, 0, 0, 0)
        grade_layout.setSpacing(0)
        
        self.overall_grade_label = QLabel("95.4%")
        self.overall_grade_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #084924;
            }
        """)
        self.overall_grade_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        grade_subtitle = QLabel("Overall Course Grade")
        grade_subtitle.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666666;
            }
        """)
        grade_subtitle.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        grade_layout.addWidget(self.overall_grade_label)
        grade_layout.addWidget(grade_subtitle)
        
        layout.addWidget(grade_container)
        
        return header
    
    def load_student_grades(self):
        """Load and display student's grades from model"""
        # Load sample data (in production, fetch from Django API)
        self.grade_model.load_sample_data()
        
        student_id = self._get_student_id()
        if not student_id:
            return
        
        # Calculate grades
        calculated = self.grade_controller.calculate_grades_for_student(student_id)
        
        # Update overall grade
        try:
            final_grade = float(calculated['final_grade'])
            self.overall_grade_label.setText(f"{final_grade:.1f}%")
        except (ValueError, TypeError):
            self.overall_grade_label.setText("0.0%")
        
        # Clear existing rows
        while self.grades_layout.count():
            item = self.grades_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add Midterm Grade section (not expandable)
        midterm_avg = float(calculated.get('midterm_avg', 0))
        midterm_row = ExpandableGradeRow(
            "Midterm Grade",
            f"{midterm_avg:.0f}",
            "100",
            f"{midterm_avg:.1f}%",
            "#084924",
            has_arrow=False  # Not expandable
        )
        self.grades_layout.addWidget(midterm_row)
        
        # Add midterm components
        self._add_components_for_term("midterm", student_id)
        
        # Add Final Term Grade section (not expandable)
        finalterm_avg = float(calculated.get('finalterm_avg', 0))
        finalterm_row = ExpandableGradeRow(
            "Final Term Grade",
            f"{finalterm_avg:.0f}",
            "100",
            f"{finalterm_avg:.1f}%",
            "#084924",
            has_arrow=False  # Not expandable
        )
        self.grades_layout.addWidget(finalterm_row)
        
        # Add final term components
        self._add_components_for_term("finalterm", student_id)
        
        # Add stretch to push everything to top
        self.grades_layout.addStretch()
    
    def _add_components_for_term(self, term, student_id):
        """Add component rows for a term"""
        term_key = 'midterm' if term == 'midterm' else 'final'
        
        for comp_name in self.grade_model.get_rubric_components(term_key):
            type_key = self.grade_model.get_component_type_key(comp_name)
            sub_items = self.grade_model.get_component_items_with_scores(type_key)
            
            # Calculate component average
            total_score = 0
            total_max = 0
            count = 0
            
            for item in sub_items:
                item_name = item['name']
                max_score = item['max_score']
                component_key = f"{item_name.lower().replace(' ', '')}_{term}"
                grade_item = self.grade_model.get_grade(student_id, component_key)
                
                if grade_item.value:
                    try:
                        if '/' in grade_item.value:
                            score_parts = grade_item.value.split('/')
                            score = float(score_parts[0])
                            total_score += score
                            total_max += max_score
                            count += 1
                    except (ValueError, IndexError):
                        pass
            
            # Get component percentage from rubric
            comp_percentage = self.grade_model.get_component_percentage(
                comp_name, 
                'midterm' if term == 'midterm' else 'final'
            )
            
            # Calculate display score
            if count > 0:
                display_score = f"{total_score:.0f}"
                display_max = f"{total_max:.0f}"
            else:
                display_score = "0"
                display_max = "0"
            
            # Create component row (#036800) - expandable
            comp_row = ExpandableGradeRow(
                f"{comp_name.title()} ({comp_percentage}%)",
                display_score,
                display_max,
                "",
                "#036800",
                has_arrow=True  # Expandable
            )
            
            # Add sub-items
            row_idx = 0
            for item in sub_items:
                item_name = item['name']
                component_key = f"{item_name.lower().replace(' ', '')}_{term}"
                grade_item = self.grade_model.get_grade(student_id, component_key)
                
                if grade_item.value:
                    comp_row.add_sub_item(item_name, grade_item.value, row_idx)
                else:
                    comp_row.add_sub_item(item_name, "0/0", row_idx)
                
                row_idx += 1
            
            self.grades_layout.addWidget(comp_row)
    
    def _get_student_id(self):
        """Get current student's ID (from model or API)"""
        if self.grade_model.students:
            # In production: filter by self.username
            return self.grade_model.students[0]['id']
        return None
    
    def _get_student_name(self):
        """Get current student's name"""
        student_id = self._get_student_id()
        if student_id:
            for student in self.grade_model.students:
                if student['id'] == student_id:
                    return student['name']
        return "Unknown Student"
    
    def clear(self):
        """Clear the view"""
        while self.grades_layout.count():
            item = self.grades_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# Test runner
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Student Grades View - Figma Design")
    window.setGeometry(100, 100, 500, 800)
    
    # Mock student data
    mock_cls = {
        'id': 'CS101',
        'name': 'Introduction to Computer Science',
        'section': 'A'
    }
    
    widget = StudentGradesView(
        cls=mock_cls,
        username='castro.carlosfidel',
        roles=['student'],
        primary_role='student',
        token='test_token'
    )
    
    window.setCentralWidget(widget)
    window.show()
    
    sys.exit(app.exec())