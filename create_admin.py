from db_config import get_db, get_db_cursor, format_sql
import hashlib

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_admin():
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        
        # Check if exists using parameterized query
        print("🔍 Checking if admin exists...")
        query_check = format_sql("SELECT * FROM officials WHERE username=?", conn)
        cursor.execute(query_check, ('admin@gov.in',))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing admin to ensure credentials match latest list
            print(f"🔄 Updating existing admin: admin@gov.in")
            query_update = format_sql("UPDATE officials SET password_hash = ?, govt_id = ?, name = ?, department = ?, email = ?, phone = ? WHERE username = ?", conn)
            cursor.execute(query_update, (hash_password('admin123'), 'GOV123', 'System Admin', 'General_Admin_Dept', 'admin@gov.in', '9876543210', 'admin@gov.in'))
            conn.commit()
            print("✅ Admin user credentials force-reset successfully")
        else:
            print("🆕 Creating new admin: admin@gov.in")
            query_insert = format_sql('''INSERT INTO officials 
                           (username, password_hash, govt_id, name, department, email, phone) 
                           VALUES (?,?,?,?,?,?,?)''', conn)
            cursor.execute(query_insert,
                        ('admin@gov.in', hash_password('admin123'), 'GOV123', 
                         'System Admin', 'General_Admin_Dept', 'admin@gov.in', '9876543210'))
            conn.commit()
            print("✅ Admin user created successfully")
        conn.close()
    except Exception as e:
        print(f"❌ Error in create_admin: {e}")

if __name__ == '__main__':
    create_admin()
