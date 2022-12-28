import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.connection = sqlite3.connect("films.db")
        self.types = {'Режиссёр': 'director', 'Жанр': 'Genre', 'Год': 'Year', 'Название': 'Name'}
        self.btn_was_clicked = False
        self.btn.clicked.connect(self.select_data)
        self.select_data()

    def select_data(self):
        cur = self.connection.cursor()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        cb_contant = self.types[self.comboBox.currentText()]
        search = str(self.lineEdit.text().capitalize())
        if self.btn_was_clicked:
            res = cur.execute(""" 
                            SELECT * FROM films
                            WHERE {} LIKE '%{}%'
                            """.format(cb_contant, search)).fetchall()
        else:
            res = cur.execute("""
                            SELECT * FROM films
                            """)
        names = list(map(lambda x: x[0], cur.description))
        print(res)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.setHorizontalHeaderLabels(names)
        stylesheet = "::section{Background-color:rgb(175, 175, 175);border-radius:14px;}"
        self.tableWidget.horizontalHeader().setStyleSheet(stylesheet)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().hide()
        self.btn_was_clicked = True

        

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())