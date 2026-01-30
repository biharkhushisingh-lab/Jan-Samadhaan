# 🚀 Quick Setup Guide - Get Your Project Running

## Step 1: Install Dependencies

```bash
cd c:\Users\nisha\Downloads\antidep\egrievance_project
pip install -r requirements.txt
```

## Step 2: Get Your FREE Google Gemini API Key

1. **Go to**: https://aistudio.google.com/
2. **Sign in** with your Google account
3. **Click "Get API Key"** button (top right)
4. **Click "Create API key in new project"**
5. **Copy the API key** - looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

> [!TIP]
> The API key is **completely FREE** with 60 requests per minute!

## Step 3: Create Your .env File

**IMPORTANT**: Your `.env` file is protected by gitignore (it won't be uploaded to GitHub). You need to create it manually.

1. **Copy the example file**:
   ```bash
   copy .env.example .env
   ```

2. **Edit the `.env` file** with your actual credentials:
   ```
   # Leave empty for SQLite (local development)
   # DATABASE_URL=

   # Your email configuration (already set from your code)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=nishantjha0070032@gmail.com
   SENDER_PASSWORD=xbjhiulvodwgsmfo
   SENDER_NAME=Bharat E-Grievance System

   # Paste your Gemini API key here
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

## Step 4: Test Everything

```bash
# Test database connection
python db_config.py

# Start the application
python bpp.py
```

You should see:
```
✅ Google Gemini AI initialized
✅ Database initialized (SQLite)
📧 Email: ✅ Configured
🇮🇳 BHARAT E-GRIEVANCE SYSTEM
🔗 http://127.0.0.1:5000
```

## Step 5: Test AI Features

1. Open http://127.0.0.1:5000 in your browser
2. Submit a test complaint
3. Check the console - you should see:
   ```
   ✅ Gemini AI Analysis: Priority=X, Dept=XXXX
   ```

---

## ⚡ Summary of Changes Made

### Security Fixes ✅
- ✅ **Email credentials** moved to `.env` file (no longer hardcoded)
- ✅ **API keys** loaded from environment variables
- ✅ **`.gitignore`** already protecting sensitive files

### AI Features ✅
- ✅ **Google Gemini AI** integrated (free alternative to Anthropic)
- ✅ **Automatic fallback** to keyword analysis if API fails
- ✅ **Smart department routing** using AI

### Configuration ✅
- ✅ **python-dotenv** added for environment variable management
- ✅ **`.env.example`** updated with all required variables
- ✅ **Application startup** now shows AI and email status

---

## 🎯 Next Steps

1. Get your Gemini API key from https://aistudio.google.com/
2. Create and configure your `.env` file
3. Run the application and test!

## 🆘 Troubleshooting

**No AI detected?**
- Make sure `GEMINI_API_KEY` is set in your `.env` file
- Verify you installed dependencies: `pip install -r requirements.txt`

**Email not sending?**
- Check that `SENDER_EMAIL` and `SENDER_PASSWORD` are set in `.env`
- For Gmail, use an App Password (not your regular password)

**Database errors?**
- Run `python db_config.py` to initialize tables
- Check that `grievance.db` file is created
