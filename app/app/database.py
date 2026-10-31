import pyodbc
from config import DB_DRIVER, DB_NAME, DB_SERVER


def create_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"Trusted_Connection=yes;"
        )
        return conn
    except Exception as err:
        print(f"Database əlaqə xətası: {err}")
        return None


def add_student(name: str, score: float) -> bool:
    conn = create_connection()
    if not conn:
        return False

    query = "INSERT INTO Students (Name, Score) VALUES (?, ?)"
    try:
        cursor = conn.cursor()
        cursor.execute(query, (name, score))
        conn.commit()
        return True
    except Exception as err:
        print(f"Tələbə əlavə edilərkən xəta: {err}")
        return False
    finally:
        conn.close()


def get_students() -> list:
    conn = create_connection()
    if not conn:
        return []

    query = "SELECT Id, Name, Score FROM Students ORDER BY Id DESC"
    students = []
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            students.append({"id": row.Id, "name": row.Name, "score": float(row.Score)})
    except Exception as err:
        print(f"Məlumatlar çəkilərkən xəta: {err}")
    finally:
        conn.close()

    return students


def get_student(search_query: str) -> list:
    conn = create_connection()
    if not conn:
        return []

    query = "SELECT Id, Name, Score FROM Students WHERE Name LIKE ? ORDER BY Id DESC"
    students = []
    try:
        cursor = conn.cursor()
        cursor.execute(query, (f"%{search_query}%",))
        rows = cursor.fetchall()
        for row in rows:
            students.append({"id": row.Id, "name": row.Name, "score": float(row.Score)})
    except Exception as err:
        print(f"Axtarış xətası: {err}")
    finally:
        conn.close()

    return students