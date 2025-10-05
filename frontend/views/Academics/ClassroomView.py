from PyQt6.QtWidgets import QWidget, QPushButton, QTabWidget, QVBoxLayout, QHBoxLayout,QButtonGroup,QMainWindow, QStackedWidget, QApplication
from PyQt6.QtCore import pyqtSignal
from frontend.views.Academics.Classroom.Shared.post_details import PostDetails
from frontend.views.Academics.Classroom.Shared.classroom_stream import ClassroomStream
from frontend.views.Academics.Classroom.Shared.classroom_classworks import ClassroomClassworks
from frontend.services.classroom_service import ClassroomService
from frontend.services.stream_service import StreamService
from frontend.services.classwork_service import ClassworkService
from frontend.controller.classroom_controller import ClassroomController
from frontend.controller.stream_controller import StreamController
from frontend.controller.classwork_controller import ClassworkController

class ClassroomView(QWidget):
    back_clicked = pyqtSignal()
    post_selected = pyqtSignal(dict) #emits post data

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
        
        stream_service = StreamService("data/classroom_data.json")
        classwork_service = ClassworkService("data/classroom_data.json")
        stream_controller = StreamController(stream_service)
        classwork_controller = ClassworkController(classwork_service)
        
        self.stream_view = ClassroomStream(self.cls, self.username, self.roles, self.primary_role, self.token, stream_controller)
        self.classworks_view = ClassroomClassworks(self.cls, self.username, self.roles, self.primary_role, self.token, classwork_controller)
        students_view = QWidget()
        attendance_view = QWidget()
        grades_view = QWidget()
        
        tabs.addTab(self.stream_view, "STREAM")
        tabs.addTab(self.classworks_view, "CLASSWORKS")
        tabs.addTab(students_view, "STUDENTS")
        tabs.addTab(attendance_view, "ATTENDANCE")
        tabs.addTab(grades_view, "GRADES")
        
        # FIX: Connect the signals properly - remove .emit from the connection
        self.stream_view.post_selected.connect(self.post_selected)
        self.classworks_view.post_selected.connect(self.post_selected)
        
        layout.addWidget(tabs)


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