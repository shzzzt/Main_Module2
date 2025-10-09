# ClassroomView.py - FIXED
from PyQt6.QtWidgets import QWidget, QPushButton, QTabWidget, QVBoxLayout, QHBoxLayout, QButtonGroup, QMainWindow, QStackedWidget, QApplication, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from frontend.views.Academics.Classroom.Shared.post_details import PostDetails
from frontend.views.Academics.Classroom.Shared.classroom_stream import ClassroomStream
from frontend.views.Academics.Classroom.Shared.classroom_classworks import ClassroomClassworks
from frontend.views.Academics.Classroom.Faculty.classroom_grades_view import FacultyGradesView
from frontend.views.Academics.Classroom.Student.classroom_grades_view import StudentGradesView
from frontend.services.post_service import PostService
from frontend.services.topic_service import TopicService
from frontend.controller.post_controller import PostController

class ClassroomView(QWidget):
    back_clicked = pyqtSignal()
    post_selected = pyqtSignal(dict) #emits post data
    navigate_to_form = pyqtSignal(str, object)  # ADD: pass through signal

    def __init__(self, cls, username, roles, primary_role, token, parent=None):
        super().__init__(parent)
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        self.cls = cls
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        lecture_btn = QPushButton("LECTURE")
        lecture_btn.setStyleSheet("""
            QPushButton { background-color: #084924; color: white; border-radius: 5px; padding: 5px 10px; }
            QPushButton:checked { background-color: #1B5E20; }
        """)
        lecture_btn.setCheckable(True)
        lecture_btn.setChecked(True)
        lab_btn = QPushButton("LABORATORY")
        lab_btn.setStyleSheet("""
            QPushButton { background-color: #084924; color: white; border-radius: 5px; padding: 5px 10px; }
            QPushButton:checked { background-color: #1B5E20; }
        """)
        lab_btn.setCheckable(True)
        group = QButtonGroup()
        group.addButton(lecture_btn)
        group.addButton(lab_btn)
        header_layout.addWidget(lecture_btn)
        header_layout.addWidget(lab_btn)
        layout.addLayout(header_layout)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: white; }
            QTabBar::tab {
                background: white;
                padding: 10px 20px;
                font-size: 14px;
                font-family: "Poppins", Arial, sans-serif;
                text-transform: uppercase;
                border: none;
            }
            QTabBar::tab:selected {
                border-bottom: 4px solid #FFD700;
                color: black;
            }
        """)
        
        # Create services and controller
        post_service = PostService("data/classroom_data.json")
        topic_service = TopicService("data/classroom_data.json")
        
        # Create post controller with both services
        post_controller = PostController(
            post_service=post_service,
            topic_service=topic_service
        )
        post_controller.set_class(self.cls["id"])
        
        self.stream_view = ClassroomStream(
            self.cls, self.username, self.roles, self.primary_role, 
            self.token, post_controller
        )
        self.classworks_view = ClassroomClassworks(
            self.cls, self.username, self.roles, self.primary_role, 
            self.token, post_controller  # Pass the same controller
        )
        
        # Connect signals
        self.stream_view.post_selected.connect(self.post_selected)
        self.classworks_view.post_selected.connect(self.post_selected)
        
        # Connect refresh signals
        self.classworks_view.post_created.connect(self.stream_view.refresh_posts)
        self.stream_view.post_created.connect(self.classworks_view.refresh_posts)
        
        # Create views for other tabs
        students_view = QWidget()
        attendance_view = QWidget()
        
        # Create grades view - Faculty gets FacultyGradesView, others get placeholder
        if self.primary_role == "faculty":
            try:
                self.grades_view = FacultyGradesView(
                    self.cls, self.username, self.roles, self.primary_role, self.token
                )
            except ImportError as e:
                # Fallback if FacultyGradesView is not available
                print(f"FacultyGradesView not available: {e}, using placeholder")
                self.grades_view = QWidget()
                self.grades_view.setStyleSheet("background-color: white;")
                student_layout = QVBoxLayout(self.grades_view)
                student_label = QLabel("Faculty Grades View - Not Available")
                student_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                student_label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
                student_layout.addWidget(student_label)
        else:
            try:
                self.grades_view = StudentGradesView(
                    self.cls, self.username, self.roles, self.primary_role, self.token
                )
            except ImportError as e:
                # Fallback if FacultyGradesView is not available
                print(f"FacultyGradesView not available: {e}, using placeholder")
                self.grades_view = QWidget()
                self.grades_view.setStyleSheet("background-color: white;")
                student_layout = QVBoxLayout(self.grades_view)
                student_label = QLabel("Student Grades View - Not Available")
                student_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                student_label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
                student_layout.addWidget(student_label)
            
        tabs.addTab(self.stream_view, "STREAM")
        tabs.addTab(self.classworks_view, "CLASSWORKS")
        tabs.addTab(students_view, "STUDENTS")
        tabs.addTab(attendance_view, "ATTENDANCE")
        tabs.addTab(self.grades_view, "GRADES")
        
        # FIX: Connect the signals properly - remove .emit from the connection
        self.stream_view.post_selected.connect(self.post_selected)
        self.classworks_view.post_selected.connect(self.post_selected)
        
        layout.addWidget(tabs)

        # FIXED: Connect form navigation to pass through to ClassroomMain
        self.classworks_view.navigate_to_form.connect(self.navigate_to_form.emit)

        # # Select dashboard based on primary_role
        # if primary_role == "student":
        #     dashboard_widget = StudentDashboard(username, roles, primary_role, token)
        # elif primary_role == "staff":
        #     dashboard_widget = StaffDashboard(username, roles, primary_role, token)
        # elif primary_role == "faculty":
        #     dashboard_widget = FacultyDashboard(username, roles, primary_role, token)
        # elif primary_role == "admin":
        #     dashboard_widget = AdminDashboard(username, roles, primary_role, token)
        # else:
        #     # Fallback for unrecognized roles
        #     layout = self._create_default_widget(
        #         "Invalid Role", f"No dashboard available for role: {primary_role}"
        #         )

    # REMOVE: Delete these methods - ClassroomMain handles form navigation
    # def handle_form_navigation(self, form_widget):
    #     """Handle navigation to material/assessment forms using stacked widget"""
    #     print(f"Navigating to form in stacked widget")
    #     
    #     # Store reference to current form
    #     self.current_form = form_widget
    #     
    #     # Connect the form's back signal to return to classworks
    #     form_widget.back_clicked.connect(self.return_to_classworks)
    #     
    #     # Add to stacked widget and show
    #     self.stacked_widget.addWidget(form_widget)
    #     self.stacked_widget.setCurrentWidget(form_widget)
    #
    # def return_to_classworks(self):
    #     """Return from form back to classworks view"""
    #     print("Returning to classworks from form")
    #     if hasattr(self, 'current_form') and self.current_form:
    #         self.stacked_widget.removeWidget(self.current_form)
    #         self.current_form.deleteLater()
    #         self.current_form = None
    #     # The classworks view should already be in the stacked widget

    def clear(self):
        self.stream_view.clear()
        self.classworks_view.clear()
            
    # def _create_default_widget(self, title, desc):
    #     """Create a fallback widget for invalid roles."""
    #     widget = QWidget()
    #     layout = QVBoxLayout()
    #     title_label = QLabel(title)
    #     title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    #     desc_label = QLabel(desc)
    #     desc_label.setFont(QFont("Arial", 12))
    #     layout.addWidget(title_label)
    #     layout.addWidget(desc_label)
    #     layout.addStretch()
    #     widget.setLayout(layout)
    #     return widget