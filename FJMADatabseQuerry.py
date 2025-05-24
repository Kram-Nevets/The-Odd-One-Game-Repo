import sqlite3
import bcrypt
from tabulate import tabulate
import datetime

conn = sqlite3.connect("UISYS/fjma_system.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_credentials (
        username TEXT PRIMARY KEY,
        password BLOB NOT NULL,
        email TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS officers (
        school_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        middle_name TEXT,
        last_name TEXT NOT NULL,
        position TEXT NOT NULL,
        date_appointed TEXT NOT NULL,
        date_joined TEXT NOT NULL,
        email_address TEXT NOT NULL,
        phone_number TEXT NOT NULL
    )
""")

# Archive table for officers
cursor.execute("""
    CREATE TABLE IF NOT EXISTS officers_archive (
        school_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        middle_name TEXT,
        last_name TEXT NOT NULL,
        position TEXT NOT NULL,
        date_appointed TEXT NOT NULL,
        date_joined TEXT NOT NULL,
        email_address TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        deleted_at TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        school_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        middle_name TEXT,
        last_name TEXT NOT NULL,
        year_level TEXT NOT NULL,
        section TEXT NOT NULL,
        email_address TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        tribe TEXT NOT NULL
    )
""")

# Archive table for members
cursor.execute("""
    CREATE TABLE IF NOT EXISTS members_archive (
        school_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        middle_name TEXT,
        last_name TEXT NOT NULL,
        year_level TEXT NOT NULL,
        section TEXT NOT NULL,
        email_address TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        tribe TEXT NOT NULL,
        deleted_at TEXT NOT NULL
    )
""")

#tribes tables

tribes = ["larab", "makani", "lawod", "lasang"]

for tribe in tribes:
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {tribe}_members (
            school_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            year_level TEXT NOT NULL,
            section TEXT NOT NULL,
            email_address TEXT NOT NULL,
            phone_number TEXT NOT NULL
        )
    """)

#archive taBLE
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {tribe}_members_archive (
            school_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            year_level TEXT NOT NULL,
            section TEXT NOT NULL,
            email_address TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            deleted_at TEXT NOT NULL
        )
    """)

#Password hashing with bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

#Admin CRUD with bcrypt

def add_admin(username, password, email):
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO login_credentials (username, password, email) VALUES (?, ?, ?)",
                   (username, hashed_password, email))
    conn.commit()

def view_admins():
    cursor.execute("SELECT username, email FROM login_credentials")
    rows = cursor.fetchall()
    print(tabulate(rows, headers=["Username", "Email"], tablefmt="fancy_grid"))

def update_admin(username, new_password=None, new_email=None):
    if new_password:
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE login_credentials SET password=? WHERE username=?", (hashed_password, username))
    if new_email:
        cursor.execute("UPDATE login_credentials SET email=? WHERE username=?", (new_email, username))
    conn.commit()

def delete_admin(username):
    cursor.execute("DELETE FROM login_credentials WHERE username=?", (username,))
    conn.commit()

def authenticate_admin(username, password):
    cursor.execute("SELECT password FROM login_credentials WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        stored_hash = result[0]
        if verify_password(password, stored_hash):
            return True
    return False

# Officers CRUD with archive on delete

def add_officer(school_id, first_name, middle_name, last_name, position, date_appointed, date_joined, email_address, phone_number):
    cursor.execute("""
        INSERT INTO officers (school_id, first_name, middle_name, last_name, position, date_appointed, date_joined, email_address, phone_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (school_id, first_name, middle_name, last_name, position, date_appointed, date_joined, email_address, phone_number))
    conn.commit()

def view_officers():
    cursor.execute("""
        SELECT school_id, first_name, middle_name, last_name, position, date_appointed, date_joined, email_address, phone_number
        FROM officers
    """)
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[
        "School ID", "First Name", "Middle Name", "Last Name", "Position",
        "Date Appointed", "Date Joined", "Email", "Phone"
    ], tablefmt="fancy_grid"))

def update_officer(school_id, first_name, middle_name, last_name, position, date_appointed, date_joined, email_address, phone_number):
    cursor.execute("""
        UPDATE officers
        SET first_name=?, middle_name=?, last_name=?, position=?, date_appointed=?, date_joined=?, email_address=?, phone_number=?
        WHERE school_id=?
    """, (first_name, middle_name, last_name, position, date_appointed, date_joined, email_address, phone_number, school_id))
    conn.commit()

def delete_officer(school_id):
    cursor.execute("SELECT * FROM officers WHERE school_id=?", (school_id,))
    record = cursor.fetchone()
    if record:
        deleted_at = datetime.datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO officers_archive (
                school_id, first_name, middle_name, last_name, position,
                date_appointed, date_joined, email_address, phone_number, deleted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, record + (deleted_at,))
        cursor.execute("DELETE FROM officers WHERE school_id=?", (school_id,))
        conn.commit()

#Members CRUD with tribe insertion and archive on delete

def add_member(school_id, first_name, middle_name, last_name, year_level, section, email_address, phone_number, tribe):
    valid_tribes = ['Larab', 'Makani', 'Lawod', 'Lasang']
    if tribe.capitalize() not in valid_tribes:
        print("Invalid tribe. Must be one of: Larab, Makani, Lawod, Lasang")
        return
    cursor.execute("""
        INSERT INTO members (school_id, first_name, middle_name, last_name, year_level, section, email_address, phone_number, tribe)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (school_id, first_name, middle_name, last_name, year_level, section, email_address, phone_number, tribe))
    
    tribe_table = tribe.lower() + "_members"
    cursor.execute(f"""
        INSERT INTO {tribe_table} (school_id, first_name, middle_name, last_name, year_level, section, email_address, phone_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (school_id, first_name, middle_name, last_name, year_level, section, email_address, phone_number))
    
    conn.commit()

def view_members():
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    print(tabulate(rows, headers=[
        "School ID", "First Name", "Middle Name", "Last Name",
        "Year Level", "Section", "Email", "Phone", "Tribe"
    ], tablefmt="fancy_grid"))

def delete_member(school_id):
    cursor.execute("SELECT * FROM members WHERE school_id=?", (school_id,))
    record = cursor.fetchone()
    if record:
        deleted_at = datetime.datetime.now().isoformat()
        tribe = record[8]  # tribe column
        # Archive member
        cursor.execute("""
            INSERT INTO members_archive (
                school_id, first_name, middle_name, last_name, year_level, section,
                email_address, phone_number, tribe, deleted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, record + (deleted_at,))

        # Archive tribe member and delete from tribe table
        tribe_table = tribe.lower() + "_members"
        tribe_archive_table = tribe.lower() + "_members_archive"

        cursor.execute(f"SELECT * FROM {tribe_table} WHERE school_id=?", (school_id,))
        tribe_record = cursor.fetchone()
        if tribe_record:
            cursor.execute(f"""
                INSERT INTO {tribe_archive_table} (
                    school_id, first_name, middle_name, last_name, year_level, section,
                    email_address, phone_number, deleted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tribe_record + (deleted_at,))
            cursor.execute(f"DELETE FROM {tribe_table} WHERE school_id=?", (school_id,))

        # Delete member record
        cursor.execute("DELETE FROM members WHERE school_id=?", (school_id,))
        conn.commit()

#add_admin("admin","admin123","admin123@gmail.com") initial admin credentials


