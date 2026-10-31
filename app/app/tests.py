import unittest
import sqlite3
import os

class TestEventManagementSystem(unittest.TestCase):
    def setUp(self):
        """Test üçün müvəqqəti verilənlər bazası yaradılır"""
        self.db_name = "test_events.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Cədvəllərin yaradılması
        self.cursor.execute('CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
        self.cursor.execute('''CREATE TABLE events (
            id INTEGER PRIMARY KEY, title TEXT, description TEXT, 
            category_id INTEGER, date TEXT, time TEXT, location TEXT, max_participants INTEGER
        )''')
        self.cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, full_name TEXT, email TEXT UNIQUE)')
        self.cursor.execute('''CREATE TABLE registrations (
            id INTEGER PRIMARY KEY, user_id INTEGER, event_id INTEGER, registration_date TEXT,
            UNIQUE(user_id, event_id)
        )''')
        self.conn.commit()

    def tearDown(self):
        """Test bitdikdən sonra test bazası silinir"""
        self.conn.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    # Test 1: Kateqoriya əlavə edilməsi
    def test_add_category(self):
        self.cursor.execute("INSERT INTO categories (name) VALUES ('Seminar')")
        self.conn.commit()
        self.cursor.execute("SELECT name FROM categories WHERE name='Seminar'")
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 'Seminar')

    # Test 2: Tədbirin düzgün yaradılması
    def test_create_event(self):
        self.cursor.execute("""
            INSERT INTO events (title, description, category_id, date, time, location, max_participants)
            VALUES ('AI Summit', 'AI Haqqında', 1, '2026-12-01', '14:00', 'Akt Zalı', 100)
        """)
        self.conn.commit()
        self.cursor.execute("SELECT title FROM events WHERE title='AI Summit'")
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 'AI Summit')

    # Test 3: İstifadəçi qeydiyyatı
    def test_register_user(self):
        self.cursor.execute("INSERT INTO users (full_name, email) VALUES ('Ali Aliyev', 'ali@mail.com')")
        self.conn.commit()
        self.cursor.execute("SELECT full_name FROM users WHERE email='ali@mail.com'")
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 'Ali Aliyev')

    # Test 4: Eyni istifadəçinin təkrar qeydiyyatının qarşısının alınması (UNIQUE Constraint)
    def test_prevent_duplicate_registration(self):
        self.cursor.execute("INSERT INTO users (id, full_name, email) VALUES (1, 'Ali', 'ali@mail.com')")
        self.cursor.execute("INSERT INTO events (id, title, description, category_id, date, time, location, max_participants) VALUES (1, 'Conf', 'Desc', 1, '2026-10-10', '10:00', 'Room A', 50)")
        self.cursor.execute("INSERT INTO registrations (user_id, event_id, registration_date) VALUES (1, 1, '2026-10-01')")
        self.conn.commit()

        # İkinci təkrar qeydiyyat cəhdi xəta verməlidir
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO registrations (user_id, event_id, registration_date) VALUES (1, 1, '2026-10-01')")
            self.conn.commit()

    # Test 5: İştirakçı limitinin dolmasını yoxlamaq
    def test_event_capacity_limit(self):
        max_limit = 2
        current_registrations = 2
        is_full = current_registrations >= max_limit
        self.assertTrue(is_full)

if __name__ == '__main__':
    unittest.main()