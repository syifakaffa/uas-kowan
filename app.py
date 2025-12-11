from flask import Flask, render_template, request, session, redirect, url_for, flash
import math
import secrets
import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret key for session - load from .env atau generate
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Email configuration - Simple way
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

# In-memory storage for OTP codes
otp_storage = {}

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(secrets.randbelow(900000) + 100000)

def cleanup_expired_otps():
    """Remove expired OTPs (5 minutes expiry)"""
    current_time = time.time()
    expired_keys = [email for email, data in otp_storage.items() 
                   if current_time - data['timestamp'] > 300]
    for key in expired_keys:
        del otp_storage[key]

def send_otp_email(to_email, otp):
    """Send OTP via email using Gmail SMTP"""
    try:
        # Validate email configuration
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            print("Email not configured - OTP will be shown in console")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Login OTP - Circle Calculator'
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        
        # HTML email body
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
              <h2 style="color: #2c3e50; margin-bottom: 20px;">Circle Calculator - Login OTP</h2>
              <p style="color: #555; font-size: 15px;">Your One-Time Password (OTP) is:</p>
              <div style="background-color: #f8f9fa; padding: 20px; border-radius: 4px; text-align: center; margin: 20px 0; border: 2px solid #2c3e50;">
                <h1 style="color: #2c3e50; font-size: 36px; letter-spacing: 8px; margin: 0; font-family: monospace;">
                  {otp}
                </h1>
              </div>
              <p style="color: #555; font-size: 14px;">
                This code will expire in <strong>5 minutes</strong>.
              </p>
              <p style="color: #555; font-size: 14px;">
                If you didn't request this code, please ignore this email.
              </p>
              <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
              <p style="color: #999; font-size: 12px; margin: 0;">
                This is an automated email. Please do not reply.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Plain text version
        text = f"""
Circle Calculator - Login OTP

Your One-Time Password (OTP) is: {otp}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send via Gmail SMTP (port 465 with SSL)
        print(f"\nSending OTP to {to_email}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed - Check SMTP_EMAIL and SMTP_PASSWORD")
        print("Make sure you're using App Password, not regular Gmail password")
        return False
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/')
def index():
    """Home page - redirect based on login status"""
    if 'user_email' in session:
        return redirect(url_for('calculator'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Passwordless login - generate and send OTP"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Email tidak boleh kosong!', 'error')
            return render_template('login.html')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            flash('Format email tidak valid!', 'error')
            return render_template('login.html')
        
        cleanup_expired_otps()
        otp = generate_otp()
        otp_storage[email] = {
            'otp': otp,
            'timestamp': time.time()
        }
        
        print(f"\n{'='*60}")
        print(f"OTP for {email}: {otp}")
        print(f"{'='*60}")
        
        # Try to send OTP via email
        if send_otp_email(email, otp):
            flash(f'OTP telah dikirim ke {email}', 'success')
            flash('Silakan cek inbox atau folder spam', 'success')
        else:
            # Fallback: show OTP in flash message for demo
            flash(f'Demo mode: OTP = {otp}', 'success')
            flash('Setup email di .env untuk kirim OTP via email', 'error')
        
        return redirect(url_for('verify_otp', email=email))
            
    return render_template('login.html')

@app.route('/verify/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    """Verify OTP code"""
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        cleanup_expired_otps()
        
        if email in otp_storage:
            stored_data = otp_storage[email]
            
            if stored_data['otp'] == entered_otp:
                # OTP is correct
                session['user_email'] = email
                del otp_storage[email]
                flash('Login berhasil!', 'success')
                return redirect(url_for('calculator'))
            else:
                flash('OTP salah! Silakan cek kembali.', 'error')
        else:
            flash('OTP expired atau tidak ditemukan!', 'error')
            flash('Silakan login ulang', 'error')
            return redirect(url_for('login'))
    
    return render_template('verify.html', email=email)

@app.route('/calculator')
def calculator():
    """Circle calculator page - requires authentication"""
    if 'user_email' not in session:
        flash('Silakan login terlebih dahulu', 'error')
        return redirect(url_for('login'))
    return render_template('calculator.html', user_email=session['user_email'])

@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculate circle area and circumference"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    try:
        radius = float(request.form.get('radius', 0))
        if radius <= 0:
            flash('Jari-jari harus lebih besar dari 0!', 'error')
            return redirect(url_for('calculator'))
        
        area = math.pi * radius ** 2
        circumference = 2 * math.pi * radius
        
        return render_template('calculator.html', 
                             user_email=session['user_email'],
                             radius=radius,
                             area=round(area, 2),
                             circumference=round(circumference, 2))
    except ValueError:
        flash('Input tidak valid! Masukkan angka yang benar.', 'error')
        return redirect(url_for('calculator'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user_email', None)
    flash('Anda telah logout', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Circle Calculator Application")
    print("="*60)
    if SMTP_EMAIL and SMTP_PASSWORD:
        print(f"Email: {SMTP_EMAIL}")
        print("Email sending: ENABLED")
    else:
        print("Email sending: DISABLED (demo mode)")
        print("Set SMTP_EMAIL and SMTP_PASSWORD in .env to enable")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)