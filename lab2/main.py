import sys
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QFrame, QTextEdit, QPushButton)
from PyQt5.QtCore import pyqtSignal, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

import cl1
import cl2

class MainWindow(QWidget):
    krw_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа #2 Буторина 6231")
        self.setMinimumSize(600, 780)
        
        self.rate_rub_to_jpy = 1.65
        self.rate_rub_to_krw = 14.50

        self.rub_model = cl1.RubModel()
        self.jpy_model = cl2.JpyModel()

        self.last_edited = 'rub'
        self.last_saved_state = ""

        self.init_ui()
        self.init_signals()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7f6;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#card {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            QLabel { font-size: 14px; font-weight: bold; color: #555; }
            QLabel#title {
                font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;
            }
            QLineEdit {
                padding: 12px; border: 2px solid #e0e0e0; border-radius: 10px;
                font-size: 16px; background-color: #fafafa; color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #3498db; background-color: #ffffff;
            }
            QTextEdit {
                background-color: white; border: 1px solid #e0e0e0;
                border-radius: 10px; padding: 10px; font-size: 13px; color: #555;
            }
            QPushButton {
                background-color: #ff6b6b; color: white; border: none;
                border-radius: 5px; padding: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #ff5252; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(10)

        title = QLabel("Конвертер валют")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        regex = QRegExp(r"^\d*[.,]?\d{0,2}$")
        validator = QRegExpValidator(regex)

        self.input_rub = QLineEdit()
        self.input_rub.setPlaceholderText("0.00")
        self.input_rub.setValidator(validator)
        self.input_rub.setAlignment(Qt.AlignRight)
        self.input_rub.setMinimumWidth(450)
        main_layout.addWidget(self.create_card("🇷🇺 Рубли (RUB)", self.input_rub))

        self.input_jpy = QLineEdit()
        self.input_jpy.setPlaceholderText("0.00")
        self.input_jpy.setValidator(validator)
        self.input_jpy.setAlignment(Qt.AlignRight)
        self.input_jpy.setMinimumWidth(450)
        main_layout.addWidget(self.create_card("🇯🇵 Йены (JPY)", self.input_jpy))

        self.input_krw = QLineEdit()
        self.input_krw.setPlaceholderText("0.00")
        self.input_krw.setValidator(validator)
        self.input_krw.setAlignment(Qt.AlignRight)
        self.input_krw.setMinimumWidth(450)
        main_layout.addWidget(self.create_card("🇰🇷 Воны (KRW)", self.input_krw))

        history_label = QLabel("История переводов:")
        history_label.setStyleSheet("margin-top: 10px; font-size: 15px;")
        main_layout.addWidget(history_label)

        hint_label = QLabel("Нажмите Enter (или кликните в другое поле), чтобы записать перевод")
        hint_label.setStyleSheet("font-size: 12px; color: #888; font-style: italic; margin-bottom: 5px; font-weight: normal;")
        hint_label.setWordWrap(True)
        main_layout.addWidget(hint_label)

        self.history_area = QTextEdit()
        self.history_area.setReadOnly(True)
        main_layout.addWidget(self.history_area, stretch=1)

        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.history_area.clear)
        main_layout.addWidget(clear_btn)

        self.setLayout(main_layout)

    def create_card(self, title_text, input_widget):
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 10, 15, 15)
        card_layout.setSpacing(5)
        
        lbl = QLabel(title_text)
        card_layout.addWidget(lbl)
        card_layout.addWidget(input_widget)
        card.setLayout(card_layout)
        return card

    def init_signals(self):
        self.input_rub.textChanged.connect(self.on_rub_changed)
        self.input_jpy.textChanged.connect(self.on_jpy_changed)
        self.input_krw.textChanged.connect(self.on_krw_changed)

        self.rub_model.rub_changed.connect(self.update_from_rub)
        self.jpy_model.jpy_changed.connect(self.update_from_jpy)
        self.krw_changed.connect(self.update_from_krw)

        self.input_rub.editingFinished.connect(self.save_to_history)
        self.input_jpy.editingFinished.connect(self.save_to_history)
        self.input_krw.editingFinished.connect(self.save_to_history)

    def _parse(self, text):
        text = text.strip().replace(',', '.')
        if not text or text == '.':
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def on_rub_changed(self):
        self.last_edited = 'rub'
        val = self._parse(self.input_rub.text())
        if val is None:
            self.set_text_safely(self.input_jpy, None)
            self.set_text_safely(self.input_krw, None)
            return
        self.rub_model.send_rub(val)

    def on_jpy_changed(self):
        self.last_edited = 'jpy'
        val = self._parse(self.input_jpy.text())
        if val is None:
            self.set_text_safely(self.input_rub, None)
            self.set_text_safely(self.input_krw, None)
            return
        self.jpy_model.send_jpy(val)

    def on_krw_changed(self):
        self.last_edited = 'krw'
        val = self._parse(self.input_krw.text())
        if val is None:
            self.set_text_safely(self.input_rub, None)
            self.set_text_safely(self.input_jpy, None)
            return
        self.krw_changed.emit(val)

    def update_from_rub(self, rub):
        self.set_text_safely(self.input_jpy, rub * self.rate_rub_to_jpy)
        self.set_text_safely(self.input_krw, rub * self.rate_rub_to_krw)

    def update_from_jpy(self, jpy):
        rub = jpy / self.rate_rub_to_jpy
        self.set_text_safely(self.input_rub, rub)
        self.set_text_safely(self.input_krw, rub * self.rate_rub_to_krw)

    def update_from_krw(self, krw):
        rub = krw / self.rate_rub_to_krw
        self.set_text_safely(self.input_rub, rub)
        self.set_text_safely(self.input_jpy, rub * self.rate_rub_to_jpy)

    def set_text_safely(self, widget, value):
        widget.blockSignals(True)
        if value is None:
            widget.clear()
        else:
            widget.setText(f"{value:.2f}")
        widget.blockSignals(False)

    def save_to_history(self):
        rub = self.input_rub.text()
        jpy = self.input_jpy.text()
        krw = self.input_krw.text()

        if not rub or not jpy or not krw:
            return
        try:
            if float(rub.replace(',', '.')) == 0.0:
                return
        except ValueError:
            return

        current_state = f"{rub}-{jpy}-{krw}"
        if current_state == self.last_saved_state:
            return
        self.last_saved_state = current_state

        time_str = datetime.now().strftime("%H:%M:%S")

        if self.last_edited == 'rub':
            entry = f"[{time_str}] 🇷🇺 {rub} RUB ➔ 🇯🇵 {jpy} JPY | 🇰🇷 {krw} KRW"
        elif self.last_edited == 'jpy':
            entry = f"[{time_str}] 🇯🇵 {jpy} JPY ➔ 🇷🇺 {rub} RUB | 🇰🇷 {krw} KRW"
        else:
            entry = f"[{time_str}] 🇰🇷 {krw} KRW ➔ 🇷🇺 {rub} RUB | 🇯🇵 {jpy} JPY"

        self.history_area.append(entry)
        scrollbar = self.history_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())