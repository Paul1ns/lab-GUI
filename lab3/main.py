import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QComboBox, QTabWidget, 
                             QTableView, QFileDialog, QMessageBox, QAction, 
                             QDialog, QTextEdit, QLabel)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа #3 Буторина 6231")
        self.resize(900, 600)
        self.db = None
        self.models = [] 
        self.main_table_name = "Students" 

        self.init_ui()
        self.create_menu()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        
        self.btn1 = QPushButton('"SELECT name"')
        self.btn1.clicked.connect(self.bt1_click)
        
        self.combo = QComboBox()
        self.combo.setMinimumWidth(150)
        self.combo.currentTextChanged.connect(self.combo_changed)
        
        self.btn3 = QPushButton('"Filter"')
        self.btn3.clicked.connect(self.bt3_click)

        self.btn4 = QPushButton('"Aggregation"')
        self.btn4.clicked.connect(self.bt4_click)

        top_layout.addWidget(self.btn1)
        top_layout.addWidget(self.combo)
        top_layout.addWidget(self.btn3)
        top_layout.addWidget(self.btn4)
        
        main_layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        self.tables = [] 
        
        for i in range(1, 7):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            table_view = QTableView()
            tab_layout.addWidget(table_view)
            self.tables.append(table_view)
            self.tabs.addTab(tab, f"Tab{i}")

        main_layout.addWidget(self.tabs)
        
        self.set_controls_enabled(False)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("☰ Menu")

        connect_action = QAction("Set connection", self)
        connect_action.triggered.connect(self.open_db)
        file_menu.addAction(connect_action)

        close_action = QAction("Close connection", self)
        close_action.triggered.connect(self.close_db)
        file_menu.addAction(close_action)
        
        custom_query_action = QAction("Custom SQL Query", self)
        custom_query_action.triggered.connect(self.open_custom_query_dialog)
        file_menu.addAction(custom_query_action)

    def set_controls_enabled(self, enabled):
        self.btn1.setEnabled(enabled)
        self.combo.setEnabled(enabled)
        self.btn3.setEnabled(enabled)
        self.btn4.setEnabled(enabled)

    
    def open_db(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл базы данных SQLite", "", "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if not file_name:
            return

        if self.db:
            self.close_db()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(file_name)

        if not self.db.open():
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД:\n{self.db.lastError().text()}")
            return

        QMessageBox.information(self, "Успех", "Соединение с БД установлено!")
        self.set_controls_enabled(True)
        
        self.execute_query("SELECT * FROM sqlite_master", 0)
        self.prepare_combobox()

    def prepare_combobox(self):
        self.combo.blockSignals(True)
        self.combo.clear()
        
        pragma_query = QSqlQuery(self.db)
        pragma_query.exec_(f"PRAGMA table_info({self.main_table_name})")
        
        while pragma_query.next():
            col_name = pragma_query.value(1) 
            self.combo.addItem(col_name)
            
        self.combo.setCurrentIndex(-1) 
        self.combo.blockSignals(False)

    def close_db(self):
        if self.db:
            self.db.close()
            self.db = None
            QSqlDatabase.removeDatabase(QSqlDatabase.database().connectionName())
            
            for table in self.tables:
                table.setModel(None)
            self.models.clear()
            self.combo.clear()
            
            self.set_controls_enabled(False)
            QMessageBox.information(self, "Инфо", "Соединение закрыто, данные очищены.")

    def execute_query(self, query_str, tab_index):
        if not self.db or not self.db.isOpen():
            return

        model = QSqlQueryModel(self)
        model.setQuery(query_str, self.db)

        if model.lastError().isValid():
            QMessageBox.warning(self, "Ошибка SQL", model.lastError().text())
            return

        self.models.append(model)
        self.tables[tab_index].setModel(model)
        self.tabs.setCurrentIndex(tab_index)

    
    def bt1_click(self):
        self.execute_query(f"SELECT name FROM {self.main_table_name}", 1)

    def combo_changed(self, column_name):
        if not column_name or not self.db:
            return
        query = f"SELECT {column_name} FROM {self.main_table_name}"
        self.execute_query(query, 2)

    def bt3_click(self):
        query = f"SELECT * FROM {self.main_table_name} WHERE grade = 5"
        self.execute_query(query, 3)

    def bt4_click(self):
        query = f"""
            SELECT group_name, 
                   COUNT(*) as total_students, 
                   AVG(grade) as average_grade 
            FROM {self.main_table_name} 
            GROUP BY group_name
        """
        self.execute_query(query, 4)

    
    def open_custom_query_dialog(self):
        if not self.db or not self.db.isOpen():
            QMessageBox.warning(self, "Внимание", "Сначала подключитесь к базе данных!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Выполнить свой SQL-запрос")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Введите SQL запрос (результат появится в Tab6):"))
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("SELECT * FROM Students;")
        layout.addWidget(text_edit)
        
        btn_run = QPushButton("Выполнить")
        layout.addWidget(btn_run)
        
        def run_query():
            query_str = text_edit.toPlainText().strip()
            if not query_str:
                return
            
            temp_model = QSqlQueryModel()
            temp_model.setQuery(query_str, self.db)
            
            if temp_model.lastError().isValid():
                QMessageBox.critical(dialog, "Ошибка", "Ошибка запроса! Проверьте запрос и попробуйте еще раз.")
                return 
                
            self.execute_query(query_str, 5)
            dialog.accept()
                
        btn_run.clicked.connect(run_query)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not QSqlDatabase.isDriverAvailable("QSQLITE"):
        QMessageBox.critical(None, "Ошибка", "Драйвер QSQLITE не найден в системе!")
        sys.exit(1)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())