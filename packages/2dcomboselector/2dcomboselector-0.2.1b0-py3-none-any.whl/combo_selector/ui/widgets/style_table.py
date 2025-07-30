from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QHeaderView
)
from PySide6.QtCore import Qt, QModelIndex, Signal, QThreadPool

from combo_selector.core.workers import TableDataWorker
from combo_selector.ui.widgets.orthogonality_table import OrthogonalityTableView, OrthogonalityTableModel



class StyledTable(QWidget):
    selectionChanged = Signal()
    def __init__(self,title=''):
        super().__init__()

        self.threadpool = QThreadPool()
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("CardFrame")
        card.setLayout(QVBoxLayout())
        card.layout().setContentsMargins(0, 0, 0, 0)
        card.layout().setSpacing(0)

        # Title bar
        title = QLabel(title)
        title.setFixedHeight(30)
        title.setObjectName("TitleBar")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title.setContentsMargins(10, 0, 0, 0)

        # Table
        self.model = OrthogonalityTableModel()
        self.table = OrthogonalityTableView(self,self.model)


        # Footer
        footer = QFrame()
        footer.setObjectName("Footer")
        footer.setLayout(QHBoxLayout())
        footer.layout().setContentsMargins(12, 6, 12, 6)
        footer.layout().setSpacing(8)

        # combo1 = QComboBox()
        # combo1.addItems(["2020", "2021", "2022"])
        # combo2 = QComboBox()
        # combo2.addItems([">20,000", ">30,000", "All"])
        # combo3 = QComboBox()
        # combo3.addItems(["All", "Positive", "Negative"])

        # footer.layout().addWidget(combo1)
        # footer.layout().addWidget(combo2)
        # footer.layout().addStretch()
        # footer.layout().addWidget(combo3)

        # Assemble
        card.layout().addWidget(title)
        card.layout().addWidget(self.table)
        card.layout().addWidget(footer)
        outer.addWidget(card)

        self._apply_styles()

        self.table.selectionModel().selectionChanged.connect(self.selection_changed)

    def clean_table(self):
        self.model.set_formated_data([])
        self.set_default_row_count(10)

    def selection_changed(self):
        self.selectionChanged.emit()

    def async_set_table_data(self, df):
        worker = TableDataWorker(df, self.model.get_header_label())
        worker.signals.finished.connect(self.handle_data)
        self.threadpool.start(worker)

    def handle_data(self,data, rows, cols):
        self.model.apply_formatted_data(data, rows, cols)



    def set_table_data(self,data):
        self.model.set_data(data)
        # self.table.resizeColumnsToContents()

        for col in range(self.model.columnCount(QModelIndex())):
            current_width = self.table.columnWidth(col)
            self.table.setColumnWidth(col, current_width + 10)  # Add padding

        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.table.horizontalHeader().setStretchLastSection(True)

        for i in range(self.table.model().columnCount(QModelIndex())):
            if i == 1:  # 'Combination' column index
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def set_table_proxy(self):
        self.model.set_proxy(self.table.getProxyModel())

    def get_proxy_model(self):
        return self.table.getProxyModel()

    def get_selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def get_model(self):
        return self.model

    def get_table_view(self):
        return self.table

    def get_row_count(self):
        return self.model.rowCount(QModelIndex())

    def select_row(self,index):
        self.table.selectRow(index)

    def set_header_label(self,header_label):
        self.model.set_header_label(header_label)

    def set_default_row_count(self,value):
        self.model.set_default_row_count(value)


    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI, Arial;
                font-size: 13px;
            }

            QFrame#CardFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #d0d5dd;
            }

            QLabel#TitleBar {
                background-color: #154E9D;
                color: white;
                font-weight:bold;
                font-size: 16px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }

    QHeaderView::section {
        background-color: #D1D9FC;
        color: #154E9D;
        font-size: 12px;
        padding: 4px;
        font-weight: bold;
        border: 1px solid #d0d4da;
    }

    QTableView {
    
        background-color: #F6F8FD;
        border: 1px solid #F6F8FD;
        gridline-color: #D4D6EC;
        selection-background-color: #c9daf8;
        selection-color: #000000;
        font-size: 11px;
    }

    QTableView::item {
        padding: 6px;Y
        padding: 2px;
        border: none;
    }

    QTableView::item:selected {
        background-color: #d8e5fc;
        color: #000000;
    }

    QScrollBar:vertical {
        border: none;
        background: #bdcaf6;
        width: 10px;
        margin: 4px 0 4px 0;
    }

    QScrollBar::handle:vertical {
        background: white;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
    }

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }

    QComboBox {
        background-color: #ffffff;
        border: 1px solid #c5d0e6;
        border-radius: 6px;
        padding: 5px 8px;
        font-size: 14px;
    }

            QFrame#Footer {
                background-color: #f1f3f6;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }

            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                padding: 4px 8px;
                border-radius: 4px;
            }
        """)