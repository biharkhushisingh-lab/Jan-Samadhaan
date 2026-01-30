"""
Remove floating buttons and let user manually add buttons to the portal card
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the floating auth buttons we added
import re

# Pattern to find and remove our auth buttons div
pattern = r'<div id="citizenAuthButtons".*?</div>\s*<script>.*?DOMContentLoaded.*?</script>'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Also try the old pattern
pattern2 = r'<div id="citizenAuthButton".*?</div>\s*<script>.*?DOMContentLoaded.*?</script>'
content = re.sub(pattern2, '', content, flags=re.DOTALL)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Removed floating buttons from top-right corner")
print("\n📝 Now I need to find the Citizen Portal card section...")

# Try to find the portal section
if 'Citizen Portal' in content or 'CITIZEN LOGIN' in content:
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Portal' in line or 'LOGIN' in line:
            print(f"Line {i+1}: {line.strip()[:100]}")
