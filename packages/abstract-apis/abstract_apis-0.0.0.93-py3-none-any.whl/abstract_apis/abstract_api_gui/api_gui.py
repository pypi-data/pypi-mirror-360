#!/usr/bin/env python3
# temp_py.py — GUI front-end for abstract_apis with dynamic endpoints, headers & params

import sys
import json
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QMessageBox,
    QTableWidget, QSizePolicy, QTableWidgetItem, QAbstractItemView, QCheckBox
)
from PyQt5.QtCore import Qt
from abstract_apis import getRequest, postRequest

# ─── Configuration ──────────────────────────────────────────────────────
PREDEFINED_BASE_URLS = [
    "https://abstractendeavors.com",
    "https://clownworld.biz",
    "https://typicallyoutliers.com",
    "https://thedailydialectics.com",
]
# Common headers to show by default
PREDEFINED_HEADERS = [
    ("Content-Type", "application/json"),
    ("Accept", "application/json"),
    ("Authorization", "Bearer "),
]

# ─── Logging Handler ──────────────────────────────────────────────────────
class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.ensureCursorVisible()

# ─── Main GUI ─────────────────────────────────────────────────────────────
class APIConsole(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Console for abstract_apis")
        self.resize(800, 900)
        self._build_ui()
        self._setup_logging()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Base URL selection
        layout.addWidget(QLabel("Base URL:"))
        self.base_combo = QComboBox()
        self.base_combo.setEditable(True)
        self.base_combo.addItems(PREDEFINED_BASE_URLS)
        self.base_combo.setInsertPolicy(QComboBox.NoInsert)
        layout.addWidget(self.base_combo)

        # Endpoints table
        layout.addWidget(QLabel("Endpoints (enter paths, select one row):"))
        self.endpoints_table = QTableWidget(1, 1)
        self.endpoints_table.setHorizontalHeaderLabels(["Endpoint Path"])
        self.endpoints_table.horizontalHeader().setStretchLastSection(True)
        self.endpoints_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.endpoints_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.endpoints_table.setFixedHeight(200)
        layout.addWidget(self.endpoints_table)
        self.endpoints_table.cellChanged.connect(self._maybe_add_endpoint_row)

        # Method selector
        row = QHBoxLayout()
        row.addWidget(QLabel("Method:"))
        self.method_box = QComboBox()
        self.method_box.addItems(["GET", "POST"])
        row.addWidget(self.method_box)
        layout.addLayout(row)

        # Headers table
        layout.addWidget(QLabel("Headers (check to include):"))
        self.headers_table = QTableWidget(len(PREDEFINED_HEADERS)+1, 3)
        self.headers_table.setHorizontalHeaderLabels(["Use", "Key", "Value"])
        self.headers_table.horizontalHeader().setStretchLastSection(True)
        self.headers_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.headers_table.setFixedHeight(200)
        layout.addWidget(self.headers_table)
        # Populate predefined headers
        for i, (key, val) in enumerate(PREDEFINED_HEADERS):
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Checked)
            self.headers_table.setItem(i, 0, chk)
            self.headers_table.setItem(i, 1, QTableWidgetItem(key))
            self.headers_table.setItem(i, 2, QTableWidgetItem(val))
        # blank row for custom
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 0, QTableWidgetItem())
        self.headers_table.cellChanged.connect(self._maybe_add_header_row)

        # Body / Query-Params table
        layout.addWidget(QLabel("Body / Query-Params (key → value):"))
        self.body_table = QTableWidget(1, 2)
        self.body_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.body_table.horizontalHeader().setStretchLastSection(True)
        self.body_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.body_table.setFixedHeight(200)
        layout.addWidget(self.body_table)
        self.body_table.cellChanged.connect(self._maybe_add_body_row)

        # Send button
        self.send_button = QPushButton("▶ Send Request")
        layout.addWidget(self.send_button)

        # Response
        layout.addWidget(QLabel("Response:"))
        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setFixedHeight(200)
        layout.addWidget(self.response_output)

        # Logs
        layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(150)
        layout.addWidget(self.log_output)

        self.send_button.clicked.connect(self.send_request)

    def _maybe_add_endpoint_row(self, row, col):
        last = self.endpoints_table.rowCount() - 1
        if row == last and self.endpoints_table.item(row, 0) and self.endpoints_table.item(row, 0).text().strip():
            self.endpoints_table.blockSignals(True)
            self.endpoints_table.insertRow(last+1)
            self.endpoints_table.blockSignals(False)

    def _maybe_add_header_row(self, row, col):
        last = self.headers_table.rowCount() - 1
        if row != last:
            return
        key_item = self.headers_table.item(row, 1)
        val_item = self.headers_table.item(row, 2)
        if (key_item and key_item.text().strip()) or (val_item and val_item.text().strip()):
            self.headers_table.blockSignals(True)
            self.headers_table.insertRow(last+1)
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Unchecked)
            self.headers_table.setItem(last+1, 0, chk)
            self.headers_table.blockSignals(False)

    def _maybe_add_body_row(self, row, col):
        last = self.body_table.rowCount() - 1
        if row == last and ((self.body_table.item(row, 0) and self.body_table.item(row, 0).text().strip()) or
                            (self.body_table.item(row, 1) and self.body_table.item(row, 1).text().strip())):
            self.body_table.blockSignals(True)
            self.body_table.insertRow(last+1)
            self.body_table.blockSignals(False)

    def _setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = QTextEditLogger(self.log_output)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'))
        logger.addHandler(handler)

    def _collect_table_data(self, table):
        data = {}
        for r in range(table.rowCount()):
            key_item = table.item(r, 0)
            if not key_item or not key_item.text().strip():
                continue
            key = key_item.text().strip()
            val_item = table.item(r, 1)
            data[key] = val_item.text().strip() if val_item else ""
        return data

    def _collect_headers(self):
        headers = {}
        for r in range(self.headers_table.rowCount()):
            chk_item = self.headers_table.item(r, 0)
            if not chk_item or chk_item.checkState() != Qt.Checked:
                continue
            key_item = self.headers_table.item(r, 1)
            if not key_item or not key_item.text().strip():
                continue
            val_item = self.headers_table.item(r, 2)
            headers[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return headers

    def send_request(self):
        base = self.base_combo.currentText().strip().rstrip('/')
        selected = self.endpoints_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "No endpoint", "Please select an endpoint row.")
            return
        r = selected[0].row()
        ep_item = self.endpoints_table.item(r, 0)
        if not ep_item or not ep_item.text().strip():
            QMessageBox.warning(self, "Invalid endpoint", "Selected endpoint is empty.")
            return
        endpoint = ep_item.text().strip()
        url = base + endpoint

        method = self.method_box.currentText()
        headers = self._collect_headers()
        params = self._collect_table_data(self.body_table)

        logging.info(f"➡ {method} {url} | headers={headers} | params={params}")
        self.response_output.clear()

        try:
            if method == "GET":
                result = getRequest(url=url, headers=headers, data=params)
            else:
                result = postRequest(url=url, headers=headers, data=params)

            out = json.dumps(result, indent=4) if isinstance(result, dict) else str(result)
            self.response_output.setPlainText(out)
            logging.info("✔ Response displayed")
        except Exception as ex:
            err = f"✖ Error: {ex}"
            self.response_output.setPlainText(err)
            logging.error(err)


def get_api_gui():
    app = QApplication(sys.argv)
    win = APIConsole()
    win.show()
    sys.exit(app.exec_())
