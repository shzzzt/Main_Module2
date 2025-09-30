#Material upload interface

#Assessment creation interface

import sys
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
    QSizePolicy, QGridLayout)

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QCursor
from frontend.widgets.labeled_section import LabeledSection
from frontend.widgets.dropdown import DropdownMenu
from frontend.widgets.upload_class_material_widget import UploadClassMaterialPanel


class MaterialForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Upload Material")
        self.setGeometry(100, 100, 1400, 800)  # Increased window size
        self.setMinimumSize(QSize(1200, 700))   # Set minimum size
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        
        header = self.create_header()
        # Left panel
        left_panel = self.create_left_panel()
        
        # Right panel
        right_panel = self.create_right_panel()

        self.upload_button = self.create_upload_button()
        
        body = QFrame()
        body_layout = QHBoxLayout(body)
        body_layout.addWidget(left_panel, 3)  # Give left panel more space ratio
        body_layout.addWidget(right_panel, 1)

        main_layout.addWidget(header)
        main_layout.addWidget(body)
        # main_layout.addWidget(self.upload_button)

    def create_header(self):
        frame = QFrame()
        header_layout = QHBoxLayout(frame)

        back_button = QPushButton("<")
        back_button.setFixedSize(40, 40)  # Fixed size for back button
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

        back_label = QLabel("Material")
        back_label.setStyleSheet("""
            QLabel {
                font-size: 24px;  /* Increased font size */
                font-weight: bold;
                color: #333;
                border: none;
                margin-left: 15px;
            }
        """)

        header_layout.addWidget(back_button)
        header_layout.addWidget(back_label)

        return frame

    def create_left_panel(self):
        return UploadClassMaterialPanel()
    
    def create_right_panel(self):
        right_frame = QFrame()
        right_frame.setMinimumWidth(300)
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
    
    def create_upload_button(self):
        # Upload button
        upload_btn = QPushButton("Upload Now")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px 24px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
        """)
        upload_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return upload_btn
    
def main():
    app = QApplication(sys.argv)
    window = MaterialForm()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()