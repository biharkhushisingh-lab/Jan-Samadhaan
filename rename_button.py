"""
Rename CITIZEN LOGIN button to NEW CITIZEN
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the button text
replacements = [
    ('CITIZEN LOGIN', 'NEW CITIZEN'),
    ('Citizen Login', 'New Citizen'),
]

changes_made = False
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Changed '{old}' to '{new}'")
        changes_made = True

if changes_made:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("\n✅ Successfully renamed button to NEW CITIZEN!")
else:
    print("⚠️ Could not find 'CITIZEN LOGIN' text in index.html")
    print("Searching for similar text...")
    
    # Search for any login-related text
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'login' in line.lower() or 'citizen' in line.lower():
            if 'button' in line.lower() or 'onclick' in line.lower():
                print(f"Line {i}: {line.strip()[:80]}")
