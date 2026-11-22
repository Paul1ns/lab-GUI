from PyQt5.QtCore import QObject, pyqtSignal

class RubModel(QObject):
    rub_changed = pyqtSignal(float)

    def send_rub(self, value):
        self.rub_changed.emit(value)