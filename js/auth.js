// ============================================
// 🔐 CITIZEN AUTHENTICATION MODULE
// Handles Sign In/Sign Up with OTP verification
// ============================================

class CitizenAuth {
    constructor() {
        this.currentPhone = null;
        this.currentEmail = null;
        this.otpSent = false;
        this.citizenData = null;
    }

    // Show authentication modal
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
    }

    // Create authentication modal UI
    createAuthModal(mode) {
        const modal = document.createElement('div');
        modal.id = 'authModal';
        modal.innerHTML = `
            <style>
                #authModal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.7);
                    z-index: 10000;
                    justify-content: center;
                    align-items: center;
                }
                .auth-container {
                    background: white;
                    border-radius: 16px;
                    padding: 40px;
                    max-width: 450px;
                    width: 90%;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                .auth-header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .auth-header h2 {
                    color: #1f2937;
                    margin-bottom: 10px;
                }
                .auth-tabs {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 30px;
                }
                .auth-tab {
                    flex: 1;
                    padding: 12px;
                    border: 2px solid #e5e7eb;
                    background: white;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s;
                }
                .auth-tab.active {
                    background: linear-gradient(135deg, #6366f1, #8b5cf6);
                    color: white;
                    border-color: #6366f1;
                }
                .auth-form-group {
                    margin-bottom: 20px;
                }
                .auth-form-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                    color: #374151;
                }
                .auth-form-group input {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 16px;
                    transition: border-color 0.3s;
                }
                .auth-form-group input:focus {
                    outline: none;
                    border-color: #6366f1;
                }
                .auth-btn {
                    width: 100%;
                    padding: 14px;
                    background: linear-gradient(135deg, #6366f1, #8b5cf6);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .auth-btn:hover {
                    transform: translateY(-2px);
                }
                .auth-btn:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                .auth-message {
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-weight: 500;
                }
                .auth-message.success {
                    background: #d1fae5;
                    color: #065f46;
                }
                .auth-message.error {
                    background: #fee2e2;
                    color: #991b1b;
                }
                .auth-close {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    font-size: 28px;
                    cursor: pointer;
                    color: #6b7280;
                }
                #otpSection {
                    display: none;
                }
                .otp-timer {
                    text-align: center;
                    margin-top: 15px;
                    color: #6b7280;
                    font-size: 14px;
                }
                .resend-link {
                    color: #6366f1;
                    cursor: pointer;
                    text-decoration: underline;
                }
            </style>
            <div class="auth-container">
                <span class="auth-close" onclick="document.getElementById('authModal').remove()">×</span>
                <div class="auth-header">
                    <h2>🔐 Citizen Login</h2>
                    <p style="color: #6b7280;">Secure access with OTP</p>
                </div>
                
                <div id="authMessage"></div>

                <!-- Phone & Email Section -->
                <div id="phoneSection">
                    <div class="auth-form-group">
                        <label id="phoneLabel">📱 Mobile Number</label>
                        <input type="tel" id="authPhone" placeholder="Enter 10-digit mobile" maxlength="10">
                    </div>
                    <div class="auth-form-group" id="emailGroup">
                        <label>📧 Email Address</label>
                        <input type="email" id="authEmail" placeholder="your.email@example.com">
                    </div>
                    <button class="auth-btn" onclick="authModule.sendOTP()">Send OTP</button>
                </div>

                <!-- OTP Verification Section -->
                <div id="otpSection">
                    <div class="auth-form-group">
                        <label>🔢 Enter 6-Digit OTP</label>
                        <input type="text" id="authOTP" placeholder="Enter OTP" maxlength="6">
                    </div>
                    <button class="auth-btn" onclick="authModule.verifyOTP()">Verify & Continue</button>
                    <div class="otp-timer">
                        OTP expires in <span id="otpTimer">5:00</span> minutes
                        <br><span class="resend-link" onclick="authModule.resendOTP()">Resend OTP</span>
                    </div>
                </div>

                <!-- Additional Info Section (for new users) -->
                <div id="signupSection" style="display: none;">
                    <div class="auth-form-group">
                        <label>👤 Full Name</label>
                        <input type="text" id="authName" placeholder="Your full name">
                    </div>
                    <div class="auth-form-group">
                        <label>🏠 Address</label>
                        <textarea id="authAddress" rows="3" style="width:100%; padding:12px; border-radius:8px; border:2px solid #e5e7eb;" placeholder="Your address"></textarea>
                    </div>
                    <button class="auth-btn" onclick="authModule.completeSignup()">Complete Registration</button>
                </div>
            </div>
        `;
        return modal;
    }

    // Switch between Sign In and Sign Up tabs
    switchTab(mode) {
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
        this.mode = mode;

        // Update UI based on mode
        const emailGroup = document.getElementById('emailGroup');
        const phoneLabel = document.getElementById('phoneLabel');
        const authPhone = document.getElementById('authPhone');

        if (mode === 'signin') {
            // CITIZEN LOGIN - hide email field
            if (emailGroup) emailGroup.style.display = 'none';
            if (phoneLabel) phoneLabel.textContent = '📱 Phone Number or Email';
            if (authPhone) authPhone.placeholder = 'Enter your phone or email';
        } else {
            // NEW CITIZEN - show email field
            if (emailGroup) emailGroup.style.display = 'block';
            if (phoneLabel) phoneLabel.textContent = '📱 Mobile Number';
            if (authPhone) authPhone.placeholder = 'Enter 10-digit mobile';
        }
    }

    // Send OTP
    async sendOTP() {
        const phone = document.getElementById('authPhone').value.trim();
        const email = document.getElementById('authEmail').value.trim();

        // For SIGN IN mode - simplified flow (just phone OR email)
        if (this.mode === 'signin') {
            const identifier = phone || email;

            if (!identifier) {
                this.showMessage('Please enter your phone number or email', 'error');
                return;
            }

            try {
                this.showMessage('Checking your account...', 'success');

                // Check if citizen exists
                const checkResponse = await fetch('/api/citizen/check-exists', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: identifier })
                });

                const checkData = await checkResponse.json();

                if (checkData.success && checkData.exists) {
                    // User exists! Get their email and send OTP
                    this.currentPhone = identifier;
                    this.currentEmail = checkData.citizen.email;

                    this.showMessage('Sending OTP to ' + this.currentEmail + '...', 'success');

                    const response = await fetch('/api/citizen/send-otp', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            phone: this.currentPhone,
                            email: this.currentEmail,
                            purpose: 'signin'
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.showMessage('✅ OTP sent! Check ' + this.currentEmail, 'success');
                        document.getElementById('phoneSection').style.display = 'none';
                        document.getElementById('otpSection').style.display = 'block';
                        this.startOTPTimer();
                    } else {
                        this.showMessage('❌ ' + data.message, 'error');
                    }
                } else {
                    this.showMessage('❌ Account not found. Please click "NEW CITIZEN" to register.', 'error');
                    setTimeout(() => {
                        document.getElementById('authModal').remove();
                    }, 3000);
                }
            } catch (error) {
                this.showMessage('❌ Error checking account. Please try again.', 'error');
            }
            return;
        }

        // For SIGN UP mode - need both phone and email
        if (!phone || phone.length !== 10) {
            this.showMessage('Please enter a valid 10-digit mobile number', 'error');
            return;
        }

        if (!email || !email.includes('@')) {
            this.showMessage('Please enter a valid email address', 'error');
            return;
        }

        this.currentPhone = phone;
        this.currentEmail = email;

        try {
            this.showMessage('Sending OTP...', 'success');
            const response = await fetch('/api/citizen/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: phone,
                    email: email,
                    purpose: this.mode || 'signin'
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('✅ OTP sent to ' + email, 'success');
                document.getElementById('phoneSection').style.display = 'none';
                document.getElementById('otpSection').style.display = 'block';
                this.startOTPTimer();
            } else {
                this.showMessage('❌ ' + data.message, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Error sending OTP. Please try again.', 'error');
        }
    }

    // Helper to switch to signup mode
    switchToSignup() {
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(tab => {
            if (tab.textContent.includes('Sign Up')) {
                tab.click();
            }
        });
    }

    // Verify OTP
    async verifyOTP() {
        const otp = document.getElementById('authOTP').value.trim();

        if (!otp || otp.length !== 6) {
            this.showMessage('Please enter a valid 6-digit OTP', 'error');
            return;
        }

        try {
            this.showMessage('Verifying OTP...', 'success');
            const response = await fetch('/api/citizen/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: this.currentPhone,
                    otp: otp
                })
            });

            const data = await response.json();

            if (data.success) {
                if (data.new_user) {
                    this.showMessage('✅ OTP verified! Please click "NEW CITIZEN" to complete registration.', 'success');
                    setTimeout(() => {
                        document.getElementById('authModal').remove();
                        showStep('citizen-verification');
                    }, 3000);
                } else {
                    // Existing user - login successful
                    this.citizenData = data.citizen;
                    this.showMessage('✅ Login successful! Welcome back, ' + data.citizen.name, 'success');
                    setTimeout(() => {
                        this.onLoginSuccess(data.citizen);
                    }, 1500);
                }
            } else {
                this.showMessage('❌ ' + data.message, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Error verifying OTP. Please try again.', 'error');
        }
    }

    // Complete signup for new users
    async completeSignup() {
        const name = document.getElementById('authName').value.trim();
        const address = document.getElementById('authAddress').value.trim();

        if (!name) {
            this.showMessage('Please enter your name', 'error');
            return;
        }

        try {
            this.showMessage('Creating your account...', 'success');
            const response = await fetch('/api/citizen/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: this.currentPhone,
                    name: name,
                    email: this.currentEmail,
                    address: address
                })
            });

            const data = await response.json();

            if (data.success) {
                this.citizenData = data.citizen;
                this.showMessage('✅ Registration successful! Welcome, ' + name, 'success');
                setTimeout(() => {
                    this.onLoginSuccess(data.citizen);
                }, 1500);
            } else {
                this.showMessage('❌ ' + data.message, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Error completing registration. Please try again.', 'error');
        }
    }

    // Resend OTP
    async resendOTP() {
        await this.sendOTP();
    }

    // OTP Timer
    startOTPTimer() {
        let timeLeft = 300; // 5 minutes
        const timerElement = document.getElementById('otpTimer');

        const timer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

            if (timeLeft <= 0) {
                clearInterval(timer);
                timerElement.textContent = 'Expired';
            }
            timeLeft--;
        }, 1000);
    }

    // Show message
    showMessage(message, type) {
        const messageDiv = document.getElementById('authMessage');
        messageDiv.className = `auth-message ${type}`;
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';
    }

    // On successful login - override this in your HTML
    onLoginSuccess(citizen) {
        // Store citizen data in localStorage
        localStorage.setItem('citizenData', JSON.stringify(citizen));

        // Close modal
        document.getElementById('authModal').remove();

        // Auto-fill form if citizen portal
        const nameField = document.querySelector('input[name="citizen_name"]');
        const emailField = document.querySelector('input[name="citizen_email"]');
        const phoneField = document.querySelector('input[name="citizen_phone"]');
        const addressField = document.querySelector('textarea[name="citizen_address"]');

        if (nameField) nameField.value = citizen.name || '';
        if (emailField) emailField.value = citizen.email || '';
        if (phoneField) phoneField.value = citizen.phone || '';
        if (addressField) addressField.value = citizen.address || '';

        // Show welcome message
        alert('Welcome back, ' + citizen.name + '! Your details have been filled automatically.');
    }
}

// Initialize global auth module
const authModule = new CitizenAuth();

// Auto-fill form if user is already logged in
window.addEventListener('DOMContentLoaded', function () {
    const citizenData = localStorage.getItem('citizenData');
    if (citizenData) {
        const citizen = JSON.parse(citizenData);
        const nameField = document.querySelector('input[name="citizen_name"]');
        if (nameField && !nameField.value) {
            // Only auto-fill if fields are empty
            authModule.onLoginSuccess(citizen);
        }
    }
});
