# upload_materials.py - UPDATED WITH RESPONSIVE LAYOUT
import sys
import os

project_root = (os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QTextEdit, 
    QComboBox, 
    QPushButton, 
    QFrame, 
    QSpacerItem, 
    QSizePolicy, 
    QGridLayout,
    QScrollArea  # ADD: Scroll area for responsiveness
)

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QCursor
from frontend.widgets.labeled_section import LabeledSection
from frontend.widgets.dropdown import DropdownMenu
from frontend.widgets.upload_class_material_widget import UploadClassMaterialPanel
from frontend.controller.Academics.class_material_controller import ClassMaterialController

class MaterialForm(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, cls=None, username=None, roles=None, primary_role=None, token=None, post_controller=None, parent=None):
        super().__init__(parent)
        self.cls = cls
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        self.post_controller = post_controller
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea {\n"
"       border: none;\n"
"       background-color: transparent;\n"
"   }\n"
"   QScrollBar:vertical {\n"
"       border: none;\n"
"       background: #F1F1F1;\n"
"       width: 8px;\n"
"       border-radius: 4px;\n"
"   }\n"
"   QScrollBar::handle:vertical {\n"
"       background: #C1C1C1;\n"
"       border-radius: 4px;\n"
"       min-height: 20px;\n"
"   }")
        
        # Main content widget
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        header = self.create_header()
        body = self.create_body()
        
        content_layout.addWidget(header)
        content_layout.addWidget(body, 1)  # Give body stretch factor
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_header(self):
        frame = QFrame()
        header_layout = QHBoxLayout(frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        back_button = QPushButton("<")
        back_button.setFixedSize(40, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                font-size: 20px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
            }               
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_button.clicked.connect(self.back_clicked)

        back_label = QLabel("Material")
        back_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                border: none;
                margin-left: 15px;
            }
        """)

        header_layout.addWidget(back_button)
        header_layout.addWidget(back_label)
        header_layout.addStretch()

        return frame
    
    def create_body(self):
        """Create responsive body with left and right panels"""
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setSpacing(20)
        body_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel (main content) - responsive
        left_panel = self.create_left_panel()
        left_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Right panel (sidebar) - fixed minimum width but can grow
        right_panel = self.create_right_panel()
        right_panel.setMinimumWidth(280)  # Minimum width for sidebar
        right_panel.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        
        body_layout.addWidget(left_panel, 3)  # Left panel gets more space
        body_layout.addWidget(right_panel, 1)  # Right panel gets less space
        
        return body_widget
    
    def create_left_panel(self):
        """Create responsive left panel"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the existing UploadClassMaterialPanel but make it responsive
        upload_panel = UploadClassMaterialPanel()
        upload_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        left_layout.addWidget(upload_panel)
        return left_widget
    
    def create_right_panel(self):
        right_frame = QFrame()
        right_frame.setMinimumWidth(280)
        right_frame.setMaximumWidth(400)  # Prevent it from getting too wide
        right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #084924;
            } 
            LabeledSection {
                border: none;                      
            }
        """)
        
        layout = QVBoxLayout(right_frame)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 25, 20, 25)

        # Category dropdown
        audience_dropdown = DropdownMenu(items=["ITSD81"])
        layout.addWidget(LabeledSection("For", audience_dropdown))

        # Assigned Students Dropdown
        assigned_dropdown = DropdownMenu(items=["All Students"])
        layout.addWidget(LabeledSection("Assigned", assigned_dropdown))

        # Topic Dropdown 
        topic_dropdown = DropdownMenu(items=["Topic 1"])
        layout.addWidget(LabeledSection("Topic", topic_dropdown))

        layout.addStretch()
        return right_frame
    
def main():
    app = QApplication(sys.argv)
    window = MaterialForm()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()