import sqlite3
import sys
from PyQt5 import uic
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QWidget, QTextEdit, QFileDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QPushButton, qApp


LOGO_SIZE = [350, 200]
SCREEN_SIZE = [400, 800]
HEADER_SIZE = [350, 20]


class FilmDB(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('main_window.ui', self)
        try:
            self.connection = sqlite3.connect("film-catalog/films.sqlite")
        except sqlite3.OperationalError:
            self.connection = sqlite3.connect("films.sqlite")
        self.asc = True
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
        self.btn_add.clicked.connect(self.add_row)
        add_styleSheet = '''QPushButton {background-color:rgb(50, 240, 50);border-radius:5px;border-style: outset; 
                            border-width: 2px; border-color:rgb(125, 125, 125);}
                            QPushButton:hover {background-color:rgb(100, 240, 150);
                            border-width: 2px; border-color:rgb(50, 50, 240);}
                            QPushButton:pressed {background-color:rgb(100, 200, 150);
                            border-width: 2px; border-color:rgb(50, 50, 200);}'''
        self.btn_add.setStyleSheet(add_styleSheet)
        remove_styleSheet = '''QPushButton {background-color:rgb(240, 50, 50);border-radius:5px;border-style: outset; 
                            border-width: 2px; border-color:rgb(125, 125, 125);}
                            QPushButton:hover {background-color:rgb(240, 100, 150);
                            border-width: 2px; border-color:rgb(50, 50, 240);}
                            QPushButton:pressed {background-color:rgb(200, 100, 150);
                            border-width: 2px; border-color:rgb(50, 50, 200);}'''
        self.btn_remove.setStyleSheet(remove_styleSheet)
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
        cur = self.connection.cursor()
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        id = self.tableWidget.item(index.row(), 0).text()
        self.info_res = cur.execute("""
                                    SELECT id, Name, Genre, director, description, logo FROM films
                                    WHERE id = '{}'""".format(id)).fetchone()
        print(self.info_res)
        self.info = Info_Window()
        self.info.show()

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
            dialog = MyAppDialog()
            dialog.exec()
            if dialog.ok_pressed:
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
            else:
                self.select_data()
        
    def remove_row(self):
        dialog = MyAppDialog()
        dialog.exec()
        if dialog.ok_pressed:
            cur = self.connection.cursor()
            delete_item = self.tableWidget.selectedItems()
            id = self.tableWidget.item(delete_item[0].row(), 0).text()
            cur.execute("""
                        DELETE FROM films
                        WHERE id = '{}'""".format(id))
            self.select_data()
            self.connection.commit()

    def add_row(self):
        cur = self.connection.cursor()
        id = self.tableWidget.rowCount()
        self.tableWidget.insertRow(id)
        values = [id + 1] + ['pass' for _ in range(7)]
        print(values)
        cur.execute("""
                    INSERT INTO films 
                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(*values))
        self.select_data()
        self.connection.commit()


class MyAppDialog(QDialog):
    def __init__(self) -> None:
        QDialog.__init__(self)
        uic.loadUi('dialog.ui', self)
        self.ok_pressed = False
        self.btn_2.clicked.connect(self.close)
        self.btn_1.clicked.connect(self.ok)

    def ok(self) -> None:
        self.ok_pressed = True
        self.close()


class Info_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 205, *SCREEN_SIZE)

        self.film_name = QLabel(self)
        self.film_name.setText(ex.info_res[1])
        self.film_name.setFont(QFont('Times', 13, QFont.Bold))
        self.film_name.resize(*HEADER_SIZE)
        self.film_name.move(25, 10)

        self.genre = QLabel(self)
        self.genre.setText(ex.info_res[2])
        self.genre.setFont(QFont('Times', 14))
        self.genre.resize(*HEADER_SIZE)
        self.genre.move(25, 40)

        self.pixmap = QPixmap(ex.info_res[5])
        if self.pixmap.isNull():
            self.pixmap = QPixmap(ex.info_res[5][13:])
        self.pixmap = self.pixmap.scaled(*LOGO_SIZE)
        self.logo = QLabel(self)
        self.logo.resize(*LOGO_SIZE)
        self.logo.move(25, 70)
        self.logo.setPixmap(self.pixmap)
        self.logo.mouseDoubleClickEvent = self.change_logo

        self.director = QLabel(self)
        self.director.setText(f'Директор: {ex.info_res[3]}')
        self.director.setFont(QFont('Times', 14))
        self.director.resize(*HEADER_SIZE)
        self.director.move(25, 280)

        self.about_header = QLabel(self)
        self.about_header.setText(f'О фильме:')
        self.about_header.setFont(QFont('Times', 14))
        self.about_header.resize(*HEADER_SIZE)
        self.about_header.move(25, 320)

        self.about_text = QTextEdit(self)
        self.about_text.setText(ex.info_res[4])
        self.about_text.setFont(QFont('Times', 12))
        self.about_text.resize(350, 300)
        self.about_text.move(25, 350)
        self.about_text.textChanged.connect(self.change_description)

    def change_description(self):
        new_desc = self.about_text.toPlainText()
        cur = ex.connection.cursor()
        id = ex.info_res[0]
        print(id, new_desc)
        cur.execute("""
                    UPDATE films
                    SET description = '{}'
                    WHERE id = '{}'
                    """.format(new_desc, id))
        ex.connection.commit()

    def change_logo(self, event):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        start = fname.find('film-catalog')
        fname = fname[start:]
        cur = ex.connection.cursor()
        id = ex.info_res[0]
        if fname != '':
            cur.execute("""
                        UPDATE films
                        SET logo = '{}'
                        WHERE id = '{}'
                        """.format(fname, id))
            ex.connection.commit()
            new_pixmap = QPixmap(fname)
            if new_pixmap.isNull:
                new_pixmap = QPixmap(fname[13:])
            self.logo.setPixmap(new_pixmap)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilmDB()
    ex.show()
    sys.exit(app.exec())