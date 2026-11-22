import os
import sys
import base64

from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Interface(QObject):
    def __init__(self):
        super().__init__()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._save_path = os.path.join(base_dir, "canvas_autosave.png")
        self._save_count = 0
        print(f"[autosave] файл будет сохраняться в: {self._save_path}")

    @pyqtSlot(str)
    def saveCanvas(self, data_url):
        """
        Вызывается из QML по таймеру.
        data_url имеет формат: 'data:image/png;base64,<...>' (или base64 без префикса).
        """
        if not data_url:
            return
        try:
            if data_url.startswith("data:"):
                # отрезаем префикс "data:image/png;base64,"
                _, b64 = data_url.split(",", 1)
            else:
                b64 = data_url

            raw = base64.b64decode(b64)
            if not raw:
                return

            with open(self._save_path, "wb") as f:
                f.write(raw)

            self._save_count += 1
            print(f"[autosave] #{self._save_count} -> "
                  f"{self._save_path} ({len(raw)} байт)")
        except Exception as e:
            print(f"[autosave] ошибка сохранения: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    interface = Interface()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    qml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mainWindow.qml",
    )
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    sys.exit(app.exec())