from PyQt5.QtCore import QObject, pyqtSignal

class JpyModel(QObject):
    jpy_changed = pyqtSignal(float)

    def send_jpy(self, value):
        self.jpy_changed.emit(value)