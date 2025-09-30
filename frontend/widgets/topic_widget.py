from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, Qt

from .topic_frame import TopicFrame

class TopicWidget(QWidget):
    # Define the signal that will be emitted when a post is clicked
    post_selected = pyqtSignal(dict)
    
    def __init__(self, topic_title, posts, controller, user_role, parent=None):
        super().__init__(parent)
        print(f"TopicWidget init: title='{topic_title}', posts count={len(posts)}")
        self.topic_title = topic_title if topic_title is not None else "Untitled"
        self.posts = posts
        self.controller = controller
        self.user_role = user_role
        self.frames = []  # Store frames for potential future filtering
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Only show title if it's not empty (for untitled posts)
        if self.topic_title:
            # Topic Title
            self.title_label = QLabel(self.topic_title, self)
            self.title_label.setStyleSheet("""
                QLabel {
                    font-size: 40px;
                    font-weight: 400;
                    margin-left: 20px;
                    margin-top: 20px;
                    margin-bottom: -10px;
                }
            """)
            layout.addWidget(self.title_label)

            # Separator
            separator = QFrame(self)
            separator.setMinimumSize(800, 1)
            separator.setMaximumHeight(1)
            separator.setStyleSheet("""
                QFrame {
                    border: 1px solid #A9A9A9;
                    background-color: transparent;
                    margin-left: 20px;
                }
            """)
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(separator)

        # Add TopicFrame for each post
        for post in self.posts:
            topic_frame = TopicFrame(post, self.controller, self.user_role)
            # Connect the frame's signal to this widget's signal
            topic_frame.post_clicked.connect(self.post_selected.emit)
            self.frames.append(topic_frame)
            layout.addWidget(topic_frame)

    # Remove the post_clicked method since we're connecting directly now