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
from ......widgets.upload_class_material_widget import UploadClassMaterialPanel
from frontend.widgets.dropdown import DropdownMenu
from frontend.widgets.labeled_section import LabeledSection


class 