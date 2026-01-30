"""
Fix the modal to show only ONE field for CITIZEN LOGIN
"""

with open('js/auth.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the showAuthModal method and update it
old_show = '''    // Show authentication modal
    showAuthModal(mode = 'signin') {
        const modal = this.createAuthModal(mode);
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }'''

new_show = '''    // Show authentication modal
    showAuthModal(mode = 'signin') {
        this.mode = mode;
        const modal = this.createAuthModal(mode);
        document.body.appendChild(modal);
        modal.style.display = 'flex';
        
        // Set initial UI state based on mode
        setTimeout(() => {
            const emailGroup = document.getElementById('emailGroup');
            const phoneLabel = document.getElementById('phoneLabel');
            const authPhone = document.getElementById('authPhone');
            
            if (mode === 'signin') {
                // CITIZEN LOGIN - hide email field
                if (emailGroup) emailGroup.style.display = 'none';
                if (phoneLabel) phoneLabel.textContent = '📱 Phone Number or Email';
                if (authPhone) {
                    authPhone.placeholder = 'Enter your phone or email';
                    authPhone.removeAttribute('maxlength');
                }
                
                // Make signin tab active
                const tabs = document.querySelectorAll('.auth-tab');
                tabs.forEach(tab => {
                    if (tab.textContent.includes('Sign In')) {
                        tab.classList.add('active');
                    } else {
                        tab.classList.remove('active');
                    }
                });
            } else {
                // SIGNUP - show both fields
                if (emailGroup) emailGroup.style.display = 'block';
                if (phoneLabel) phoneLabel.textContent = '📱 Mobile Number';
                if (authPhone) {
                    authPhone.placeholder = 'Enter 10-digit mobile';
                    authPhone.setAttribute('maxlength', '10');
                }
                
                // Make signup tab active
                const tabs = document.querySelectorAll('.auth-tab');
                tabs.forEach(tab => {
                    if (tab.textContent.includes('Sign Up')) {
                        tab.classList.add('active');
                    } else {
                        tab.classList.remove('active');
                    }
                });
            }
        }, 10);
    }'''

if old_show in content:
    content = content.replace(old_show, new_show)
    print("✅ Updated showAuthModal to initialize UI correctly")
else:
    print("⚠️ Could not find showAuthModal method")

# Write back
with open('js/auth.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Fixed! Now:")
print("  CITIZEN LOGIN → Shows ONLY 'Phone or Email' field")
print("  NEW CITIZEN → Shows both Phone AND Email fields")
