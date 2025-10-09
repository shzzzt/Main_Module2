import logging
from typing import Dict, List

from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt6.QtGui import QColor

logger = logging.getLogger(__name__)

class ClassesTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._classes: List[Dict] = []
        self._headers = [
            "No.",
            "Code",
            "Title",
            "Units",
            "Section",
            "Schedule",
            "Room",
            "Instructor",
            "Type"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._classes)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self._classes) or index.row() < 0:
            return None

        class_obj = self._classes[index.row()]
        col = index.column()

        # Display role
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:  # No.
                return str(index.row() + 1)  # Auto-number rows
            elif col == 1:  # Code
                return class_obj.get('code', '')
            elif col == 2:  # Title
                return class_obj.get('title', '')
            elif col == 3:  # Units
                return str(class_obj.get('units', ''))
            elif col == 4:  # Section
                return class_obj.get('section_name', '')
            elif col == 5:  # Schedule
                return class_obj.get('schedules', [])
            elif col == 6:  # Room
                return class_obj.get('room', '')
            elif col == 7:  # Instructor
                return class_obj.get('instructor', '')
            elif col == 8:  # Type
                return class_obj.get('type', '')
            return None

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Center-align numeric columns (No., Units)
            if col in [0, 3]:
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() % 2 == 0:
                return QColor("#ffffff")
            return QColor("#f5f5f5")

        elif role == Qt.ItemDataRole.ForegroundRole:
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

    # ========================================================
    # DATA MANAGEMENT METHODS
    # ========================================================

    def add_class(self, class_data:Dict) -> None:
        logger.info("Entered add_class method")

        class_row = len(self._classes)

        self.beginInsertRows(QModelIndex(), class_row, class_row)
        self._classes.append(class_data)
        self.endInsertRows()

    def set_classes(self, classes: Dict) -> None:
        self.beginResetModel()
        self._classes = classes.copy() if classes else []
        self.endResetModel()
