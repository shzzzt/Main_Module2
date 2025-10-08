from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt6.QtGui import QColor
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class SectionTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        """
        Initialize the sections table model. 

        Args:
            parent: Parent object (optional)
        """

        super().__init__()
        self._sections: List[Dict] = [] 
        self._headers = [
            "No.", 
            "Section", 
            "Program", 
            "Year", 
            "Type", 
            "Capacity", 
            "Remarks"
        ]

        logging.info("Initialized section table model")

    # def load_data(self):
    #     self.beginResetModel()
    #     self._sections = self._service.get_sections()
    #     self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._sections)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        section = self._sections[index.row()]
        keys = ["id", "section", "program", "year", "type", "capacity", "remarks"]
        return section.get(keys[index.column()], "")
    
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

    def add_section(self, section: Dict) -> None:
        logger.debug(f"Entered add_section method")

        section_row = len(self._sections)

        # notify view of row insertion
        self.beginInsertRows(QModelIndex(), section_row, section_row)
        self._sections.append(section)
        self.endInsertRows()
    
    def set_sections(self, sections_data: List[Dict]) -> None:
        self.beginResetModel()
        self._sections = sections_data.copy() if sections_data else []
        self.endResetModel() 

