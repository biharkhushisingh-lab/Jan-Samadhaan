from db_config import get_db, get_db_cursor, format_sql
import hashlib

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_department_officials():
    officials = [
        # Username, Password, Govt ID, Name, Department, Email, Phone
        ('water@gov.in', 'water123', 'GOV_WATER', 'Water Official', 'Water_Supply_Dept', 'water@gov.in', '9999911111'),
        ('roads@gov.in', 'roads123', 'GOV_ROADS', 'Roads Official', 'Public_Works_Dept', 'roads@gov.in', '9999922222'),
        ('sanitation@gov.in', 'clean123', 'GOV_SANI', 'Sanitation Official', 'Sanitation_Dept', 'sanitation@gov.in', '9999933333'),
        ('power@gov.in', 'power123', 'GOV_POWER', 'Power Official', 'Power_Dept', 'power@gov.in', '9999944444'),
        ('health@gov.in', 'health123', 'GOV_HEALTH', 'Health Official', 'Health_Dept', 'health@gov.in', '9999955555'),
        ('police@gov.in', 'cop123', 'GOV_POLICE', 'Police Official', 'Public_Safety_Dept', 'police@gov.in', '9999966666')
    ]

    conn = get_db()
    cursor = get_db_cursor(conn)
    
    print("🚀 Seeding Department Officials...")
    
    for user in officials:
        username, password, govt_id, name, dept, email, phone = user
        
        # Check if exists
        query_check = format_sql("SELECT * FROM officials WHERE username=?")
        cursor.execute(query_check, (username,))
        exists = cursor.fetchone()
        
        if not exists:
            try:
                query_insert = format_sql('''INSERT INTO officials 
                               (username, password_hash, govt_id, name, department, email, phone) 
                               VALUES (?,?,?,?,?,?,?)''')
                cursor.execute(query_insert,
                            (username, hash_password(password), govt_id, name, dept, email, phone))
                print(f"✅ Created: {name} ({dept}) - User: {username} / Pass: {password}")
            except Exception as e:
                print(f"❌ Failed to create {username}: {e}")
        else:
            print(f"ℹ️  Exists: {name} ({dept})")
            
    conn.commit()
    conn.close()
    print("\n✨ Done! You can now login with these credentials.")

if __name__ == '__main__':
    create_department_officials()
