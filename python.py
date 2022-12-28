import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.connection = sqlite3.connect("films.sqlite")
        self.btn.clicked.connect(self.select_data)
        self.select_data()

    def select_data(self):
        cur = self.connection.cursor()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        print(cur.description)
        names = list(map(lambda x: x[0], cur.description))
        res_2 = cur.execute(f""" SELECT * FROM films""").fetchall()
        print(res_2)
        for i, row in enumerate(res_2):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        # self.tableWidget.setHorizontalHeaderLabels(names)

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())