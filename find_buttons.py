"""
Find CITIZEN LOGIN and NEW CITIZEN buttons in index.html
"""

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Searching for NEW CITIZEN and login-related buttons...\n")

for i, line in enumerate(lines, 1):
    if 'NEW CITIZEN' in line or ('citizen' in line.lower() and 'login' in line.lower()):
        print(f"Line {i}: {line.strip()[:120]}")
        # Show context
        if i > 1:
            print(f"  Line {i-1}: {lines[i-2].strip()[:100]}")
        if i < len(lines):
            print(f"  Line {i+1}: {lines[i].strip()[:100]}")
        print()
