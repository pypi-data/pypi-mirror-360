import random
import sqlite3
import zipfile
import tempfile
import os
import importlib.resources as pkg_resources
import mnk_persian_words.data

def extract_db():
    temp_dir = tempfile.gettempdir()
    extract_path = os.path.join(temp_dir, 'words.db')

    # اگر فایل دیتابیس از قبل وجود داشت، همان را برگردان
    if os.path.exists(extract_path):
        return extract_path

    # در غیر این صورت، فایل فشرده را استخراج کن
    with pkg_resources.files(mnk_persian_words.data, 'words.db.zip') as zip_path:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract('words.db', temp_dir)
    return extract_path

def connect_db():
    db_path = extract_db()
    import sqlite3
    conn = sqlite3.connect(db_path)
    return conn

words = []

def load_words_from_db(db_path: str = "words.db", table_name: str = "words") -> list[str]:
    global words
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"SELECT word FROM {table_name}")
        words = [row[0] for row in cur.fetchall()]
        print(f"✅ {len(words)} کلمه از دیتابیس خوانده شد.")
    except sqlite3.Error as e:
        print(f"❌ خطا در ارتباط با دیتابیس: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_random_persian_word(words_count: int = 1) -> str:
    if not words:
        return "⚠️ لیست کلمات خالی است."
    return ' '.join(random.choices(words, k=words_count))

def get_random_persian_paragraph(words_count: int = 5, paragraphs: int = 1) -> str:
    if not words:
        return "⚠️ لیست کلمات خالی است."
    all_paragraphs = []
    for _ in range(paragraphs):
        para = ' '.join(random.choices(words, k=words_count))
        all_paragraphs.append(para)
    return '\n'.join(all_paragraphs)

# اگر بخوای تست کنی:
if __name__ == "__main__":
    load_words_from_db("words.db", "words")  # مسیر دیتابیس و نام جدول
    print(get_random_persian_word(3))
    print("---")
    print(get_random_persian_paragraph(5, 2))
