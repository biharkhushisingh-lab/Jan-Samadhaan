# Quick Start: Get PostgreSQL Credentials from Render

## 📋 Step-by-Step Guide

### 1. Go to Render Dashboard
🔗 https://dashboard.render.com

### 2. Find Your PostgreSQL Database
- Look in your dashboard for the PostgreSQL database you created
- Click on it to open

### 3. Get the Database URL
Scroll down to the **"Connections"** section. You'll see:

#### Internal Database URL
```
postgresql://internal-url...
```
⚠️ Don't use this one!

#### External Database URL
```
postgresql://username:password@dpg-xxxxx.region.render.com/database_name
```
✅ **Copy this entire URL!** This is what you need.

### 4. Example of What You'll Copy
```
postgresql://egrievance_user:Abc123xyz456@dpg-cr1234abcd-a.oregon-postgres.render.com/egrievance_db
```

---

## ⚙️ How to Use It

### For Local Testing:
1. Create file named `.env` in your project folder
2. Add this line (paste YOUR actual URL):
   ```
   DATABASE_URL=postgresql://your_actual_url_here
   ```

### For Render Deployment:
1. Go to your Render **Web Service** (when you create it)
2. Go to **Environment** tab
3. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://your_actual_url_here`

---

## ✅ That's it!
Your app will automatically detect and use PostgreSQL when it sees this `DATABASE_URL` variable.

## 🧪 Test Your Connection
Run this command to test:
```bash
python db_config.py
```

You should see: ✅ Connection successful!
