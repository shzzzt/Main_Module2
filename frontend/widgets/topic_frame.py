from PyQt6.QtWidgets import QFrame, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt

from .item_widget import ItemWidget

class TopicFrame(QFrame):
    post_clicked = pyqtSignal(dict)

    def __init__(self, post, controller, user_role, parent=None):
        super().__init__(parent)
        self.post = post
        self.controller = controller
        self.user_role = user_role
        self.setObjectName(f"topicItemFrame_{id(self)}")
        self.setMinimumSize(800, 70)
        self.setMaximumHeight(70)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #084924;
                border-radius: 20px;
                margin-left: 20px;
            }
            QFrame:hover {
                background-color: #F8F9FA;
                border-color: #D0D7DE;
            }
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Remove spacing
        item_widget = ItemWidget(self.post, self.controller, self.user_role)
        layout.addWidget(item_widget)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.post_clicked.emit(self.post)
        super().mousePressEvent(event)