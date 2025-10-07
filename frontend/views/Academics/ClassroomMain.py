from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect, QPushButton, QApplication, QHBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import sys
import os

# Relative imports from Academics to Classroom/Shared
try:
    # Try relative imports first (works when run directly)
    from .Classroom.Shared.classroom_home import ClassroomHome
    from .Classroom.Shared.post_details import PostDetails
    from .ClassroomView import ClassroomView
    from ...controller.classroom_controller import ClassroomController

except ImportError:
    try:
        # Fallback: import from current directory structure
        from Classroom.Shared.classroom_home import ClassroomHome
        from Classroom.Shared.post_details import PostDetails
        from ClassroomView import ClassroomView
        from controller.classroom_controller import ClassroomController

    except ImportError:
        # Final fallback: import using full path
        from views.Academics.Classroom.Shared.classroom_home import ClassroomHome
        from views.Academics.Classroom.Shared.post_details import PostDetails
        from views.Academics.ClassroomView import ClassroomView


class ClassroomMain(QWidget):
    def __init__(self, username, roles, primary_role, token, parent=None):
        super().__init__(parent)
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        self.setMinimumSize(940, 530)
        self.setStyleSheet("background-color: white;")
        
        # Main layout - vertical for header + sidebar-content area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header (spans full width)
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: white; 
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        header_title = QLabel("CLASSROOM")
        header_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        header_title.setStyleSheet("color: #1e5631;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        main_layout.addWidget(header)
        
        # Content area (sidebar + main content)
        content_area = QWidget()
        content_area_layout = QHBoxLayout(content_area)
        content_area_layout.setContentsMargins(0, 0, 0, 0)
        content_area_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(120)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #white;
                border-right: 1px solid #d0d0d0;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Sidebar buttons
        home_button = QPushButton("Home")
        home_button.setFixedHeight(50)
        home_button.setStyleSheet("""
            QPushButton {
                color: black;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        home_button.clicked.connect(self.show_home)
        sidebar_layout.addWidget(home_button)
        
        classes_button = QPushButton("Classes")
        classes_button.setFixedHeight(50)
        classes_button.setStyleSheet("""
            QPushButton {
                color: black;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        # You can connect this to show a classes overview if needed
        # classes_button.clicked.connect(self.show_classes_overview)
        sidebar_layout.addWidget(classes_button)
        
        sidebar_layout.addStretch()
        
        # Main content area
        shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=3, color=QColor(0, 0, 0, 40))
        content_widget = QWidget()
        content_widget.setGraphicsEffect(shadow)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Stacked widget for dynamic content
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: white;")
        
        # Initialize views
        self.classroom_controller = ClassroomController()
        self.home_view = ClassroomHome(username, roles, primary_role, token)
        self.current_classroom_view = None
        self.current_post_view = None
        self.current_form_view = None  # ADD: track current form
        
        # Add home view as default
        self.stacked_widget.addWidget(self.home_view)
        self.home_view.class_selected.connect(self.show_classroom)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Add sidebar and content to content area
        content_area_layout.addWidget(sidebar)
        content_area_layout.addWidget(content_widget)
        
        # Add content area to main layout
        main_layout.addWidget(content_area)
        
        # Set initial view to home
        self.stacked_widget.setCurrentWidget(self.home_view)
    
    def show_classroom(self, cls):
        print(f"Showing classroom: {cls['title']}")
        
        if self.current_classroom_view:
            self.stacked_widget.removeWidget(self.current_classroom_view)
            self.current_classroom_view.deleteLater()
        
        self.current_classroom_view = ClassroomView(cls, self.username, self.roles, self.primary_role, self.token)
        self.current_classroom_view.back_clicked.connect(self.show_home)
        self.current_classroom_view.post_selected.connect(self.show_post)
        self.current_classroom_view.navigate_to_form.connect(self.show_form)
        self.stacked_widget.addWidget(self.current_classroom_view)
        self.stacked_widget.setCurrentWidget(self.current_classroom_view)

    def show_form(self, form_type, cls):
        """NEW: Show material or assessment form"""
        print(f"Showing {form_type} form for class: {cls['title']}")
        
        # Clean up any existing form
        if self.current_form_view:
            self.stacked_widget.removeWidget(self.current_form_view)
            self.current_form_view.deleteLater()
        
        # Create the appropriate form
        if form_type == "material":
            from frontend.views.Academics.Classroom.Faculty.upload_materials import MaterialForm
            self.current_form_view = MaterialForm(
                cls=cls,
                username=self.username,
                roles=self.roles,
                primary_role=self.primary_role,
                token=self.token,
                post_controller=self.current_classroom_view.classworks_view.post_controller if self.current_classroom_view else None
            )
        elif form_type == "assessment":
            from frontend.views.Academics.Classroom.Faculty.create_assessment import AssessmentForm
            self.current_form_view = AssessmentForm(
                cls=cls,
                username=self.username,
                roles=self.roles,
                primary_role=self.primary_role,
                token=self.token,
                post_controller=self.current_classroom_view.classworks_view.post_controller if self.current_classroom_view else None
            )
        else:
            print(f"Unknown form type: {form_type}")
            return
        
        # Connect back signal
        self.current_form_view.back_clicked.connect(self.return_to_classroom_from_form)
        
        # Add to stacked widget and show
        self.stacked_widget.addWidget(self.current_form_view)
        self.stacked_widget.setCurrentWidget(self.current_form_view)

    def return_to_classroom_from_form(self):
        """NEW: Return from form back to classroom view"""
        print("Returning to classroom from form")
        if self.current_form_view:
            self.stacked_widget.removeWidget(self.current_form_view)
            self.current_form_view.deleteLater()
            self.current_form_view = None
        
        # Return to the classroom view
        if self.current_classroom_view:
            self.stacked_widget.setCurrentWidget(self.current_classroom_view)
    
    def show_post(self, post):
        print(f"Showing post: {post['title']}")
        
        if self.current_post_view:
            self.stacked_widget.removeWidget(self.current_post_view)
            self.current_post_view.deleteLater()
        
        self.current_post_view = PostDetails(post)
        self.current_post_view.back_clicked.connect(self.return_to_classroom)
        self.stacked_widget.addWidget(self.current_post_view)
        self.stacked_widget.setCurrentWidget(self.current_post_view)
    
    def return_to_classroom(self):
        print("Returning to classroom")
        if self.current_post_view:
            self.stacked_widget.removeWidget(self.current_post_view)
            self.current_post_view.deleteLater()
            self.current_post_view = None
        self.stacked_widget.setCurrentWidget(self.current_classroom_view)
    
    def show_home(self):
        print("Showing home")
        if self.current_classroom_view:
            self.stacked_widget.removeWidget(self.current_classroom_view)
            self.current_classroom_view.deleteLater()
            self.current_classroom_view = None
        self.stacked_widget.setCurrentWidget(self.home_view)
        

def main():
    app = QApplication(sys.argv)
    window = ClassroomMain()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()