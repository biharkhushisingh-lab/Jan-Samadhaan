"""
Add CITIZEN LOGIN button below NEW CITIZEN button
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the NEW CITIZEN button and add CITIZEN LOGIN below it
# Search for the button
import re

# Pattern to find any button with "NEW CITIZEN" text
pattern = r'(<button[^>]*>[\s\S]*?NEW CITIZEN[\s\S]*?</button>)'

match = re.search(pattern, content, re.IGNORECASE)

if match:
    new_citizen_button = match.group(1)
    print("✅ Found NEW CITIZEN button:")
    print(new_citizen_button[:100] + "...")
    
    # Create the CITIZEN LOGIN button
    citizen_login_button = '''
        
        <!-- CITIZEN LOGIN Button (for existing users) -->
        <button onclick="authModule.showAuthModal('signin')" style="
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
            font-size: 16px;
            margin-top: 15px;
            transition: all 0.3s;
        " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
            CITIZEN LOGIN →
        </button>'''
    
    # Insert the CITIZEN LOGIN button right after NEW CITIZEN button
    content = content.replace(match.group(0), match.group(0) + citizen_login_button)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Successfully added CITIZEN LOGIN button below NEW CITIZEN!")
    print("\nNow you have:")
    print("  1. NEW CITIZEN → (green) - for registration")
    print("  2. CITIZEN LOGIN → (purple) - for existing users")
    
else:
    print("❌ Could not find NEW CITIZEN button")
    print("Searching for button patterns...")
    
    # Find all buttons
    buttons = re.findall(r'<button[^>]*>.*?</button>', content, re.DOTALL)
    for i, btn in enumerate(buttons[:5], 1):
        print(f"\nButton {i}: {btn[:80]}...")
