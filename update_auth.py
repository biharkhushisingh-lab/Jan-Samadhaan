"""
Update auth.js to hide email field in signin mode
"""

with open('js/auth.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the switchTab method
old_switch = '''    // Switch between Sign In and Sign Up tabs
    switchTab(mode) {
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
        this.mode = mode;
    }'''

new_switch = '''    // Switch between Sign In and Sign Up tabs
    switchTab(mode) {
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
        this.mode = mode;
        
        // Update UI based on mode
        const emailGroup = document.getElementById('emailGroup');
        const phoneLabel = document.getElementById('phoneLabel');
        const authPhone = document.getElementById('authPhone');
        
        if (mode === 'signin') {
            // CITIZEN LOGIN - hide email field
            if (emailGroup) emailGroup.style.display = 'none';
            if (phoneLabel) phoneLabel.textContent = '📱 Phone Number or Email';
            if (authPhone) authPhone.placeholder = 'Enter your phone or email';
        } else {
            // NEW CITIZEN - show email field
            if (emailGroup) emailGroup.style.display = 'block';
            if (phoneLabel) phoneLabel.textContent = '📱 Mobile Number';
            if (authPhone) authPhone.placeholder = 'Enter 10-digit mobile';
        }
    }'''

if old_switch in content:
    content = content.replace(old_switch, new_switch)
    print("✅ Updated switchTab method")
else:
    print("⚠️ Could not find exact switchTab method")

# Also update the HTML template to add IDs
old_phone_section = '''                <div id="phoneSection">
                    <div class="auth-form-group">
                        <label>📱 Mobile Number</label>
                        <input type="tel" id="authPhone" placeholder="Enter 10-digit mobile" maxlength="10">
                    </div>
                    <div class="auth-form-group">
                        <label>📧 Email Address</label>
                        <input type="email" id="authEmail" placeholder="your.email@example.com">
                    </div>'''

new_phone_section = '''                <div id="phoneSection">
                    <div class="auth-form-group">
                        <label id="phoneLabel">📱 Mobile Number</label>
                        <input type="tel" id="authPhone" placeholder="Enter 10-digit mobile" maxlength="10">
                    </div>
                    <div class="auth-form-group" id="emailGroup">
                        <label>📧 Email Address</label>
                        <input type="email" id="authEmail" placeholder="your.email@example.com">
                    </div>'''

if old_phone_section in content:
    content = content.replace(old_phone_section, new_phone_section)
    print("✅ Added IDs to form fields")
else:
    print("⚠️  Could not find phone section HTML")

# Write back
with open('js/auth.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Auth.js updated successfully!")
print("\nNow CITIZEN LOGIN will:")
print("  - Show only ONE field (phone OR email)")
print("  - Check if account exists")
print("  - Send OTP to registered email")
print("  - Login without re-entering details!")
