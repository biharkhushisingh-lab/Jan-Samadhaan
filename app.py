# =================================================================
# 🇮🇳 BHARAT E-GRIEVANCE SYSTEM - MULTILINGUAL EDITION
# Features: AI, Maps, SLA, Forwarding, EMAIL, GEOLOCATION, TRANSLATION
# Supports: Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu
# =================================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from db_config import get_db, init_db, is_postgres, get_db_cursor, format_sql  # PostgreSQL support
import os
import time
import random
import hashlib
import requests
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Translation imports
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    print("⚠️  deep-translator not installed. Run: pip install deep-translator")
    TRANSLATION_AVAILABLE = False

# ============= CONFIGURATION =============
app = Flask(__name__)
CORS(app)

VERSION = "v2.0.5-DIAGNOSTIC"

@app.route('/api/health')
def health():
    db_type = "PostgreSQL" if is_postgres() else "SQLite"
    return jsonify({
        "status": "online",
        "version": VERSION,
        "database": db_type,
        "time": datetime.now().isoformat()
    }), 200

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Handle DB initialization
init_db()

# ============= 🌐 MULTILINGUAL SUPPORT =============
SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'native': 'English', 'flag': '🇬🇧'},
    'hi': {'name': 'Hindi', 'native': 'हिंदी', 'flag': '🇮🇳'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'flag': '🇮🇳'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'flag': '🇮🇳'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'flag': '🇮🇳'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'flag': '🇮🇳'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'flag': '🇮🇳'},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'flag': '🇮🇳'},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'flag': '🇮🇳'},
    'pa': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'flag': '🇮🇳'},
    'or': {'name': 'Odia', 'native': 'ଓଡ଼ିଆ', 'flag': '🇮🇳'},
    'as': {'name': 'Assamese', 'native': 'অসমীয়া', 'flag': '🇮🇳'},
    'ur': {'name': 'Urdu', 'native': 'اردو', 'flag': '🇮🇳'}
}

def translate_text(text, from_lang='auto', to_lang='en'):
    """Universal translator for Bharat languages"""
    if not TRANSLATION_AVAILABLE or not text or text.strip() == '':
        return text
    
    try:
        if from_lang == to_lang:
            return text
        
        translator = GoogleTranslator(source=from_lang, target=to_lang)
        translated = translator.translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# ============= 📧 EMAIL CONFIGURATION =============
EMAIL_CONFIG = {
    'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
    'SENDER_EMAIL': os.getenv('SENDER_EMAIL', ''),
    'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD', ''),
    'SENDER_NAME': os.getenv('SENDER_NAME', 'भारत ई-शिकायत प्रणाली | Bharat E-Grievance')
}

# ============= AI & SLA CONFIG =============
# Google Gemini Configuration - Using REST API for Python 3.14 compatibility
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

if GEMINI_API_KEY:
    AI_AVAILABLE = True
    print("✅ Google Gemini AI initialized (REST API)")
else:
    AI_AVAILABLE = False
    print("⚠️  No Gemini API key found. AI features will use fallback logic.")
    print("   Get FREE API key: https://aistudio.google.com/")

# ============= UTILITIES =============

def hash_password(p):
    """Securely hash passwords using SHA-256"""
    return hashlib.sha256(p.encode()).hexdigest()

SLA_TIMES = {
    1: 2, 2: 4, 3: 8, 4: 12, 5: 24, 
    6: 48, 7: 72, 8: 96, 9: 120, 10: 168
}

ESCALATION_LEVELS = {
    'WARNING': 50, 'URGENT': 75, 'CRITICAL': 90, 'OVERDUE': 100
}

# ============= EMAIL HELPER FUNCTIONS =============

def send_email_async(to_email, subject, html_content, attachments=None):
    if not to_email: return
    thread = threading.Thread(target=send_email, args=(to_email, subject, html_content, attachments))
    thread.daemon = True
    thread.start()

def send_email(to_email, subject, html_content, attachments=None):
    try:
        if 'your.email' in EMAIL_CONFIG['SENDER_EMAIL']:
            print(f"⚠️  Email skipped: Config not set. (To: {to_email})")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EMAIL_CONFIG['SENDER_NAME']} <{EMAIL_CONFIG['SENDER_EMAIL']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                        msg.attach(part)
        
        with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email Error: {str(e)}")
        return False

def get_email_template(template_type, data, lang='en'):
    base_style = """
    <style>
        body { font-family: 'Segoe UI', 'Noto Sans', sans-serif; color: #333; line-height: 1.8; }
        .container { max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }
        .header { background: linear-gradient(135deg, #FF9933, #138808); color: white; padding: 25px; text-align: center; }
        .content { padding: 30px; background: #fff; }
        .info-box { background: #f8f9fa; padding: 15px; border-left: 4px solid #FF9933; margin: 20px 0; border-radius: 4px; }
        .footer { background: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #777; }
        .btn { display: inline-block; padding: 10px 20px; background: #FF9933; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }
        .map-link { display: inline-block; padding: 8px 15px; background: #138808; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }
    </style>
    """

    map_link_html = ""
    if data.get('latitude') and data.get('longitude'):
        map_link_html = f"""
        <p><strong>📍 Location:</strong> 
           <a href="https://www.google.com/maps?q={data['latitude']},{data['longitude']}" 
              class="map-link" target="_blank">View on Map</a>
        </p>
        """

    if template_type == 'complaint_submitted':
        return f"""
        <html><head>{base_style}</head><body>
            <div class="container">
                <div class="header"><h1>🇮🇳 Complaint Registered | शिकायत दर्ज</h1></div>
                <div class="content">
                    <p>Dear <strong>{data['citizen_name']}</strong>,</p>
                    <p>Your complaint has been registered successfully.</p>
                    <div class="info-box">
                        <p><strong>Tracking ID:</strong> {data['tracking_id']}</p>
                        <p><strong>Priority:</strong> P-{data['priority']}</p>
                        <p><strong>Department:</strong> {data['department']}</p>
                        <p><strong>SLA Deadline:</strong> {data['sla_deadline']}</p>
                        {map_link_html}
                    </div>
                </div>
                <div class="footer">भारत ई-शिकायत प्रणाली | Bharat E-Grievance</div>
            </div>
        </body></html>
        """
    
    return "<html><body>Notification</body></html>"

# ============= DATABASE FUNCTIONS =============
# Database functions (get_db, init_db) are now in db_config.py

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_with_ai(desc, cat):
    """Analyze complaint using Google Gemini AI or fallback to keyword analysis"""
    
    # Try Gemini AI REST API first
    if AI_AVAILABLE and GEMINI_API_KEY:
        try:
            prompt = f"""Analyze this complaint and provide ONLY a JSON response (no markdown, no code blocks):

Description: {desc}
Category: {cat}

Provide JSON response with these exact fields:
{{
    "priority": 1-10 (1=highest urgency, 10=lowest),
    "sentiment": "positive/neutral/negative",
    "detected_department": "department name"
}}

Priority Level Guide:
- P1 (2h): Life-threatening, live wires, major water bursts, gas leaks.
- P2 (4h): Very High. Sewage overflow, large potholes on main roads.
- P3 (8h): High. Street lights out in high-risk areas, hospital equipment issues.
- P4-P5 (12-24h): Medium. Missed garbage collection, minor drainage blocks.
- P6-P7 (48-72h): Standard. Poor maintenance, street cleaning, park lighting.
- P8-P10 (4-7 days): Low. Future planning, beautification, general inquiries.

Department detection rules:
- Water/sewage/drainage issues → "Water_Supply_Dept"
- Road/bridge/infrastructure → "Public_Works_Dept"
- Garbage/cleaning/sanitation → "Sanitation_Dept"
- Electricity/power/transformer → "Power_Dept"
- Hospital/clinic/medical → "Health_Dept"
- Everything else → "General_Admin_Dept"

Analyze carefully and detect the correct department and priority."""
            
            # Call Gemini REST API
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result_data = response.json()
                result_text = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up response (remove markdown code blocks if present)
                result_text = result_text.replace('```json', '').replace('```', '').strip()
                
                result = json.loads(result_text)
                
                # Ensure we have all required fields
                if 'detected_department' not in result:
                    result['detected_department'] = None
                if 'priority' not in result:
                    result['priority'] = 5
                if 'sentiment' not in result:
                    result['sentiment'] = 'neutral'
                    
                print(f"✅ Gemini AI Analysis: Priority={result['priority']}, Dept={result.get('detected_department')}")
                return result
            else:
                print(f"⚠️  Gemini API Error: {response.status_code}, falling back to keyword analysis")
            
        except Exception as e:
            print(f"⚠️  Gemini AI Error: {e}, falling back to keyword analysis")
    
    # Fallback: Simple keyword-based detection
    desc_lower = desc.lower()
    detected_dept = None
    
    # Keywords for department detection
    if any(word in desc_lower for word in ['electricity', 'power', 'transformer', 'current', 'voltage', 'बिजली', 'विद्युत']):
        detected_dept = 'Power_Dept'
    elif any(word in desc_lower for word in ['water', 'pipe', 'leak', 'sewage', 'drainage', 'पानी', 'नाली']):
        detected_dept = 'Water_Supply_Dept'
    elif any(word in desc_lower for word in ['road', 'pothole', 'bridge', 'footpath', 'सड़क']):
        detected_dept = 'Public_Works_Dept'
    elif any(word in desc_lower for word in ['garbage', 'trash', 'waste', 'cleaning', 'sanitation', 'कचरा']):
        detected_dept = 'Sanitation_Dept'
    elif any(word in desc_lower for word in ['hospital', 'doctor', 'medical', 'health', 'clinic', 'अस्पताल']):
        detected_dept = 'Health_Dept'
    
    pri = 7 # Default standard
    
    # Check for explicit Emergency categories
    if cat in ['Power_Emergency', 'Water_Emergency', 'Safety_Emergency']:
        pri = 1
        print(f"🚨 Categorical Emergency Detected: Priority forced to 1")
    
    # Critical (P1-P2) keywords (only check if not already forced to P1)
    if pri > 1:
        if any(word in desc_lower for word in ['emergency', 'danger', 'hazard', 'death', 'killed', 'safety', 'shock', 'blast', 'live wire', 'transformer', 'manhole', 'gas leak', 'मृत्यु', 'खतरा', 'அபாயம்']):
            pri = 1
        elif any(word in desc_lower for word in ['burst', 'overflow', 'pothole', 'accident', 'injury', 'fallen tree', 'flickering', 'dark', 'चोट', 'दुर्घटना']):
            pri = 2
    # High (P3-P4)
    elif any(word in desc_lower for word in ['urgent', 'immediately', 'night', 'hospital', 'medical', 'dog bite', 'stray dog', 'तुरंत', 'உடனடியாக']):
        pri = 3
    elif any(word in desc_lower for word in ['block', 'smell', 'dead animal', 'गंध', 'दुर्गंध']):
        pri = 4
    # Low (P8-P10)
    elif any(word in desc_lower for word in ['planning', 'beautification', 'future', 'suggestion', 'योजना', 'सौंदर्यीकरण']):
        pri = 9
    
    print(f"📊 Keyword Analysis: Priority={pri}, Dept={detected_dept}")
    return {
        'priority': pri, 
        'sentiment': 'neutral', 
        'urgency': 'medium',
        'detected_department': detected_dept
    }

def route_complaint(cat):
    ROUTES = {
        'Water_Supply': 'Water_Supply_Dept',
        'Water_Emergency': 'Water_Supply_Dept',
        'Roads_Infrastructure': 'Public_Works_Dept',
        'Sanitation': 'Sanitation_Dept',
        'Power': 'Power_Dept',
        'Power_Emergency': 'Power_Dept',
        'Street_Lights': 'Power_Dept',
        'Health': 'Health_Dept',
        'Health_Services': 'Health_Dept',
        'Safety_Emergency': 'General_Admin_Dept',
        'Animals': 'Sanitation_Dept',
        'Drainage': 'Water_Supply_Dept'
    }
    return ROUTES.get(cat, 'General_Admin_Dept')

def get_department_email(dept):
    """Retrieve email address for a specific department"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql("SELECT email FROM officials WHERE department = ? LIMIT 1", conn)
        cursor.execute(query, (dept,))
        result = cursor.fetchone()
        conn.close()
        return result['email'] if result else None
    except Exception as e:
        print(f"Error getting dept email: {e}")
        return None

def check_sla_status(complaint):
    try:
        if complaint['status'] in ['Resolved', 'Rejected']:
            return 'NONE'
        
        deadline = datetime.fromisoformat(complaint['sla_deadline'])
        now = datetime.now()
        remaining = (deadline - now).total_seconds() / 3600
        percent = (1 - (remaining / complaint['sla_hours'])) * 100
        
        if percent >= 100: return 'OVERDUE'
        elif percent >= 90: return 'CRITICAL'
        elif percent >= 75: return 'URGENT'
        elif percent >= 50: return 'WARNING'
        return 'NONE'
    except:
        return 'NONE'

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in meters
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth's radius in meters
    R = 6371000
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def check_duplicate_complaints(lat, lon, category, radius_meters=20):
    """
    Check if there are existing complaints within specified radius
    Returns list of nearby complaints
    """
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        # Get all complaints with location data that are not resolved
        query = '''SELECT id, category, description, latitude, longitude, 
                   created_at, status, citizen_name, priority
                   FROM complaints 
                   WHERE latitude IS NOT NULL 
                   AND longitude IS NOT NULL 
                   AND status NOT IN ('Resolved', 'Rejected')'''
        
        cursor.execute(format_sql(query, conn))
        complaints = cursor.fetchall()
        conn.close()
        
        nearby = []
        for complaint in complaints:
            c_lat = complaint['latitude']
            c_lon = complaint['longitude']
            
            # Calculate distance
            distance = calculate_distance(float(lat), float(lon), c_lat, c_lon)
            
            # Check if within radius
            if distance <= radius_meters:
                # Check if same category or similar
                if complaint['category'] == category or category == '' or category is None:
                    nearby.append({
                        'id': complaint['id'],
                        'category': complaint['category'],
                        'description': complaint['description'][:100] + '...' if len(complaint['description']) > 100 else complaint['description'],
                        'distance': round(distance, 1),
                        'created_at': complaint['created_at'],
                        'status': complaint['status'],
                        'citizen_name': complaint['citizen_name'],
                        'priority': complaint['priority']
                    })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance'])
        
        return nearby
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return []

# ============= OTP & AUTHENTICATION HELPERS =============

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def generate_tracking_id():
    """Generate unique complaint tracking ID"""
    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    random_part = str(random.randint(1000, 9999))
    return f"GRV-{date_part}-{random_part}"

def store_otp(phone, otp_code, purpose='signin'):
    """Store OTP in database with expiration"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        expiry = (datetime.now() + timedelta(minutes=5)).isoformat()
        
        query = format_sql("INSERT INTO otps (phone, otp_code, purpose, created_at, expires_at) VALUES (?, ?, ?, ?, ?)", conn)
        cursor.execute(query, (phone, otp_code, purpose, datetime.now().isoformat(), expiry))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error storing OTP: {e}")
        return False

def validate_otp(phone, otp_code):
    """Validate OTP and mark as used"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        now = datetime.now().isoformat()
        
        # Find valid, unused OTP
        query = format_sql('''SELECT * FROM otps 
                             WHERE phone=? AND otp_code=? AND used=? AND expires_at > ?
                             ORDER BY created_at DESC LIMIT 1''')
        cursor.execute(query, (phone, otp_code, 0, now))
        otp = cursor.fetchone()
        
        if otp:
            # Mark as used
            upd_q = format_sql('UPDATE otps SET used=? WHERE id=?')
            cursor.execute(upd_q, (1, otp['id']))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    except Exception as e:
        print(f"Error validating OTP: {e}")
        return False

def send_otp_email(to_email, otp_code, phone, purpose='signin'):
    """Send OTP via email"""
    purpose_text = "Sign In" if purpose == 'signin' else "Sign Up"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; }}
            .header {{ background: linear-gradient(135deg, #FF9933, #138808); color: white; padding: 25px; text-align: center; }}
            .content {{ padding: 30px; }}
            .otp-box {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; 
                       letter-spacing: 8px; color: #FF9933; border: 2px dashed #FF9933; border-radius: 8px; margin: 20px 0; }}
            .footer {{ background: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><h1>🔐 Your OTP Code</h1></div>
            <div class="content">
                <p>Dear Citizen,</p>
                <p>Your OTP for <strong>{purpose_text}</strong> to Jan Samadhaan portal is:</p>
                <div class="otp-box">{otp_code}</div>
                <p><strong>⏰ Valid for 5 minutes only</strong></p>
                <p>Mobile Number: {phone}</p>
                <p>If you didn't request this OTP, please ignore this email.</p>
            </div>
            <div class="footer">भारत ई-शिकायत प्रणाली | Bharat E-Grievance</div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, f"🔐 Your OTP Code - {otp_code}", html_content)

def get_citizen_by_phone(phone):
    """Retrieve citizen details by phone number"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql("SELECT * FROM citizens WHERE phone = ?")
        cursor.execute(query, (phone,))
        citizen = cursor.fetchone()
        conn.close()
        return dict(citizen) if citizen else None
    except Exception as e:
        print(f"Error fetching citizen: {e}")
        return None

def create_citizen(phone, name=None, email=None, address=None):
    """Create new citizen record"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        now = datetime.now().isoformat()
        query = format_sql("INSERT INTO citizens (phone, name, email, address, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?)")
        cursor.execute(query, (phone, name, email, address, now, now))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating citizen: {e}")
        return False

def update_citizen_login(phone):
    """Update last login time for citizen"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        now = datetime.now().isoformat()
        query = format_sql("UPDATE citizens SET last_login = ? WHERE phone = ?", conn)
        cursor.execute(query, (now, phone))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating login: {e}")
        return False

# ============= API ROUTES =============

@app.route('/')
@app.route('/index.html')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route('/official.html')
def official():
    return send_from_directory('.', 'official.html')

@app.route('/api/languages', methods=['GET'])
def get_languages():
    return jsonify({"success": True, "languages": SUPPORTED_LANGUAGES, 
                    "translation_available": TRANSLATION_AVAILABLE}), 200

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    from_lang = data.get('from', 'auto')
    to_lang = data.get('to', 'en')
    
    if not TRANSLATION_AVAILABLE:
        return jsonify({"success": False, "message": "Translation not available"}), 400
    
    translated = translate_text(text, from_lang, to_lang)
    
    return jsonify({
        "success": True, 
        "translated": translated,
        "from": from_lang,
        "to": to_lang
    }), 200

# ============= CITIZEN AUTHENTICATION ENDPOINTS =============

@app.route('/api/citizen/check-exists', methods=['POST'])
def check_citizen_exists():
    """Check if citizen exists by phone or email"""
    try:
        data = request.json
        identifier = data.get('phone')
        
        if not identifier:
            return jsonify({"success": False, "message": "Identifier required"}), 400
            
        conn = get_db()
        cursor = get_db_cursor(conn)
        # Search by phone
        query_phone = format_sql('SELECT * FROM citizens WHERE phone=?')
        citizen = cursor.execute(query_phone, (identifier,)).fetchone()
        
        # If not found and identifier looks like email, search by email
        if not citizen and '@' in identifier:
            query_email = format_sql('SELECT * FROM citizens WHERE email=?')
            citizen = cursor.execute(query_email, (identifier,)).fetchone()
            
        conn.close()
        
        if citizen:
            c = dict(citizen)
            return jsonify({
                "success": True,
                "exists": True,
                "citizen": {
                    "phone": c['phone'],
                    "email": c['email'],
                    "name": c['name'],
                    "address": c.get('address', '')
                }
            }), 200
        else:
            return jsonify({"success": True, "exists": False}), 200
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/citizen/send-otp', methods=['POST'])
def citizen_send_otp():
    """Send OTP to citizen's phone (via email)"""
    try:
        data = request.json
        phone = data.get('phone')
        email = data.get('email')
        purpose = data.get('purpose', 'signin')
        
        if not phone or not email:
            return jsonify({"success": False, "message": "Phone and email required"}), 400
        
        # Generate and store OTP (123456 is mock code for testing)
        otp_code = "123456" 
        
        if not store_otp(phone, otp_code, purpose):
            return jsonify({"success": False, "message": "Failed to generate OTP"}), 500
        
        # Send real email in BACKGROUND to prevent UI hang
        import threading
        threading.Thread(target=send_otp_email, args=(email, otp_code, phone, purpose)).start()
        
        return jsonify({
            "success": True, 
            "message": f"OTP 123456 sent to {email}",
            "expires_in": 300
        }), 200
            
    except Exception as e:
        print(f"Send OTP error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/citizen/verify-otp', methods=['POST'])
def citizen_verify_otp():
    """Verify OTP for sign in"""
    try:
        data = request.json
        phone = data.get('phone')
        otp_code = data.get('otp')
        
        if not phone or not otp_code:
            return jsonify({"success": False, "message": "Phone and OTP required"}), 400
        
        if validate_otp(phone, otp_code):
            # Check if citizen exists
            citizen = get_citizen_by_phone(phone)
            
            if citizen:
                # Update last login
                update_citizen_login(phone)
                
                return jsonify({
                    "success": True,
                    "message": "OTP verified",
                    "citizen": {
                        "phone": citizen['phone'],
                        "name": citizen['name'],
                        "email": citizen['email'],
                        "address": citizen['address']
                    }
                }), 200
            else:
                # New user - need to complete signup
                return jsonify({
                    "success": True,
                    "message": "OTP verified - complete registration",
                    "new_user": True
                }), 200
        else:
            return jsonify({"success": False, "message": "Invalid or expired OTP"}), 401
            
    except Exception as e:
        print(f"Verify OTP error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/citizen/signup', methods=['POST'])
def citizen_signup():
    """Complete citizen signup after OTP verification"""
    try:
        data = request.json
        phone = data.get('phone')
        name = data.get('name')
        email = data.get('email')
        address = data.get('address')
        
        if not phone or not name or not email:
            return jsonify({"success": False, "message": "Phone, name, and email required"}), 400
        
        # Create citizen record
        if create_citizen(phone, name, email, address):
            return jsonify({
                "success": True,
                "message": "Registration completed successfully",
                "citizen": {
                    "phone": phone,
                    "name": name,
                    "email": email,
                    "address": address
                }
            }), 200
        else:
            return jsonify({"success": False, "message": "User may already exist"}), 400
            
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# Duplicate removed - using version at line 586

@app.route('/api/citizen/complaints', methods=['GET'])
def get_citizen_complaints():
    """Get all complaints for a citizen by phone number"""
    try:
        phone = request.args.get('phone')
        if not phone:
            return jsonify({"success": False, "message": "Phone required"}), 400
            
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql("SELECT * FROM complaints WHERE citizen_phone = ? ORDER BY created_at DESC")
        cursor.execute(query, (phone,))
        complaints = cursor.fetchall()
        
        # Format results
        results = []
        for c in complaints:
            d = dict(c)
            d['escalation_level'] = check_sla_status(d)
            results.append(d)
        conn.close()
        return jsonify({"success": True, "complaints": results}), 200
    except Exception as e:
        print(f"Error fetching complaints: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ============= OLD VERIFICATION (DEPRECATED) =============
@app.route('/api/verify_citizen', methods=['POST'])
def verify():
    """Legacy endpoint - now also saves citizen to database"""
    d = request.json
    name = d.get('name')
    email = d.get('email')
    phone = d.get('phone')
    
    if name and email and phone:
        try:
            conn = get_db()
            cursor = get_db_cursor(conn)
            # Register or update the citizen in our new system table
            now = datetime.now().isoformat()
            if is_postgres():
                query = '''
                    INSERT INTO citizens (phone, name, email, created_at, last_login)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT(phone) DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        last_login = EXCLUDED.last_login
                '''
                cursor.execute(query, (phone, name, email, now, now))
            else:
                query = '''
                    INSERT OR REPLACE INTO citizens (phone, name, email, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?)
                '''
                cursor.execute(query, (phone, name, email, now, now))
            conn.commit()
            conn.close()
            return jsonify({"success": True}), 200
        except Exception as e:
            print(f"Verify save error: {e}")
            return jsonify({"success": True}), 200 # Still return true so frontend continues
            
    return jsonify({"success": False, "message": "All fields required"}), 400


@app.route('/api/check_duplicates', methods=['POST'])
def check_duplicates():
    """
    Check for duplicate complaints near the selected location
    """
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        category = data.get('category', '')
        radius = int(data.get('radius', 20))  # Default 20 meters
        
        if not lat or not lon:
            return jsonify({"success": False, "message": "Location required"}), 400
        
        # Check for nearby complaints
        nearby_complaints = check_duplicate_complaints(lat, lon, category, radius)
        
        return jsonify({
            "success": True,
            "duplicates_found": len(nearby_complaints) > 0,
            "count": len(nearby_complaints),
            "nearby_complaints": nearby_complaints[:5],  # Return max 5
            "radius_checked": radius
        }), 200
        
    except Exception as e:
        print(f"Duplicate check error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/submit_complaint', methods=['POST'])
def submit():
    try:
        d = request.form
        cat = d.get('category')
        desc = d.get('description')
        citizen_lang = d.get('citizen_language', 'en')
        
        desc_original = desc
        desc_translated = translate_text(desc, citizen_lang, 'en') if citizen_lang != 'en' else desc
        
        lat = d.get('latitude')
        lon = d.get('longitude')
        loc_addr = d.get('location_address', d.get('citizen_address', ''))
        
        # Get AI analysis (includes department detection)
        ai = analyze_with_ai(desc_translated, cat)
        pri = ai.get('priority', 5)
        
        # Use AI-detected department if category is empty or if AI suggests a better department
        if not cat or cat == '':
            # No category provided - use AI detection
            dept = ai.get('detected_department', 'General_Admin_Dept')
            print(f"⚠️ No category provided. AI detected department: {dept}")
        else:
            # Category provided - use standard routing but check AI suggestion
            dept = route_complaint(cat)
            ai_dept = ai.get('detected_department')
            if ai_dept and ai_dept != dept:
                # AI suggests different department - use AI's suggestion as it analyzed the description
                print(f"ℹ️ AI suggests {ai_dept} instead of {dept} based on description analysis")
                dept = ai_dept
        
        sla_h = SLA_TIMES.get(pri, 24)
        sla_dl = datetime.now() + timedelta(hours=sla_h)
        tid = generate_tracking_id()  # Use new standardized format
        
        media = None
        if 'media_upload' in request.files:
            f = request.files['media_upload']
            if f and allowed_file(f.filename):
                fn = secure_filename(f.filename)
                media = f"{tid}_{fn}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], media))
        
        conn = get_db()
        cursor = get_db_cursor(conn)
        
        sql = """INSERT INTO complaints 
            (id, citizen_name, citizen_email, citizen_phone, citizen_address, 
             latitude, longitude, location_address,
             category, description, description_original, description_translated,
             media_path, priority, department, assigned_to, 
             created_at, sla_hours, sla_deadline, ai_analysis, citizen_language)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
            
        cursor.execute(format_sql(sql, conn),
            (tid, d['citizen_name'], d['citizen_email'], d['citizen_phone'], d['citizen_address'],
             lat, lon, loc_addr,
             cat if cat else 'Auto-Detected', desc_translated, desc_original, desc_translated, 
             media, pri, dept, f"{dept}_Manager", 
             datetime.now().isoformat(), sla_h, sla_dl.isoformat(), json.dumps(ai), citizen_lang))
        conn.commit()
        conn.close()
        
        email_data = {
            'citizen_name': d['citizen_name'],
            'tracking_id': tid,
            'category': cat if cat else 'Auto-Detected by AI',
            'priority': pri,
            'department': dept,
            'sla_deadline': sla_dl.strftime("%Y-%m-%d %H:%M"),
            'sla_hours': sla_h,
            'ai_sentiment': ai.get('sentiment', 'Neutral'),
            'latitude': lat,
            'longitude': lon
        }
        
        send_email_async(d['citizen_email'], f"Complaint Registered - {tid}", 
                        get_email_template('complaint_submitted', email_data, citizen_lang))
        
        dept_email = get_department_email(dept)
        if dept_email:
            email_data['description'] = desc_translated
            send_email_async(dept_email, f"🔔 New Complaint - {tid}", 
                           get_email_template('complaint_submitted', email_data, 'en'))

        return jsonify({
            "success": True, 
            "tracking_id": tid, 
            "priority": pri, 
            "department": dept, 
            "sla_hours": sla_h, 
            "sla_deadline": sla_dl.strftime("%Y-%m-%d %H:%M"), 
            "ai_sentiment": ai.get('sentiment','Neutral'),
            "translation_done": citizen_lang != 'en',
            "detected_language": citizen_lang,
            "ai_routed": not cat or cat == ''
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/official/login', methods=['POST'])
def official_login():
    try:
        data = request.json
        u = data.get('username', '').lower().strip()
        p = data.get('password', '')
        g = data.get('govt_id', '').strip()
        
        if not u or not p:
            return jsonify({"success": False, "message": "Username and password required"}), 400
            
        print(f"🔑 Login attempt for user: {u}")
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql("SELECT * FROM officials WHERE LOWER(username) = LOWER(?)", conn)
        cursor.execute(query, (u,))
        off = cursor.fetchone()
        conn.close()
        
        if off:
            print(f"✅ Found official: {off['username']}")
            ph = hash_password(p)
            
            # Use dictionary access for PostgreSQL/SQLite compatibility
            # SQLite rows don't have .get(), so we use a safe access pattern
            stored_hash = off['password_hash']
            
            try:
                gid_val = off['govt_id']
            except (KeyError, IndexError, TypeError):
                gid_val = None
                
            stored_gid = str(gid_val).strip() if gid_val is not None else ""
            
            pw_match = (stored_hash == ph)
            # If g is provided, it must match. If not provided, skip gid check.
            gid_match = (not g or g == stored_gid)
            
            if pw_match and gid_match:
                return jsonify({
                    "success": True, 
                    "token": f"TOK_{off['id']}",
                    "user": {
                        "username": off['username'],
                        "name": off['name'],
                        "department": off['department'],
                        "language": off['preferred_language']
                    },
                    "department": off['department']
                }), 200
            else:
                reason = "Incorrect password" if not pw_match else "Incorrect Govt ID"
                return jsonify({"success": False, "message": f"Login Failed ({VERSION}): {reason}"}), 401
        
        return jsonify({"success": False, "message": f"Login Failed ({VERSION}): Official account not found"}), 401
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

@app.route('/api/debug/db-status')
def db_status():
    """Diagnostic route to check database health and contents"""
    try:
        from db_config import get_db_info
        info = get_db_info()
        
        conn = get_db()
        cursor = get_db_cursor(conn)
        
        # Robust count fetching
        def get_count(table):
            cursor.execute(format_sql(f"SELECT COUNT(*) FROM {table}", conn))
            row = cursor.fetchone()
            if not row: return 0
            if isinstance(row, (list, tuple)): return row[0]
            if hasattr(row, 'values'): return list(row.values())[0]
            try: return row[0]
            except: return 0

        official_count = get_count("officials")
        complaint_count = get_count("complaints")
        
        # Check if admin specifically exists
        cursor.execute(format_sql("SELECT username FROM officials WHERE username = ?", conn), ('admin@gov.in',))
        admin_exists = cursor.fetchone() is not None
        
        conn.close()
        
        return jsonify({
            "success": True,
            "db_type": info['type'],
            "officials_count": official_count,
            "complaints_count": complaint_count,
            "admin_ready": admin_exists,
            "version": VERSION,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/debug/force-seed')
def force_seed():
    """Manually trigger database seeding and return results/errors"""
    results = {}
    try:
        from create_admin import create_admin
        from create_department_officials import create_department_officials
        
        results['admin'] = "Attempting..."
        try:
            create_admin()
            results['admin'] = "Success"
        except Exception as e:
            results['admin'] = f"Failed: {str(e)}"
            
        results['officials'] = "Attempting..."
        try:
            create_department_officials()
            results['officials'] = "Success"
        except Exception as e:
            results['officials'] = f"Failed: {str(e)}"
            
        return jsonify({
            "success": True,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "results": results
        }), 500

@app.route('/api/complaints')
def get_all_complaints():
    dept = request.args.get('department')
    
    conn = get_db()
    cursor = get_db_cursor(conn)
    q = "SELECT * FROM complaints WHERE 1=1"
    p = []
    if dept: 
        q += " AND department=?"; p.append(dept)
    
    q += " ORDER BY created_at DESC"
    
    cursor.execute(format_sql(q, conn), tuple(p))
    rows = cursor.fetchall()
    conn.close()
    
    res = []
    for r in rows:
        d = dict(r)
        d['escalation_level'] = check_sla_status(d)
        # Ensure frontend expected fields are present
        d['description_display'] = d.get('description_translated', d.get('description', ''))
        d['description_original'] = d.get('description_original', d.get('description', ''))
        res.append(d)
    
    return jsonify({"success": True, "complaints": res}), 200

@app.route('/api/complaint/<cid>', methods=['GET'])
def get_complaint_details(cid):
    """Get details of a single complaint by ID"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql("SELECT * FROM complaints WHERE id = ?")
        cursor.execute(query, (cid,))
        c = cursor.fetchone()
        conn.close()
        if c:
            return jsonify({"success": True, "complaint": dict(c)}), 200
        return jsonify({"success": False, "message": "Not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/complaint/<cid>/update', methods=['POST'])
def update(cid):
    try:
        d = request.form
        status = d.get('status')
        summary = d.get('resolution_summary')
        forward_dept = d.get('forward_dept')
        rejection_reason = d.get('rejection_reason')
        transferred_by = d.get('transferred_by', 'Official')
        transfer_reason = d.get('transfer_reason', '')
        
        conn = get_db()
        cursor = get_db_cursor(conn)
        
        curr_query = format_sql('SELECT * FROM complaints WHERE id=?', conn)
        curr = cursor.execute(curr_query, (cid,)).fetchone()
        
        if not curr:
            conn.close()
            return jsonify({"success": False, "message": "Complaint not found"}), 404
        
        upd_q_parts = ["status=?", "resolution_summary=?"]
        upd_p = [status, summary]
        
        citizen_lang = curr['citizen_language'] if curr['citizen_language'] else 'en'
        
        if 'resolution_proof' in request.files:
            f = request.files['resolution_proof']
            if f and allowed_file(f.filename):
                fn = secure_filename(f.filename)
                proof = f"res_{int(time.time())}_{fn}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], proof))
                upd_q_parts.append("resolution_proof=?")
                upd_p.append(proof)

        # Handle department transfer
        if status == 'Forwarded' and forward_dept:
            old_dept = curr['department']
            upd_q_parts.extend(["department=?", "assigned_to=?", "transfer_count=?"])
            upd_p.extend([forward_dept, f"{forward_dept}_Manager", 
                         (curr['transfer_count'] or 0) + 1])
            
            # Log transfer history
            transfer_query = format_sql('''INSERT INTO complaint_transfers 
                           (complaint_id, from_department, to_department, transferred_by, transfer_reason, transferred_at)
                           VALUES (?,?,?,?,?,?)''', conn)
            cursor.execute(transfer_query,
                        (cid, old_dept, forward_dept, transferred_by, transfer_reason, 
                         datetime.now().isoformat()))

        # Handle rejection
        if status == 'Rejected' and rejection_reason:
            upd_q_parts.append("rejection_reason=?")
            upd_p.append(rejection_reason)

        if status == 'Resolved':
            upd_q_parts.append("resolved_at=?")
            upd_p.append(datetime.now().isoformat())

        upd_q = format_sql(f"UPDATE complaints SET {', '.join(upd_q_parts)} WHERE id=?", conn)
        upd_p.append(cid)
        
        cursor.execute(upd_q, tuple(upd_p))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Complaint {status}"}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/complaint/<cid>/transfers', methods=['GET'])
def get_transfer_history(cid):
    """Get transfer history for a complaint"""
    try:
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql('''SELECT * FROM complaint_transfers 
                                   WHERE complaint_id=? 
                                   ORDER BY transferred_at DESC''', conn)
        transfers = cursor.execute(query, (cid,)).fetchall()
        conn.close()
        
        res = [dict(t) for t in transfers]
        return jsonify({"success": True, "transfers": res}), 200
    except Exception as e:
        print(f"Transfer history error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/complaint/<cid>/feedback', methods=['POST'])
def feedback(cid):
    try:
        d = request.json
        conn = get_db()
        cursor = get_db_cursor(conn)
        
        q = format_sql('UPDATE complaints SET citizen_feedback_rating=?, citizen_feedback_comments=? WHERE id=?', conn)
        cursor.execute(q, (d['rating'], d.get('comment',''), cid))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Feedback error: {e}")
        return jsonify({"success": False}), 500

@app.route('/api/add_official', methods=['POST'])
def add_official():
    try:
        d = request.json
        conn = get_db()
        cursor = get_db_cursor(conn)
        query = format_sql('''INSERT INTO officials 
                       (username, password_hash, govt_id, name, department, email, phone) 
                       VALUES (?,?,?,?,?,?,?)''', conn)
        cursor.execute(query, (d['username'], hash_password(d['password']), d['govt_id'], 
                      d['name'], d['department'], d.get('email'), d.get('phone')))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e: 
        print(e)
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/uploads/<fn>')
def get_file(fn): 
    return send_from_directory(app.config['UPLOAD_FOLDER'], fn)

@app.route('/api/analytics/dashboard', methods=['GET'])
def analytics():
    try:
        dept = request.args.get('department')
        conn = get_db()
        cursor = get_db_cursor(conn)
        
        q_base = "FROM complaints WHERE 1=1"
        p = []
        if dept: 
            q_base += " AND department = ?"
            p.append(dept)
        
        query_count = format_sql(f"SELECT COUNT(*) {q_base}", conn)
        cursor.execute(query_count, tuple(p))
        tot = cursor.fetchone()
        count = tot[0] if isinstance(tot, (list, tuple)) else tot['count'] if 'count' in tot else tot[list(tot.keys())[0]]
        
        query_avg = format_sql(f"SELECT AVG(citizen_feedback_rating) {q_base}", conn)
        cursor.execute(query_avg, tuple(p))
        avg_row = cursor.fetchone()
        avg_r = avg_row[0] if isinstance(avg_row, (list, tuple)) else avg_row['avg'] if 'avg' in avg_row else avg_row[list(avg_row.keys())[0]]
        avg_r = avg_r or 0
        
        conn.close()
        return jsonify({"success": True, "analytics": {
            "total_complaints": count, 
            "avg_citizen_rating": round(float(avg_r), 1), 
            "avg_resolution_hours": 0
        }}), 200
    except Exception as e:
        print(f"Analytics Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
@app.route('/api/test_email', methods=['POST'])
def test_email_route():
    try:
        data = request.json
        email = data.get('email')
        
        if not email: 
            return jsonify({"success": False, "message": "No email provided"}), 400
        
        # Create dummy data for the test
        test_data = {
            'citizen_name': 'Test User', 
            'tracking_id': 'TEST-001', 
            'category': 'Testing',
            'priority': 1, 
            'department': 'IT Support',
            'sla_deadline': 'Today', 
            'sla_hours': 24, 
            'ai_sentiment': 'Positive',
            'latitude': '',
            'longitude': ''
        }
        
        # Send the email
        if send_email(email, "🧪 Test Email - Bharat E-Grievance", get_email_template('complaint_submitted', test_data)):
            return jsonify({"success": True, "message": "Email sent"}), 200
        else:
            return jsonify({"success": False, "message": "SMTP failed. Check server logs."}), 500
            
    except Exception as e:
        print(f"Test Email Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
# ============= MAIN =============
if __name__ == '__main__':
    init_db()
    print("="*60)
    print("🇮🇳 BHARAT E-GRIEVANCE SYSTEM - MULTILINGUAL EDITION")
    print("🔗 http://127.0.0.1:5000")
    print("🗺️  Map Integration: Active")
    print("🤖 AI Analysis:", "✅ Google Gemini" if AI_AVAILABLE else "⚠️  Keyword-based (Get free key: https://aistudio.google.com/)")
    print("🌐 Multilingual Support:", "✅ ACTIVE" if TRANSLATION_AVAILABLE else "❌ DISABLED")
    if TRANSLATION_AVAILABLE:
        print("📚 Supported Languages:", len(SUPPORTED_LANGUAGES))
        print("   ", ", ".join([f"{v['flag']} {v['native']}" for v in list(SUPPORTED_LANGUAGES.values())[:6]]))
    else:
        print("⚠️  Install: pip install deep-translator")
    if not EMAIL_CONFIG['SENDER_EMAIL']:
        print("📧 Email:", "⚠️  Configure SENDER_EMAIL in .env file")
    else:
        print("📧 Email:", "✅ Configured")
    print("="*60)
    # Use PORT from environment for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)