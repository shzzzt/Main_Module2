from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QMainWindow, QLabel, QPushButton, QTableWidget,QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPalette, QFont
import sys
from modal_create_section import Create_Section_Dialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sections Management")
        self.setAutoFillBackground(True)
        self.setFixedSize(QSize(900,600))
        
        # Main container for the window
        container = QWidget()
        container.setAutoFillBackground(True)
        pal = container.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("white"))
        container.setPalette(pal)
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # horizontal layout that will hold and section label and plus button
        header_layout = QHBoxLayout()
        
        # sections header label
        title_label = QLabel("Sections")
        title_font = QFont("Poppins", 34)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #000000;")
        
        # spacer_item to push button to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # plus button
        plus_button = QPushButton("＋")
        plus_button.setFixedSize(40, 40)
        plus_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                border: 2px solid #000000;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #808080;
            }
            QPushButton:pressed {
                background-color: #808080;
            }
        """)


        # add the section qlabel() and the plus button to the top
        header_layout.addWidget(title_label)
        header_layout.addItem(spacer)
        header_layout.addWidget(plus_button)

        #Adding a horizontal line base sa figma
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        
        
        # adding to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(line)

        # creating a table widget for the viewing the created sections

        self.row_data = [
            ["1", "A", "BS Information Technology", "3", "Lecture", "50", "Regular"],
            ["2", "B", "BS Information Technology", "3", "Lecture", "50", "Regular"],
            ["3", "C", "BS Information Technology", "3", "Lecture", "50", "Regular"],
        ]

        self.table = QTableWidget()
        self.setup_table()

        
        main_layout.addWidget(self.table)
        
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        #create section button clicked then
        plus_button.clicked.connect(self.create_section)
    
    # method for setting up the table
    def setup_table(self):
        header_names = ["No.", "Section", "Program", "Year", "Type", "Capacity", "Remarks"]
        self.table.setColumnCount(len(header_names))
        self.table.setHorizontalHeaderLabels(header_names)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #E0E0E0;
                selection-background-color: #FFFFFF;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #084924;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 0px solid #E0E0E0;
            }
        """)

        # header = self.table.horizontalHeader()
        self.table.setColumnWidth(0,50)
        self.table.setColumnWidth(1, 80) 
        self.table.setColumnWidth(2, 300) 
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 100)  
        self.table.setColumnWidth(5, 100)   
        self.table.setColumnWidth(6, 150)  

        sample_data = [
            ["1", "A", "BS Information Technology", "3", "Lecture", "50", "Regular"],
            ["2", "B", "BS Information Technology", "3", "Lecture", "50", "Regular"],
            ["3", "C", "BS Information Technology", "3", "Lecture", "50", "Regular"],
        ]
        
        self.table.setRowCount(len(sample_data))
        
        self.refresh_table_data()
        
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.verticalHeader().hide()
        
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()

    def refresh_table_data(self):
        self.table.setRowCount(len(self.row_data))

        for row, data in enumerate(self.row_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                font = QFont("Inter", 10)
                item.setFont(font)
                item.setForeground(QColor("#4F4F4F"))
                self.table.setItem(row, col, item)

                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
    
    #method for maybe creating new window for create sections
    def create_section(self):
        dialog = Create_Section_Dialog(self)

        dialog.section_created.connect(self.on_section_created)
        
        # Show dialog
        dialog.exec()
    
    def on_section_created(self, section_data):
        new_no = str(len(self.row_data) + 1)
        
        new_section = [
            new_no,
            section_data['section'],
            section_data['program'],
            section_data['year'],
            section_data['type'],
            section_data['capacity'],
            section_data['remarks']
        ]
        
        self.row_data.append(new_section)
        
        self.refresh_table_data()
        
        print(f"New section created: {section_data}") 

        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()