import os
import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QRegion, QPainter, QColor


def resource_path(filename):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


class MainWindow(QWidget):
    MAIN_BUTTON_STYLE = (
        "QPushButton {"
        "  background-color: #e6e6e6;"
        "  color: #333333;"
        "  border: 1px solid #c4c4c4;"
        "  border-radius: 20px;"
        "  font-size: 14px;"
        "  font-weight: bold;"
        "}"
        "QPushButton:hover   { background-color: #d6d6d6; }"
        "QPushButton:pressed { background-color: #c0c0c0; }"
    )

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа #1 Буторина 6231")
        self.resize(600, 450)

        self.bg_pixmap = QPixmap(resource_path("image_1.png"))
        self.scaled_bg = QPixmap()

        self.is_image_shown = False
        self.is_shape_changed = False
        self.original_geometry = None
        self.original_flags = self.windowFlags()
        self._drag_pos = None

        self.content = QWidget(self)
        self.content.setGeometry(0, 0, 600, 450)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(25, 15, 25, 0)
        layout.setSpacing(0)

        self.label_container = QWidget(self.content)
        self.label_container.setFixedHeight(200)

        label_container_layout = QVBoxLayout(self.label_container)
        label_container_layout.setContentsMargins(0, 0, 0, 0)
        label_container_layout.setSpacing(0)
        label_container_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.label = QLabel("Нужно что-то выбрать")
        self.label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #333333;"
        )
        self.label.setAlignment(Qt.AlignCenter)
        label_container_layout.addWidget(self.label)

        layout.addWidget(self.label_container)

        layout.addSpacing(25)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        self.btn1 = QPushButton("Вариант 1")
        self.btn1.setFixedSize(140, 40)
        self.btn1.setCursor(Qt.PointingHandCursor)
        self.btn1.setStyleSheet(self.MAIN_BUTTON_STYLE)
        self.btn1.clicked.connect(self.button1_click)

        self.btn2 = QPushButton("Вариант 2")
        self.btn2.setFixedSize(140, 40)
        self.btn2.setCursor(Qt.PointingHandCursor)
        self.btn2.setStyleSheet(self.MAIN_BUTTON_STYLE)
        self.btn2.clicked.connect(self.button2_click)

        btn_layout.addWidget(self.btn1)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn2)

        layout.addLayout(btn_layout)

        layout.addStretch(1)

        self.shape_label = None
        self.close_btn = None
        self.revert_btn = None

        self._update_background()

    def _update_background(self):
        if self.bg_pixmap.isNull():
            self.scaled_bg = QPixmap()
            return
        self.scaled_bg = self.bg_pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.is_shape_changed:
            if not self.scaled_bg.isNull():
                x = (self.width() - self.scaled_bg.width()) // 2
                y = (self.height() - self.scaled_bg.height()) // 2
                painter.drawPixmap(x, y, self.scaled_bg)
            else:
                painter.fillRect(self.rect(), QColor("#f4f4f9"))
        painter.end()

    def resizeEvent(self, event):
        self.content.setGeometry(0, 0, self.width(), self.height())
        self._update_background()
        super().resizeEvent(event)

    def _reset_label_to_text(self):
        self.label.setPixmap(QPixmap())
        self.label.setText("Нужно что-то выбрать")
        self.label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #333333;"
        )
        self.is_image_shown = False

    def button1_click(self):
        if not self.is_image_shown:
            path = resource_path("image.png")
            pixmap = QPixmap(path)
            if pixmap.isNull():
                self.label.setPixmap(QPixmap())
                self.label.setText("Файл image.png не найден")
                self.label.setStyleSheet("font-size: 18px; color: red;")
                print("Не удалось загрузить:", path)
                return
            pixmap = pixmap.scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.label.setText("")
            self.label.setPixmap(pixmap)
            self.is_image_shown = True
        else:
            self._reset_label_to_text()

    def button2_click(self):
        if self.is_image_shown:
            self._reset_label_to_text()

        if not self.is_shape_changed:
            self._enter_shape_mode()
        else:
            self._exit_shape_mode()

    def _enter_shape_mode(self):
        path = resource_path("shape.png")
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Ошибка: не удалось загрузить shape.png по пути:", path)
            return

        pixmap = pixmap.scaled(
            500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        w, h = pixmap.width(), pixmap.height()

        self.original_geometry = self.geometry()
        self.content.hide()

        self.shape_label = QLabel(self)
        self.shape_label.setPixmap(pixmap)
        self.shape_label.setGeometry(0, 0, w, h)
        self.shape_label.setStyleSheet("background: transparent;")
        self.shape_label.show()

        self.close_btn = QPushButton("x", self)
        self.close_btn.setGeometry(w - 40, 10, 30, 30)
        self.close_btn.setStyleSheet(
            "background-color: #ff4d4d; color: white; border: none;"
            "border-radius: 15px; font-weight: bold;"
        )
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.show()
        self.close_btn.raise_()

        self.revert_btn = QPushButton("<-", self)
        self.revert_btn.setGeometry(w - 80, 10, 30, 30)
        self.revert_btn.setStyleSheet(
            "background-color: #4d79ff; color: white; border: none;"
            "border-radius: 15px; font-weight: bold;"
        )
        self.revert_btn.setCursor(Qt.PointingHandCursor)
        self.revert_btn.clicked.connect(self._exit_shape_mode)
        self.revert_btn.show()
        self.revert_btn.raise_()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(200, 200, w, h)
        self.show()

        self._apply_shape_mask(pixmap)

        self.is_shape_changed = True
        self.update()

    def _exit_shape_mode(self):
        if self.shape_label:
            self.shape_label.deleteLater()
            self.shape_label = None
        if self.close_btn:
            self.close_btn.deleteLater()
            self.close_btn = None
        if self.revert_btn:
            self.revert_btn.deleteLater()
            self.revert_btn = None

        self.clearMask()
        self.setWindowFlags(self.original_flags)
        self.setGeometry(self.original_geometry)
        self.content.show()
        self.show()

        self.is_shape_changed = False
        self.update()

    def _apply_shape_mask(self, pixmap):
        image = pixmap.toImage()
        if image.hasAlphaChannel():
            mask = pixmap.mask()
        else:
            bg_color = image.pixelColor(0, 0)
            mask = pixmap.createMaskFromColor(bg_color, Qt.MaskInColor)

        region = QRegion(mask)
        if self.close_btn:
            region = region.united(QRegion(self.close_btn.geometry()))
        if self.revert_btn:
            region = region.united(QRegion(self.revert_btn.geometry()))

        self.setMask(region)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self.is_shape_changed and event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if (self.is_shape_changed
                and self._drag_pos is not None
                and event.buttons() & Qt.LeftButton):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())