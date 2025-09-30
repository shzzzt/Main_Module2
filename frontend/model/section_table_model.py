# models/section_table_model.py
from PyQt6.QtCore import QAbstractTableModel, Qt

class SectionTableModel(QAbstractTableModel):
    def __init__(self, service):
        super().__init__()
        self._headers = ["No.", "Section", "Program", "Year", "Type", "Capacity", "Remarks"]
        self._sections = []
        self._service = service

    def load_data(self):
        self.beginResetModel()
        self._sections = self._service.get_sections()
        self.endResetModel()

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
        return None
