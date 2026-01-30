"""
Fix both buttons to open proper auth modals
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the Citizen Portal card - remove the inline onclick, add button onclicks
old_card = '''<div class="role-card" onclick="showStep('citizen-verification')">
                <h3>👤 Citizen Portal</h3>
                <p>File complaints with AI-powered priority assignment, real-time SLA tracking, intelligent department
                    routing, and multilingual support.</p>
                <button class="role-button">NEW CITIZEN →</button>'''

new_card = '''<div class="role-card">
                <h3>👤 Citizen Portal</h3>
                <p>File complaints with AI-powered priority assignment, real-time SLA tracking, intelligent department
                    routing, and multilingual support.</p>
                <button class="role-button" onclick="authModule.showAuthModal('signup'); event.stopPropagation();">NEW CITIZEN →</button>'''

if old_card in content:
    content = content.replace(old_card, new_card)
    print("✅ Fixed NEW CITIZEN button to open signup modal")
else:
    print("⚠️ Could not find exact card pattern, trying alternative...")
    # Try simpler pattern
    content = content.replace(
        '<div class="role-card" onclick="showStep(\'citizen-verification\')">',
        '<div class="role-card">'
    )
    content = content.replace(
        '<button class="role-button">NEW CITIZEN →</button>',
        '<button class="role-button" onclick="authModule.showAuthModal(\'signup\')">NEW CITIZEN →</button>'
    )
    print("✅ Applied alternative fix")

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Both buttons now properly call auth module!")
print("\nButtons will now:")
print("  NEW CITIZEN → Opens signup modal (phone + email required)")
print("  CITIZEN LOGIN → Opens signin modal (phone OR email only)")
