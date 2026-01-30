"""
Embed auth.js directly into index.html to avoid 404 error
"""

# Read auth.js content
with open('js/auth.js', 'r', encoding='utf-8') as f:
    auth_content = f.read()

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Remove the external script tag and replace with inline script
old_script_tag = '<script src="js/auth.js"></script>'

if old_script_tag in html_content:
    new_inline_script = f'<script>\n{auth_content}\n</script>'
    html_content = html_content.replace(old_script_tag, new_inline_script)
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Embedded auth.js directly into index.html!")
    print("This fixes the 404 error you saw in the console.")
else:
    print("⚠️ Could not find external script tag")

print("\n✅ Now refresh browser and buttons should work!")
