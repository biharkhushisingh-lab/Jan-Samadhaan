# API Keys Setup Guide

This project requires several API keys to function. Follow these instructions to set them up safely.

## Required API Keys

### 1. Google Maps API Key

**Used in**: `index.html`, `official.html`

**Setup Steps**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. Create a new project or select existing one
3. Enable "Maps JavaScript API" and "Places API"
4. Create API key in "Credentials"
5. **IMPORTANT**: Restrict the API key:
   - Application restrictions: HTTP referrers
   - Add your website URL (e.g., `https://yoursite.com/*`)
   - API restrictions: Limit to Maps JavaScript API and Places API

**How to use**:
- Open `index.html` and `official.html`
- Find: `key=YOUR_GOOGLE_MAPS_API_KEY`
- Replace with your actual API key

### 2. Google Gemini API Key

**Used in**: Backend (via `.env` file)

**Setup Steps**:
1. Visit [Google AI Studio](https://aistudio.google.com/apikeys)
2. Click "Create API Key"
3. Copy the key

**How to use**:
- Add to `.env` file: `GEMINI_API_KEY=your_key_here`

### 3. Email Configuration (Gmail App Password)

**Used in**: Backend (via `.env` file)

**Setup Steps**:
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" as the app
3. Generate password (16 characters)
4. Copy the password

**How to use**:
- Add to `.env` file:
  ```
  SENDER_EMAIL=your.email@gmail.com
  SENDER_PASSWORD=your_16_char_app_password
  ```

## Security Best Practices

### Google Maps API Key (Frontend)
- ✅ **DO**: Restrict by HTTP referrer
- ✅ **DO**: Limit to only required APIs
- ❌ **DON'T**: Use the same key for backend services

### Backend API Keys (.env file)
- ✅ **DO**: Keep `.env` file local only (never commit to Git)
- ✅ **DO**: Use different keys for development and production
- ✅ **DO**: Rotate keys periodically
- ❌ **DON'T**: Share keys in screenshots, chat, or documentation

## Exposed API Key - What to Do

If you accidentally expose an API key:

1. **Immediately revoke the key** in Google Cloud Console
2. **Generate a new key** with proper restrictions
3. **Update your local files** with the new key
4. **If committed to Git**: Clean git history (see `SECURITY_GUIDE.md`)

## For Other Contributors

If someone else is deploying this project:
- They must create their own API keys
- Copy `env.example` to `.env` and fill in their keys
- Add their own Maps API key to the HTML files
