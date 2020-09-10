from PyQt5 import QtCore, QtWidgets
import sys
import os
import signal
import subprocess
import psutil
from PyQt5.QtGui import QPalette, QColor
from time import sleep


class PythonProcessThread(QtCore.QThread):
    change_value = QtCore.pyqtSignal(list)

    def run(self):
        while True:
            wmic_cmd = """wmic process where 'name="pythonw.exe" or name="python.exe"' get commandline,processid"""
            wmic_prc = subprocess.Popen(wmic_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            wmic_out, wmic_err = wmic_prc.communicate()

            python_procs = [item.rsplit(None, 1) for item in wmic_out.splitlines() if item][1:]
            python_procs = [[cmdline.decode("utf-8"), int(pid), 0, 0] for [cmdline, pid] in python_procs if
                            int(pid) != os.getpid()]
            for i, item in enumerate(python_procs):
                item_pid = psutil.Process(int(item[1]))
                item[2] = f"{item_pid.cpu_percent(interval=0.1) / psutil.cpu_count():.1f}"
                item[3] = f"{item_pid.memory_full_info().uss / 1000000:.1f}"
            self.change_value.emit(python_procs)
            sleep(1)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.pythons = {}
        self.processTimer = QtCore.QTimer()
        self.setObjectName("MainWindow")
        self.resize(800, 600)
        self.setMinimumSize(400, 200)
        self.setWindowTitle("Python Task Manager")
        self.setupUI()
        self.startProcessThread()

    def startProcessThread(self):
        self.proc_thread = PythonProcessThread()
        self.proc_thread.change_value.connect(self.setPythonProcs)
        self.proc_thread.start()

    def setPythonProcs(self, python_procs):
        self.pythons = {}
        for i, item in enumerate(python_procs):
            self.pythons[item[1]] = {"process": item[0], "cpu": item[2], "ram": item[3]}
        # print(self.pythons)
        to_remove = []
        for x in range(self.processlist.rowCount()):
            if self.processlist.item(x, 0) is not None:
                if int(self.processlist.item(x, 0).text()) not in self.pythons.keys():
                    to_remove.append(x)
                    break
        for item in to_remove:
            self.processlist.removeRow(item)
        self.getPythonProcesses()

    def setupUI(self):
        self.setupCentralWindow()
        self.setupMenuBar()

        self.retranslateUI()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setupUIActions()

    def setupUIActions(self):
        self.deleteSelectedItemButton.clicked.connect(lambda: self.killSelectedProcess())

    def setupCentralWindow(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.deleteSelectedItemButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteSelectedItemButton.setObjectName("deleteSelectedItemButton")
        self.deleteSelectedItemButton.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        font = self.deleteSelectedItemButton.font()
        font.setPointSize(10)
        self.deleteSelectedItemButton.setFont(font)

        self.processlist = QtWidgets.QTableWidget(self.centralwidget)
        self.processlist.setRowCount(0)
        self.processlist.setColumnCount(4)
        self.processlist.setShowGrid(True)
        self.processlist.setFocusPolicy(QtCore.Qt.NoFocus)
        self.processlist.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        stylesheet = "QTableWidget::item{selection-background-color: #a9e5e8; selection-color: black;}"
        self.processlist.setStyleSheet(stylesheet)
        self.processlist.setHorizontalHeaderLabels(["PID", "CPU %", "Memory (MB)", "Process Name"])
        self.processlist.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.processlist.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.processlist.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.processlist.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.processlist.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.vBox = QtWidgets.QVBoxLayout(self.centralwidget)
        self.vBox.addWidget(self.processlist)
        self.vBox.addWidget(self.deleteSelectedItemButton, alignment=QtCore.Qt.AlignRight)

        self.setCentralWidget(self.centralwidget)

    def setupMenuBar(self):
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Python Task Manager"))
        self.deleteSelectedItemButton.setText(_translate("MainWindow", "End Process"))

    def getPythonProcesses(self):
        for i, key in enumerate(self.pythons):
            cont_flag = False
            for x in range(self.processlist.rowCount()):
                if self.processlist.item(x, 0) is not None:
                    if int(self.processlist.item(x, 0).text()) == int(key):
                        self.processlist.item(x, 0).setText(f"{key}")
                        self.processlist.item(x, 1).setText(f"{self.pythons[key]['cpu']}")
                        self.processlist.item(x, 2).setText(f"{self.pythons[key]['ram']}")
                        self.processlist.item(x, 3).setText(
                            f"""{self.pythons[key]['process'].split(" ", 1)[1].replace('"', "")}""")
                        cont_flag = True
                        break
            if cont_flag:
                continue
            print(f"inserting row - {i} {self.pythons[key]}")
            self.processlist.insertRow(i)
            self.processlist.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{key}"))
            self.processlist.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{self.pythons[key]['cpu']}"))
            self.processlist.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{self.pythons[key]['ram']}"))
            self.processlist.setItem(i, 3, QtWidgets.QTableWidgetItem(
                f"""{self.pythons[key]['process'].split(" ", 1)[1].replace('"', "")}"""))

    def killSelectedProcess(self):
        if self.processlist.currentRow() is not None:
            os.kill(int(self.processlist.item(self.processlist.currentRow(), 0).text()), signal.SIGTERM)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
