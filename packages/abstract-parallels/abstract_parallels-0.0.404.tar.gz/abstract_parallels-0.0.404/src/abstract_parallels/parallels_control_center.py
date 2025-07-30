#!/usr/bin/env python3
"""
parallels_control_center.py
A single-window launcher/manager for all Abstract-Parallels sub-GUIs.

 ▸ Starts any tool in its own QProcess
 ▸ Shows CPU / RAM live (optional; easy to hook in)
 ▸ Double-click or press “Start” to launch
 ▸ “Stop” kills the child   · “Logs” tails journalctl if it’s a systemd-user unit
 ▸ Minimises to tray; closing the window keeps children alive until you quit
"""
import os, sys, signal, subprocess, shlex
from functools       import partial
from PyQt5.QtCore    import Qt, QTimer, QProcess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QMessageBox, QSystemTrayIcon, QAction, QMenu,QStyle
)

# ── EDIT HERE if your paths differ ────────────────────────────
PKG_DIR     = os.path.dirname(os.path.abspath(__file__))
TOOLS = {
    "Window Manager":       f"{PKG_DIR}/window_mgr/run_clipit_window_mgr.sh",
    "Services Manager":     f"{PKG_DIR}/services_mgr/run_service_manager.sh",
    "API GUI":              f"{PKG_DIR}/apis/run_api_gui.sh",
    "Clipit":               f"{PKG_DIR}/clipit/run_clipit_gui.sh",
    "Dashboard Picker":     f"{PKG_DIR}/parallels_dashboard.sh"
}
# If you installed the suite via parallels_setup.sh the *same* commands work
# because the scripts are already on-path & executable.

# ──────────────────────────────────────────────────────────────

class ControlCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract-Parallels ▸ Control-Center")
        self.setGeometry(100, 100, 700, 300)
        self.processes = {}              # {name: QProcess}

        self._build_ui()
        self._make_tray()
        self._refresh_timer = QTimer(self, timeout=self.refresh_table, interval=1500)
        self._refresh_timer.start()

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget(self); self.setCentralWidget(central)
        layout  = QVBoxLayout(central)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Tool", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table)

        for tool in TOOLS:
            self._add_row(tool)

    def _add_row(self, name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem("stopped"))
        # --- action buttons ---
        btn_start  = QPushButton("Start")
        btn_stop   = QPushButton("Stop")
        btn_logs   = QPushButton("Logs")

        btn_start.clicked.connect(partial(self.start_tool,  name))
        btn_stop .clicked.connect(partial(self.stop_tool,   name))
        btn_logs .clicked.connect(partial(self.show_logs,   name))

        lay = QHBoxLayout(); box = QWidget(); box.setLayout(lay)
        for b in (btn_start, btn_stop, btn_logs):
            lay.addWidget(b)
        lay.setContentsMargins(0,0,0,0)
        self.table.setCellWidget(row, 2, box)

    # ---------- Process control ----------
    def start_tool(self, name):
        if name in self.processes and self.processes[name].state() != QProcess.NotRunning:
            self._notify("Already running", f"{name} is already active.")
            return
        cmd = TOOLS[name]
        proc = QProcess(self)
        proc.setProgram(cmd)
        proc.setProcessChannelMode(QProcess.MergedChannels)
        proc.started.connect(self.refresh_table)
        proc.finished.connect(lambda *_: self.refresh_table())
        proc.start()
        if not proc.waitForStarted(3000):
            self._notify("Launch error", f"Could not start {name}.")
            return
        self.processes[name] = proc
        self.refresh_table()

    def stop_tool(self, name):
        proc = self.processes.get(name)
        if proc and proc.state() != QProcess.NotRunning:
            proc.terminate()
            if not proc.waitForFinished(3000):
                proc.kill()
        self.refresh_table()

    def show_logs(self, name):
        # journalctl -fu abstract_<unit>.service  (if using parallels_setup)
        unit = name.split()[0].lower()           # crude → "clipboard" -> clip_win unit
        unit_map = {
            "window_mgr": "get_window_mgr",
            "services":  "services_mgr",
            "api":       "api_gui",
            "clipit":    "get_clipit",
            "dashboard": "dashboard"
        }
        svc = f"abstract_{unit_map.get(unit, unit)}.service"
        cmd = f"gnome-terminal -- bash -c 'journalctl --user -fu {svc}; exec bash'"
        subprocess.Popen(cmd, shell=True)

    # ---------- Helpers ----------
    def refresh_table(self):
        for row in range(self.table.rowCount()):
            name = self.table.item(row,0).text()
            proc = self.processes.get(name)
            running = proc and proc.state() != QProcess.NotRunning
            self.table.item(row,1).setText("running" if running else "stopped")

    def _notify(self, title, text):
        QMessageBox.information(self, title, text)

    # ---------- Tray ----------
    def _make_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        menu = QMenu()
        show  = QAction("Show / Hide", self, triggered=self.toggle_visibility)
        quit_ = QAction("Quit (All children will be stopped)", self,
                        triggered=self.close)
        menu.addAction(show); menu.addAction(quit_)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())

    # ---------- Clean-up ----------
    def closeEvent(self, ev):
        # Ask before exiting
        if any(p.state()!=QProcess.NotRunning for p in self.processes.values()):
            if QMessageBox.question(self, "Exit?",
                 "Quit Control-Center and terminate ALL running tools?",
                 QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.No:
                ev.ignore(); return
        for p in self.processes.values():
            if p.state()!=QProcess.NotRunning: p.terminate()
        QApplication.quit()

# ─── main ──────────────────────────────────────────────────────
def parallels_control_center_main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)     # allow Ctrl-C
    app = QApplication(sys.argv)
    win = ControlCenter(); win.show()
    sys.exit(app.exec_())


