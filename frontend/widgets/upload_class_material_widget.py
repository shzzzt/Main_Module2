from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from frontend.widgets.labeled_section import LabeledSection

class UploadClassMaterialPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initializeUI()

    def initializeUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #084924;
            }
        """)

        self.__layout = QVBoxLayout(self)
        self.__layout.setSpacing(20)  # Responsive spacing
        self.__layout.setContentsMargins(30, 25, 30, 25)

        self.setup_widgets(self.__layout)

    def setup_widgets(self, layout):
        title_input = QLineEdit()
        title_input.setPlaceholderText("Enter title")
        title_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;  /* Increased padding */
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;  /* Minimum height */
            }
            QLineEdit:focus {
                border-color: #0066cc;
                border-width: 2px;
            }
        """)

        title_section = LabeledSection(label="Title", widget=title_input, sub_label="*Required")

        # Instructions field
        instructions_input = QTextEdit()
        instructions_input.setStyleSheet("""
            QTextEdit {
                padding: 15px;  /* Increased padding */
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #0066cc;
                border-width: 2px;
            }
        """)
        instructions_input.setMinimumHeight(100)
        instructions_input.setMaximumHeight(120)  # Limit max height for responsive behavior
        
        instructions_section = LabeledSection(label="Instructions (Optional)", widget=instructions_input)

        layout.addWidget(title_section)
        layout.addWidget(instructions_section)

        self.upload_file_section(layout)
        
    def upload_file_section(self, layout):
        upload_layout = QVBoxLayout()
        upload_layout.setSpacing(15)
        
        upload_label = QLabel("Upload File")
        upload_label.setStyleSheet("""
            QLabel {
                font-size: 16px;  /* Increased font size */
                font-weight: 500;
                color: #333;
                border: none;
            }
        """)
        
        # Upload area
        upload_frame = QFrame()
        upload_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #fafafa;
            }
        """)
        upload_frame.setMinimumHeight(140)  # Reduced minimum height for better fit
        upload_frame.setMaximumHeight(160)  # Responsive maximum height
        
        upload_content_layout = QVBoxLayout(upload_frame)
        upload_content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_content_layout.setSpacing(10)
        
        # File icon (using text as placeholder)
        file_icon = QLabel("📄")
        file_icon.setStyleSheet("""
            QLabel {
                font-size: 32px;
                border: none;
                color: #28a745;
            }
        """)
        file_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        drag_label = QLabel("Drag n Drop here")
        drag_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                border: none;
            }
        """)
        drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        or_label = QLabel("Or")
        or_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                border: none;
            }
        """)
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("""
            QPushButton {
                color: #0066cc;
                background: none;
                border: none;
                font-size: 14px;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #0052a3;
            }
        """)
        
        upload_content_layout.addWidget(file_icon)
        upload_content_layout.addWidget(drag_label)
        upload_content_layout.addWidget(or_label)
        upload_content_layout.addWidget(browse_btn)

        upload_layout.addWidget(upload_frame)

        layout.addWidget(upload_layout)
        self.setup_upload_button(upload_layout)

    def setup_upload_button(self, upload_layout):
        upload_now_btn = QPushButton("Upload Now")
        upload_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;  /* Green color to match image */
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px 24px;  /* Increased padding */
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        upload_now_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    