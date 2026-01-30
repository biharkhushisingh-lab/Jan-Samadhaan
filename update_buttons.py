"""
Add two separate buttons: NEW CITIZEN and CITIZEN LOGIN
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the auth button we added earlier
old_button = '''<div id="citizenAuthButton" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <button id="mainAuthBtn" onclick="authModule.showAuthModal('signin')" style="
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            transition: all 0.3s;
            font-size: 14px;
        ">
            <span id="authButtonText">🔐 Sign In / Sign Up</span>
        </button>
    </div>'''

new_buttons = '''<div id="citizenAuthButtons" style="position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;">
        <!-- NEW CITIZEN Button -->
        <button onclick="authModule.showAuthModal('signup')" style="
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            transition: all 0.3s;
            font-size: 14px;
            white-space: nowrap;
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            ✨ NEW CITIZEN
        </button>
        
        <!-- CITIZEN LOGIN Button -->
        <button id="mainAuthBtn" onclick="authModule.showAuthModal('signin')" style="
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            transition: all 0.3s;
            font-size: 14px;
            white-space: nowrap;
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            <span id="authButtonText">🔐 CITIZEN LOGIN</span>
        </button>
    </div>'''

if old_button in content:
    content = content.replace(old_button, new_buttons)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully added NEW CITIZEN and CITIZEN LOGIN buttons!")
else:
    print("⚠️ Could not find the old button. Let me try a different approach...")
    # Try to find just the div
    if 'id="citizenAuthButton"' in content:
        print("Found the button div, updating...")
        # Replace the entire div
        import re
        pattern = r'<div id="citizenAuthButton".*?</div>'
        content = re.sub(pattern, new_buttons, content, flags=re.DOTALL)
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Successfully updated buttons!")
    else:
        print("❌ Could not find button to replace")
