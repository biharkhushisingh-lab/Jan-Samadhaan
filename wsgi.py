from app import app, init_db
from create_admin import create_admin
from create_department_officials import create_department_officials

# Initialize the database explicitly on startup
# This is required for Render/Gunicorn deployment
print("🚀 WSGI startup: Initializing database...")
init_db()

# Seed database with default users if they don't exist
try:
    print("🌱 WSGI startup: Seeding database...")
    create_admin()
    create_department_officials()
except Exception as e:
    print(f"⚠️ Warning: Database seeding failed: {e}")

if __name__ == "__main__":
    app.run()
