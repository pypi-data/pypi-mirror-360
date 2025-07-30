from PySide6.QtCore import QAbstractItemModel
from PySide6.QtCore import QObject
from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtCore import Qt


class SearchableModel(QSortFilterProxyModel):
    def __init__(
        self, model: QAbstractItemModel, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self.setSourceModel(model)
        self.setFilterKeyColumn(-1)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
