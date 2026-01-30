"""
Database Configuration Module
Supports both PostgreSQL (for deployment) and SQLite (for local development)
"""

import os
import sqlite3
from urllib.parse import urlparse

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 not installed. Using SQLite fallback.")
    print("   For PostgreSQL support, run: pip install psycopg2-binary")

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')  # From Render or other hosting
SQLITE_DB = 'grievance.db'  # Fallback local database

def get_db():
    """
    Get database connection - PostgreSQL if available, otherwise SQLite
    """
    if DATABASE_URL and POSTGRES_AVAILABLE:
        # Use PostgreSQL from environment
        try:
            # Parse DATABASE_URL if it starts with postgres://
            db_url = DATABASE_URL
            if db_url.startswith('postgres://'):
                # Render uses postgres:// but psycopg2 needs postgresql://
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(db_url)
            conn.row_factory = RealDictCursor  # Return rows as dictionaries
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            print("   Falling back to SQLite...")
            # Fall through to SQLite
    
    # Use SQLite (local development or fallback)
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def is_postgres():
    """Check if currently using PostgreSQL"""
    return DATABASE_URL and POSTGRES_AVAILABLE

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Complaints table (with new fields)
        cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            citizen_name TEXT,
            citizen_email TEXT,
            citizen_phone TEXT,
            citizen_address TEXT,
            category TEXT,
            description TEXT,
            media_path TEXT,
            latitude REAL,
            longitude REAL,
            location_address TEXT,
            priority INTEGER,
            department TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT,
            resolved_at TEXT,
            sla_hours INTEGER,
            sla_deadline TEXT,
            resolution_summary TEXT,
            resolution_proof TEXT,
            citizen_feedback_rating INTEGER,
            citizen_feedback_comments TEXT,
            ai_analysis TEXT,
            citizen_language TEXT DEFAULT 'en',
            description_original TEXT,
            description_translated TEXT,
            rejection_reason TEXT,
            transfer_count INTEGER DEFAULT 0
        )''')
        
        # Citizens table (new)
        cursor.execute('''CREATE TABLE IF NOT EXISTS citizens (
            id SERIAL PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            address TEXT,
            created_at TEXT,
            last_login TEXT
        )''' if is_postgres() else '''CREATE TABLE IF NOT EXISTS citizens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            address TEXT,
            created_at TEXT,
            last_login TEXT
        )''')
        
        # OTPs table (new)
        cursor.execute('''CREATE TABLE IF NOT EXISTS otps (
            id SERIAL PRIMARY KEY,
            phone TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            purpose TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used BOOLEAN DEFAULT false
        )''' if is_postgres() else '''CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            purpose TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )''')
        
        # Complaint transfers table (new)
        cursor.execute('''CREATE TABLE IF NOT EXISTS complaint_transfers (
            id SERIAL PRIMARY KEY,
            complaint_id TEXT NOT NULL,
            from_department TEXT,
            to_department TEXT NOT NULL,
            transferred_by TEXT,
            transfer_reason TEXT,
            transferred_at TEXT NOT NULL
        )''' if is_postgres() else '''CREATE TABLE IF NOT EXISTS complaint_transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT NOT NULL,
            from_department TEXT,
            to_department TEXT NOT NULL,
            transferred_by TEXT,
            transfer_reason TEXT,
            transferred_at TEXT NOT NULL
        )''')
        
        # Officials table
        cursor.execute('''CREATE TABLE IF NOT EXISTS officials (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            govt_id TEXT UNIQUE,
            name TEXT,
            department TEXT,
            email TEXT,
            phone TEXT,
            preferred_language TEXT DEFAULT 'en'
        )''' if is_postgres() else '''CREATE TABLE IF NOT EXISTS officials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            govt_id TEXT UNIQUE,
            name TEXT,
            department TEXT,
            email TEXT,
            phone TEXT,
            preferred_language TEXT DEFAULT 'en'
        )''')
        
        # Try to add new columns to existing complaints table (for migration)
        try:
            cursor.execute("ALTER TABLE complaints ADD COLUMN rejection_reason TEXT")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE complaints ADD COLUMN transfer_count INTEGER DEFAULT 0")
        except:
            pass  # Column already exists
        
        conn.commit()
        print(f"✅ Database initialized ({'PostgreSQL' if is_postgres() else 'SQLite'})")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_db_info():
    """Get current database information"""
    if is_postgres():
        parsed = urlparse(DATABASE_URL)
        return {
            'type': 'PostgreSQL',
            'host': parsed.hostname,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username
        }
    else:
        return {
            'type': 'SQLite',
            'database': SQLITE_DB
        }

if __name__ == '__main__':
    # Test database connection
    print("=" * 60)
    print("🔍 Testing Database Connection")
    print("=" * 60)
    
    info = get_db_info()
    print(f"\n📊 Database Type: {info['type']}")
    
    if info['type'] == 'PostgreSQL':
        print(f"🗄️  Database: {info['database']}")
        print(f"🖥️  Host: {info['host']}")
        print(f"👤 User: {info['user']}")
    else:
        print(f"📁 File: {info['database']}")
    
    try:
        conn = get_db()
        print("\n✅ Connection successful!")
        conn.close()
        
        print("\n🔨 Initializing tables...")
        init_db()
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
    
    print("=" * 60)
