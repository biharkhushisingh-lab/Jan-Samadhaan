# 🚀 How to Deploy on Render with PostgreSQL

## Step 1: Get Your PostgreSQL Credentials from Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your PostgreSQL database** (the one you already created)
3. **Scroll down to "Connections"** section
4. **Copy the "External Database URL"** - it looks like:
   ```
   postgresql://username:password@host:port/database_name
   ```
   Example:
   ```
   postgresql://myuser:abc123xyz@dpg-abc123-a.oregon-postgres.render.com/mydb
   ```

## Step 2: Set Up Your Project Locally

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   copy .env.example .env
   ```

3. **Edit `.env` file** and paste your DATABASE_URL:
   ```
   DATABASE_URL=postgresql://your_actual_url_from_render
   ```

4. **Test database connection**:
   ```bash
   python db_config.py
   ```
   You should see: ✅ Connection successful!

5. **Initialize the database**:
   ```bash
   python bpp.py
   ```
   This will create the necessary tables in PostgreSQL.

## Step 3: Deploy to Render

### Method 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "PostgreSQL migration"
   git remote add origin https://github.com/yourusername/yourrepo.git
   git push -u origin main
   ```

2. **Create Web Service on Render**:
   - Go to Render Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Fill in:
     - **Name**: `bharat-egrievance` (or any name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Add Environment Variable**:
   - In Render Web Service settings → "Environment"
   - Click "Add Environment Variable"
   - **Key**: `DATABASE_URL`
   - **Value**: Your PostgreSQL URL from Step 1
   - Click "Save Changes"

4. **Deploy**: Click "Create Web Service"

### Method 2: Deploy Manually (Without GitHub)

1. Install **Render CLI** or use the Render web interface
2. Follow the same steps as Method 1 but upload files manually

## Step 4: Initialize Database Tables on Render

After deployment, you need to create the tables:

1. **Go to Render Dashboard** → Your Web Service → "Shell"
2. **Run**:
   ```bash
   python db_config.py
   ```
   This creates the tables in your PostgreSQL database.

3. **Add test officials** (optional):
   ```bash
   python setup_emails.py
   ```

## Step 5: Access Your Deployed App

Your app will be available at:
```
https://your-app-name.onrender.com
```

## Troubleshooting

### Database Connection Error
- ✅ Check that `DATABASE_URL` is set correctly in Render environment variables
- ✅ Make sure the PostgreSQL database is running (green status in Render)
- ✅ Verify the URL format: `postgresql://` (not `postgres://`)

### Tables Not Created
- Run `python db_config.py` in the Render Shell to initialize

### App Won't Start
- Check logs in Render Dashboard
- Ensure `requirements.txt` is installed properly
- Verify start command is: `gunicorn app:app`

## Local Development vs Production

-   **Local**: Uses SQLite automatically (if no `DATABASE_URL` set)
-   **Production**: Uses PostgreSQL (when `DATABASE_URL` is set in Render)

This means you can develop locally without PostgreSQL and deploy with PostgreSQL!

## Important Files

- `db_config.py` - Database configuration (auto-detects PostgreSQL or SQLite)
- `bpp.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `.env` - Local environment variables (DON'T commit to Git!)
- `.env.example` - Template for environment variables

## Security Notes

⚠️ **NEVER commit `.env` file to Git!**

Add to `.gitignore`:
```
.env
*.db
__pycache__/
uploads/
```

---

🎉 **You're all set!** Your E-Grievance system is now ready for deployment on Render with PostgreSQL.
