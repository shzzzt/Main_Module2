from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableView,
                             QStackedWidget, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QFont, QIcon, QColor

class SectionsTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = ['No.', 'Section', 'Program', 'Year', 'Type', 'Capacity', 'Remarks']
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = self._data[index.row()]
        col = index.column()
        value = list(row.values())[col]
        
        if role == Qt.ItemDataRole.DisplayRole:
            return str(value)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Center-align numeric columns (No., Year, Capacity)
            if col in [0, 3, 5]:
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Handle background for selected and alternate rows
            if index.row() % 2 == 0:
                return QColor("#ffffff")
            return QColor("#f5f5f5")
        elif role == Qt.ItemDataRole.ForegroundRole:
            # Ensure text is visible when selected
            return QColor("#2d2d2d")
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        elif role == Qt.ItemDataRole.TextAlignmentRole and orientation == Qt.Orientation.Horizontal:
            return Qt.AlignmentFlag.AlignCenter
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        # Items stay visible and "enabled" but cannot be selected or edited
        return Qt.ItemFlag.ItemIsEnabled