"""
Debug and fix button functionality
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Checking button onclick handlers...")

# Find NEW CITIZEN button
if 'authModule.showAuthModal' in content:
    count = content.count('authModule.showAuthModal')
    print(f"✅ Found {count} references to authModule.showAuthModal")
else:
    print("❌ authModule.showAuthModal NOT found in index.html")

# Check if auth.js script is present
if '<script src="js/auth.js"></script>' in content:
    print("✅ auth.js script tag found")
elif 'auth.js' in content:
    print("⚠️ auth.js mentioned but might not be properly linked")
else:
    print("❌ auth.js NOT found")

# Let's add a simpler initialization check
# Find the script tag and add initialization check
if '</body>' in content and 'auth.js' in content:
    # Add a check script after auth.js loads
    check_script = '''
    <script>
        // Check if authModule loaded
        window.addEventListener('DOMContentLoaded', function() {
            if (typeof authModule === 'undefined') {
                console.error('❌ authModule not loaded! Check if js/auth.js exists');
                alert('Authentication module failed to load. Please refresh the page.');
            } else {
                console.log('✅ authModule loaded successfully');
            }
        });
    </script>
'''
    
    if 'authModule not loaded' not in content:
        body_pos = content.rfind('</body>')
        content = content[:body_pos] + check_script + '\n' + content[body_pos:]
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ Added authModule check script")
        print("Now refresh browser and check console (F12) for errors")

print("\nTo test:")
print("1. Refresh browser")
print("2. Press F12 to open console")
print("3. Look for '✅ authModule loaded successfully' message")
print("4. Click buttons and check for errors")
