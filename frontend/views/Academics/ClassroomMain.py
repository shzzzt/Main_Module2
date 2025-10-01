from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QApplication, QHBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
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
        
        # Main layout - horizontal for sidebar + content
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(90)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: ##F1F1F3;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Home button in sidebar
        home_button = QPushButton("Home")
        home_button.setFixedHeight(50)
        home_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                text-align: left;
                padding-left: 14px;
                font-size: 14px;
                
            }
            QPushButton:hover {
                background-color: #2d6a3f;
            }
        """)
        home_button.clicked.connect(self.show_home)
        sidebar_layout.addWidget(home_button)
        
        # Add some spacing and other potential sidebar items
        sidebar_layout.addStretch()
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header (without Home button now)
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #d0d0d0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        header_title = QLabel("CLASSROOM")
        header_title.setFont(QFont("Poppins", 14, QFont.Weight.DemiBold))
        header_title.setStyleSheet("color: #1e5631;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        content_layout.addWidget(header)
        
        # Stacked widget for dynamic content
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: white")
        
        # Initialize views
        self.classroom_controller = ClassroomController()
        self.home_view = ClassroomHome(username, roles, primary_role, token)
        self.current_classroom_view = None
        self.current_post_view = None
        
        # Add home view as default
        self.stacked_widget.addWidget(self.home_view)
        self.home_view.class_selected.connect(self.show_classroom)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_widget)
        
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
        self.stacked_widget.addWidget(self.current_classroom_view)
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