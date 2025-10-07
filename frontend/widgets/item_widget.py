from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

# In item_widget.py - modify only the title_text line
class ItemWidget(QWidget):
    def __init__(self, post, controller, user_role, parent=None):
        super().__init__(parent)
        self.post = post
        self.controller = controller
        self.user_role = user_role
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setSpacing(8)  # Reduced spacing to save horizontal space
        layout.setContentsMargins(10, 8, 10, 8)

       # Icon Label (placeholder green circle)
        icon_label = QLabel(self)
        icon_label.setMinimumSize(32, 32)
        icon_label.setMaximumSize(32, 32)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #084924;
                border-radius: 16px;  /* Changed from 19px to 16px (half of minimum size) */
                border: 2px solid white;
                margin: 0px;
                padding: 0px;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        # Title Label - CHANGED: Only show title, no "User posted..." text
        title_text = self.post.get("title", "")  # Simplified to just the title
        title_label = QLabel(title_text, self)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 400;
                color: #24292f;
                border: none;
                background: transparent;
                margin-left: 5px;           /* Added margin for consistency */
                padding: 2px;          /* Added padding for text */
            }
        """)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)

        # Date Label
        date_text = self.post.get("date", "").split(" ")[0]  # e.g., "2025-08-18"
        date_label = QLabel(date_text, self)
        date_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #656d76;
                border: none;
                background: transparent;
                margin: 5px;           /* Added margin for consistency */
                padding: 2px;          /* Added padding for text */
            }
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(date_label)

        # Menu Button (for faculty/admin)
        if self.user_role in ["faculty", "admin"]:
            self.menu_button = QPushButton("⋮", self)
            self.menu_button.setMinimumSize(24, 24)
            self.menu_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    font-size: 34px;
                    color: #656d76;
                    border-radius: 12px;
                    margin: 5px;       /* Added margin for consistency */
                    padding: 0px;      /* No padding needed for the dots */
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            layout.addWidget(self.menu_button)
            self.menu_button.clicked.connect(self.show_menu)

    def show_menu(self):
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
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
            }
        """)
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)
        edit_action.triggered.connect(lambda: self.controller.edit_post(self.post))
        delete_action.triggered.connect(lambda: self.controller.delete_post(self.post))
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        button_pos = self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        menu.exec(button_pos)

    def show_menu(self):
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
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
            }
        """)
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)
        edit_action.triggered.connect(lambda: self.controller.edit_post(self.post))
        delete_action.triggered.connect(lambda: self.controller.delete_post(self.post))
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        button_pos = self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        menu.exec(button_pos)