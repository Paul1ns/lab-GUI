import sqlite3

conn = sqlite3.connect('my_base.db')
cursor = conn.cursor()

# Создаем ОДНУ таблицу
cursor.execute('''
CREATE TABLE Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    group_name TEXT,
    grade INTEGER
)
''')

# Добавляем данные
cursor.executemany('INSERT INTO Students (name, group_name, grade) VALUES (?, ?, ?)', [
    ('Иванов Иван', 'ИС-21', 5),
    ('Петрова Мария', 'ИС-21', 4),
    ('Сидоров Алексей', 'ПИ-22', 3)
])

conn.commit()
conn.close()
print("База 'my_base.db' с одной таблицей 'Students' создана!")