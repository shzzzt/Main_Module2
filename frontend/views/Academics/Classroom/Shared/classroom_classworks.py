# classroom_classworks.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QDialog, QLineEdit, QTextEdit, QPushButton, QMenu, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QPixmap, QIcon
from widgets.classroom_classworks_content_ui import Ui_ClassroomClassworksContent
from widgets.topic_widget import TopicWidget
import os

class ClassroomClassworks(QWidget):
    post_selected = pyqtSignal(dict)

    def __init__(self, cls, username, roles, primary_role, token, controller, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ClassroomClassworks {
                background-color: white;
            }
            QDialog {
                background-color: white;
            }
        """)
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        self.ui = Ui_ClassroomClassworksContent()
        self.ui.setupUi(self)
        self.cls = cls
        self.controller = controller
        self.controller.set_class(cls["id"])
        self.topic_widgets = []
        self.untitled_frames = []
        
        self.setup_role_based_ui()
        self.setup_filter()
        self.connect_signals()
        self.initialize_layout()
        self.load_posts()

    def initialize_layout(self):
        """Properly initialize the scroll area layout"""
        scroll_widget = self.ui.scrollAreaWidgetContents
        if scroll_widget.layout() is None:
            scroll_widget.setLayout(QVBoxLayout())
        else:
            # Clear existing layout properly
            layout = scroll_widget.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def _load_icon(self, path):
        icon = QIcon()
        full_path = os.path.join("frontend", "assets", "icons", path)
        if os.path.exists(full_path):
            icon.addPixmap(QPixmap(full_path), QIcon.Mode.Normal, QIcon.State.Off)
        else:
            print(f"Icon file not found: {full_path}")
            icon = QIcon.fromTheme("list-add")
        return icon

    def setup_role_based_ui(self):
        if self.primary_role == "student":
            self.ui.createButton.hide()
        else:
            self.ui.createButton.show()
            self.ui.createButton.setIcon(self._load_icon("baseline-add.svg"))
            self.ui.createButton.setIconSize(QSize(19, 19))
            self.ui.createButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            self.ui.createButton.setStyleSheet("""
                QToolButton {
                    background-color: #084924;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 23px;
                    font-weight: 600;
                    font-size: 16px;
                    min-width: 90px;
                    min-height: 30px;
                }
                QToolButton:hover {
                    background-color: #1B5E20;
                }
                QToolButton:pressed {
                    background-color: #0D4E12;
                }
                QToolButton::menu-arrow {
                    image: none;
                    width: 0px;
                }
                QToolButton::menu-button {
                    border: none;
                    background: transparent;
                    width: 0px;
                }
            """)

    def connect_signals(self):
        self.ui.filterComboBox.currentTextChanged.connect(self.filter_posts)
        self.ui.createButton.clicked.connect(self.show_create_menu)

    def setup_filter(self):
        """Setup filter combo box without duplicates"""
        self.ui.filterComboBox.clear()
        self.ui.filterComboBox.addItem("All")
        self.ui.filterComboBox.addItem("Material")
        self.ui.filterComboBox.addItem("Assessment")
        
        # Get unique topics
        topics = self.controller.get_available_topics()
        unique_topics = sorted(list(set(topics)))  # Remove duplicates
        
        for topic in unique_topics:
            if topic:  # Skip empty topics
                self.ui.filterComboBox.addItem(topic)

    def show_create_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 8px 16px;
                font-size: 13px;
                color: black;
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
            }
        """)
        
        material_action = QAction("Material", self)
        assessment_action = QAction("Assessment", self)
        topic_action = QAction("Topic", self)
        
        material_action.triggered.connect(lambda: self.create_item("material"))
        assessment_action.triggered.connect(lambda: self.create_item("assessment"))
        topic_action.triggered.connect(lambda: self.create_item("topic"))
        
        menu.addAction(material_action)
        menu.addAction(assessment_action)
        menu.addAction(topic_action)
        
        button_pos = self.ui.createButton.mapToGlobal(self.ui.createButton.rect().bottomLeft())
        menu.exec(button_pos)

    def create_item(self, item_type):
        if item_type == "topic":
            self.create_topic()
        else:
            self.show_create_dialog(item_type)

    def create_topic(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Topic")
        dialog.setStyleSheet("background-color: white;")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        title_label = QLabel("Title:")
        title_input = QLineEdit()
        layout.addWidget(title_label)
        layout.addWidget(title_input)
        
        type_label = QLabel("Type:")
        type_combo = QComboBox()
        type_combo.addItems(["material", "assessment"])
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        
        button_layout = QVBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(lambda: self.handle_create_topic(title_input.text(), type_combo.currentText(), dialog))
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        dialog.exec()

    def handle_create_topic(self, title, type_, dialog):
        if not title:
            print("Topic title is required")
            return
        
        if self.controller.create_topic(title, type_):
            print("Topic created successfully")
            self.setup_filter()  # Refresh filter options
            self.load_posts()    # Reload posts
            dialog.accept()
        else:
            print("Failed to create topic")

    def show_create_dialog(self, item_type):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Create {item_type.capitalize()}")
        dialog.setStyleSheet("background-color: white;")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        title_label = QLabel("Title:")
        title_input = QLineEdit()
        layout.addWidget(title_label)
        layout.addWidget(title_input)
        
        content_label = QLabel("Content:")
        content_input = QTextEdit()
        layout.addWidget(content_label)
        layout.addWidget(content_input)
        
        topic_label = QLabel("Topic:")
        topic_combo = QComboBox()
        topic_combo.addItem("None")
        for topic in self.controller.get_available_topics():
            if topic:
                topic_combo.addItem(topic)
        layout.addWidget(topic_label)
        layout.addWidget(topic_combo)
        
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(lambda: self.handle_create_content(
            title_input.text(),
            content_input.toPlainText(),
            item_type,
            topic_combo.currentText() if topic_combo.currentText() != "None" else None,
            dialog
        ))
        layout.addWidget(create_btn)
        
        dialog.exec()

    def handle_create_content(self, title, content, type_, topic_name, dialog):
        if not title or not content:
            print("Title and content are required")
            return
        
        if self.controller.create_post(title, content, type_, topic_name):
            print(f"{type_.capitalize()} created successfully")
            self.load_posts(self.ui.filterComboBox.currentText())
            dialog.accept()
        else:
            print(f"Failed to create {type_}")

    def load_posts(self, filter_topic=None):
        """Load posts using refactored MVC pattern."""
        # Determine filter parameters
        filter_type = None
        topic_name = None
        if filter_topic == "Material":
            filter_type = "material"
        elif filter_topic == "Assessment":
            filter_type = "assessment"
        elif filter_topic not in ["All", "Material", "Assessment"]:
            topic_name = filter_topic
        
        # Use refactored controller method
        self.controller.set_filter(filter_type=filter_type, topic_name=topic_name)
        posts = self.controller.get_classwork_items()
        
        # Sort posts: latest first (assuming posts have a timestamp field like 'created_at')
        try:
            posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        except:
            # If sorting fails, keep the original order (assuming it's already newest first)
            pass
        
        # Get the layout
        scroll_widget = self.ui.scrollAreaWidgetContents
        layout = scroll_widget.layout()
        
        # Clear previous content
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear references
        self.topic_widgets.clear()
        self.untitled_frames.clear()
        
        # Add posts to layout
        if posts:
            grouped = {}
            for post in posts:
                topic_title = post.get("topic", "Untitled")
                grouped.setdefault(topic_title, []).append(post)
            
            # Sort posts within each group by date (latest first)
            for topic_title in grouped:
                grouped[topic_title].sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Put Untitled group first, then alphabetical order for others
            sorted_groups = sorted(grouped.items(), 
                                key=lambda x: (x[0] != "Untitled", x[0] if x[0] != "Untitled" else ""))
            
            for topic_title, topic_posts in sorted_groups:
                if topic_title == "Untitled":
                    # Add untitled posts directly without TopicWidget container
                    for post in topic_posts:
                        from frontend.widgets.topic_frame import TopicFrame
                        frame = TopicFrame(post, self.controller, self.primary_role)
                        frame.post_clicked.connect(self.post_selected.emit)
                        layout.addWidget(frame)
                        self.untitled_frames.append(frame)
                else:
                    # Use TopicWidget for posts with topics
                    topic_widget = TopicWidget(topic_title, topic_posts, self.controller, self.primary_role)
                    
                    # Connect post selection signal
                    for frame in topic_widget.frames:
                        frame.post_clicked.connect(self.post_selected.emit)
                    
                    layout.addWidget(topic_widget)
                    self.topic_widgets.append(topic_widget)
        
        layout.addStretch()

    def filter_posts(self, filter_text):
        """Filter posts based on selection"""
        if not filter_text:
            return
        
        # Show all first
        for topic_widget in self.topic_widgets:
            topic_widget.setVisible(True)
            for frame in topic_widget.frames:
                frame.setVisible(True)
        
        for frame in self.untitled_frames:
            frame.setVisible(True)
        
        # Apply filters
        if filter_text == "All":
            return  # Already visible
        
        elif filter_text == "Material":
            for frame in self.untitled_frames:
                frame.setVisible(frame.post["type"] == "material")
            
            for widget in self.topic_widgets:
                has_materials = any(f.post["type"] == "material" for f in widget.frames)
                widget.setVisible(has_materials)
                if widget.isVisible():
                    for frame in widget.frames:
                        frame.setVisible(frame.post["type"] == "material")
        
        elif filter_text == "Assessment":
            for frame in self.untitled_frames:
                frame.setVisible(frame.post["type"] == "assessment")
            
            for widget in self.topic_widgets:
                has_assessments = any(f.post["type"] == "assessment" for f in widget.frames)
                widget.setVisible(has_assessments)
                if widget.isVisible():
                    for frame in widget.frames:
                        frame.setVisible(frame.post["type"] == "assessment")
        
        else:  # Topic filter
            # Hide all untitled frames when filtering by topic
            for frame in self.untitled_frames:
                frame.setVisible(False)
            
            for widget in self.topic_widgets:
                widget.setVisible(widget.title_label.text() == filter_text)
                if widget.isVisible():
                    for frame in widget.frames:
                        frame.setVisible(True)

    def clear(self):
        """Clean up method"""
        self.ui.filterComboBox.clear()
        layout = self.ui.scrollAreaWidgetContents.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()