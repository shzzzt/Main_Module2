# views/section_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHBoxLayout

class SectionView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sections")
        self.resize(800, 400)

        self.table = QTableView()
        self.add_button = QPushButton("+ Add Section")
        
        # Debug print to verify button click
        self.add_button.clicked.connect(lambda: print("Button clicked from view!"))

        layout = QVBoxLayout()
        layout.addWidget(self.add_button)
        layout.addWidget(self.table)
        self.setLayout(layout)
