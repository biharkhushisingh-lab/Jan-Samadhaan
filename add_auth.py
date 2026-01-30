"""
Script to add authentication module to index.html
"""

# Read the file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Code to inject before </body>
auth_code = '''
    <!-- 🔐 CITIZEN AUTHENTICATION MODULE -->
    <script src="js/auth.js"></script>
    
    <!-- Floating Sign In/Sign Up Button -->
    <div id="citizenAuthButton" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <button id="mainAuthBtn" onclick="authModule.showAuthModal('signin')" style="
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            transition: all 0.3s;
            font-size: 14px;
        ">
            <span id="authButtonText">🔐 Sign In / Sign Up</span>
        </button>
    </div>

    <script>
        // Handle logged-in state
        window.addEventListener('DOMContentLoaded', function() {
            const citizenData = localStorage.getItem('citizenData');
            const authBtn = document.getElementById('mainAuthBtn');
            const btnText = document.getElementById('authButtonText');
            
            if (citizenData) {
                try {
                    const citizen = JSON.parse(citizenData);
                    const firstName = citizen.name ? citizen.name.split(' ')[0] : 'User';
                    btnText.innerHTML = '👋 Hi, ' + firstName;
                    
                    // Change button to logout
                    authBtn.onclick = function() {
                        if (confirm('Logout from Jan Samadhaan?')) {
                            localStorage.removeItem('citizenData');
                            location.reload();
                        }
                    };
                    
                    // Add hover effect
                    authBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                } catch (e) {
                    console.error('Error loading citizen data:', e);
                }
            }
        });
    </script>

</body>'''

# Replace </body> with our code
if '</body>' in content:
    content = content.replace('</body>', auth_code)
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully added authentication module to index.html!")
else:
    print("❌ Could not find </body> tag in index.html")
