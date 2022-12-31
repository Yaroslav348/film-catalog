import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QPushButton, qApp


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.asc = True
        self.connection = sqlite3.connect("films.sqlite")
        self.types = {'Режиссёр': 'director', 'Жанр': 'Genre', 'Год': 'Year', 'Название': 'Name'}
        self.btn_was_clicked = False
        self.last_position = None
        self.checkBox.stateChanged.connect(self.select_data)
        self.btn.clicked.connect(self.select_data)
        self.header = self.tableWidget.horizontalHeader()
        self.header.sectionDoubleClicked.connect(self.sort_column)
        self.select_data()

    def select_data(self):
        cur = self.connection.cursor()
        cb_contant = self.types[self.comboBox.currentText()]
        search = str(self.lineEdit.text().capitalize())
        if self.checkBox.checkState() == Qt.Unchecked:
            if self.btn_was_clicked:
                res = cur.execute(""" 
                                SELECT id, Name, Genre, Year, director, rating FROM films
                                WHERE {} LIKE '%{}%'
                                """.format(cb_contant, search)).fetchall()
            else:
                res = cur.execute("""
                                SELECT id, Name, Genre, Year, director, rating FROM films
                                """)
        else:
            if self.btn_was_clicked:
                res = cur.execute(""" 
                                SELECT id, Name, Genre, Year, director, rating FROM films
                                WHERE {} LIKE '%{}%'
                                ORDER BY rating DESC
                                """.format(cb_contant, search)).fetchmany(5)
            else:
                res = cur.execute("""
                                SELECT id, Name, Genre, Year, director, rating FROM films
                                ORDER BY rating DESC
                                """).fetchmany(5)
        self.names = list(map(lambda x: x[0], cur.description))
        self.names.append(('more'))
        self.make_table(res)
        self.btn_was_clicked = True
        pass

    def make_table(self, res):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
            btn = QPushButton()
            btn.setText('...')
            btn.setObjectName('btn_{}'.format(row[0]))
            self.tableWidget.setCellWidget(
                i, 6, btn
            )
            btn.clicked.connect(self.more_information)
        self.tableWidget.setHorizontalHeaderLabels(self.names)
        stylesheet = "::section{Background-color:rgb(175, 175, 175);border-radius:14px;}"
        
        self.header.setStyleSheet(stylesheet)
        self.header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.tableWidget.verticalHeader().hide()

    def more_information(self):
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        id = self.tableWidget.item(index.row(), 0)
        print(id.text())

    def sort_column(self, position):
        cur = self.connection.cursor()
        cb_contant = self.types[self.comboBox.currentText()]
        search = str(self.lineEdit.text().capitalize())
        sort_type = self.names[position]
        if not (self.last_position == position):
            self.asc = True
        print(position, self.last_position)
        try:
            if self.last_position == position:
                self.asc = not self.asc
            print(self.asc)
            if self.asc:
                res = cur.execute("""
                                SELECT id, Name, Genre, Year, director, rating FROM films
                                WHERE {} LIKE '%{}%'
                                ORDER BY 
                                {} ASC""".format(cb_contant, search, sort_type)).fetchall()
            else:
                res = cur.execute("""
                                SELECT id, Name, Genre, Year, director, rating FROM films
                                WHERE {} LIKE '%{}%'
                                ORDER BY 
                                {} DESC""".format(cb_contant, search, sort_type)).fetchall()
            self.make_table(res) 
        except sqlite3.OperationalError:
            pass
        self.last_position = position

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())