import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QPushButton, qApp


class DBSample(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.asc = True
        self.connection = sqlite3.connect("films.sqlite")
        self.types = {'Режиссёр': 'director', 'Жанр': 'Genre', 'Год': 'Year', 'Название': 'Name'}
        self.btn_was_clicked = False
        self.last_position = None
        self.human_changing = False
        self.checkBox.stateChanged.connect(self.select_data)
        self.btn.clicked.connect(self.select_data)
        self.header = self.tableWidget.horizontalHeader()
        self.header.sectionDoubleClicked.connect(self.sort_column)
        self.tableWidget.itemChanged.connect(self.change_item)
        self.btn_remove.clicked.connect(self.remove_row)
        self.select_data()

    def select_data(self) -> None:
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

    def make_table(self, res: sqlite3.Cursor) -> None:
        self.human_changing = False
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
        self.human_changing = True

    def more_information(self) -> None:
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        id = self.tableWidget.item(index.row(), 0)
        print(id.text())

    def sort_column(self, position: int) -> None:
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

    def change_item(self, item: QTableWidgetItem) -> None:
        if self.human_changing:
            cur = self.connection.cursor()
            row = item.row()
            column = item.column()
            change_type = self.names[column]
            new_text = item.text()
            id = self.tableWidget.item(row, 0).text()
            cur.execute("""
                    UPDATE films
                    SET '{}' = '{}'
                    WHERE id = '{}'
                    """.format(change_type, new_text, id))
            self.connection.commit()
        
    def remove_row(self):
        dialog = MyAppDialog()
        dialog.exec()
        if dialog.delete:
            print(self.tableWidget.selectedItems())


class MyAppDialog(QDialog):
    def __init__(self) -> None:
        QDialog.__init__(self)
        uic.loadUi('dialog.ui', self)
        self.delete = False
        self.btn_2.clicked.connect(self.close)
        self.btn_1.clicked.connect(self.ok)

    def ok(self) -> None:
        self.delete = True
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())