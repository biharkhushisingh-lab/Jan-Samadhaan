"""
Revert NEW CITIZEN button to original behavior
Keep CITIZEN LOGIN with modal
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find NEW CITIZEN button and change it back to original onclick
old_new_citizen = 'onclick="authModule.showAuthModal(\'signup\')"'
new_new_citizen = 'onclick="showStep(\'citizen-verification\')"'

if old_new_citizen in content:
    content = content.replace(old_new_citizen, new_new_citizen)
    print("✅ NEW CITIZEN button restored to original behavior")
else:
    print("⚠️ Could not find NEW CITIZEN button with modal onclick")

# Also restore the parent div onclick if needed
old_div = '<div class="role-card">'
new_div = '<div class="role-card" onclick="showStep(\'citizen-verification\')">'

# But only if the button doesn't already have the onclick
if 'showStep(\'citizen-verification\')' not in content:
    content = content.replace(old_div, new_div, 1)  # Only first occurrence
    print("✅ Restored parent div onclick")

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Fixed!")
print("NEW CITIZEN → Shows original full form")
print("CITIZEN LOGIN → Shows simplified modal (phone/email → OTP)")
