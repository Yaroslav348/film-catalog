# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QFont

LOGO_SIZE = [350, 200]
SCREEN_SIZE = [400, 800]
HEADER_SIZE = [350, 20]


class Info_Window(QWidget):
    def __init__(self, name='Имя', genre='Жанр', director='Режиссёр', picture_path = 'film-catalog/film.jpg'):
        super().__init__()
        self.setGeometry(300, 300, *SCREEN_SIZE)

        self.film_name = QLabel(self)
        self.film_name.setText(name)
        self.film_name.setFont(QFont('Times', 13, QFont.Bold))
        self.film_name.resize(*HEADER_SIZE)
        self.film_name.move(25, 10)

        self.genre = QLabel(self)
        self.genre.setText(genre)
        self.genre.setFont(QFont('Times', 14))
        self.genre.resize(*HEADER_SIZE)
        self.genre.move(25, 40)

        self.pixmap = QPixmap(picture_path)
        self.pixmap = self.pixmap.scaled(*LOGO_SIZE)
        self.logo = QLabel(self)
        self.logo.resize(*LOGO_SIZE)
        self.logo.move(25, 70)
        self.logo.setPixmap(self.pixmap)

        self.director = QLabel(self)
        self.director.setText(f'Директор: {director}')
        self.director.setFont(QFont('Times', 14))
        self.director.resize(*HEADER_SIZE)
        self.director.move(25, 280)

        self.about_header = QLabel(self)
        self.about_header.setText('О фильме:')
        self.about_header.setFont(QFont('Times', 14))
        self.about_header.resize(*HEADER_SIZE)
        self.about_header.move(25, 320)

        self.about_text = QLabel(self)
        self.about_text.setWordWrap(True)
        self.about_text.setText('Планета Земля 20 тысяч лет тому назад... Удивительный доисторический мир переживает наступление Ледникового периода. Спасаясь от смертельного холода, обитатели Земли — как самые огромные, так и самые маленькие — устремляются на Юг. И только двое остаются в стороне от общего движения: мохнатый мамонт Манфред (Мэни), бродяга, полагающийся на естественный ход событий, и медлительный ленивец Сидни (Сид) — убежденный сибарит...')
        self.about_text.setFont(QFont('Times', 12))
        self.about_text.resize(350, 300)
        self.about_text.move(25, 350)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Info_Window()
    ex.show()
    sys.exit(app.exec())