from db_config import get_db
import hashlib

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_admin():
    try:
        conn = get_db()
        # Check if exists
        exists = conn.execute("SELECT * FROM officials WHERE username='admin@gov.in'").fetchone()
        if not exists:
            conn.execute('''INSERT INTO officials 
                           (username, password_hash, govt_id, name, department, email, phone) 
                           VALUES (?,?,?,?,?,?,?)''',
                        ('admin@gov.in', hash_password('admin123'), 'GOV123', 
                         'System Admin', 'General_Admin_Dept', 'admin@gov.in', '9876543210'))
            conn.commit()
            print("✅ Admin user created successfully")
            print("Username: admin@gov.in")
            print("Password: admin123")
            print("Govt ID: GOV123")
        else:
            print("ℹ️ Admin user already exists")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_admin()
