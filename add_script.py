"""
Add auth.js script to index.html
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if auth.js is already added
if 'auth.js' in content:
    print("✅ auth.js script already in index.html")
else:
    print("⚠️ auth.js script NOT found, adding it...")
    
    # Add before closing </body> tag
    if '</body>' in content:
        # Find the position
        body_pos = content.rfind('</body>')
        
        # Insert the script tag
        script_tag = '\n    <!-- 🔐 CITIZEN AUTHENTICATION MODULE -->\n    <script src="js/auth.js"></script>\n\n'
        
        content = content[:body_pos] + script_tag + content[body_pos:]
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added auth.js script tag before </body>")
    else:
        print("❌ Could not find </body> tag")

print("\n✅ Now the authModule will be available!")
print("Refresh browser and click buttons - they should open the modal!")
