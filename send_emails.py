import os
import csv
import json
import smtplib
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# File paths
ENV_FILE = ".env"
SENT_TRACKER_FILE = "emailed_testers.json"

DEFAULT_JOIN_LINK = "https://play.google.com/apps/testing/com.invopocket.quotes"

def load_env():
    """Manually parse .env file to avoid external dependencies like python-dotenv."""
    env_data = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_data[key.strip()] = val.strip().strip('"').strip("'")
    return env_data

def save_env(env_data):
    """Save configuration to .env file."""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("# InvoPocket Tester Email Configuration\n")
        for key, val in env_data.items():
            f.write(f"{key}={val}\n")

def load_sent_emails():
    """Load list of already emailed testers."""
    if os.path.exists(SENT_TRACKER_FILE):
        try:
            with open(SENT_TRACKER_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_sent_emails(sent_emails):
    """Save list of emailed testers to JSON."""
    with open(SENT_TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_emails), f, indent=2)

def get_html_template(name, join_link):
    """Generate professional HTML email template."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>InvoPocket Early Access Invitation</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #000000;
    color: #ffffff;
    margin: 0;
    padding: 0;
  }}
  .container {{
    max-width: 550px;
    margin: 40px auto;
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  }}
  .logo-area {{
    text-align: center;
    margin-bottom: 30px;
  }}
  .logo {{
    font-size: 24px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.5px;
  }}
  .logo span {{
    color: #71717a;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 20px;
    color: #ffffff;
    text-align: center;
  }}
  p {{
    font-size: 15px;
    line-height: 1.6;
    color: #a1a1aa;
    margin-bottom: 24px;
  }}
  .steps {{
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
  }}
  .step-item {{
    margin-bottom: 16px;
    font-size: 14px;
    color: #d4d4d8;
  }}
  .step-item:last-child {{
    margin-bottom: 0;
  }}
  .step-num {{
    color: #ffffff;
    font-weight: 800;
    margin-right: 6px;
  }}
  .btn-area {{
    text-align: center;
    margin-bottom: 30px;
  }}
  .btn {{
    display: inline-block;
    background-color: #ffffff;
    color: #000000 !important;
    text-decoration: none;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 28px;
    border-radius: 8px;
    transition: background 0.2s;
  }}
  .footer {{
    text-align: center;
    font-size: 12px;
    color: #52525b;
    border-top: 1px solid #27272a;
    padding-top: 20px;
    margin-top: 30px;
  }}
  a {{
    color: #ffffff;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="logo-area">
    <div class="logo">Invo<span>Pocket</span></div>
  </div>
  
  <h1>You're Invited to Test InvoPocket!</h1>
  
  <p>Hi {name},</p>
  
  <p>We are excited to invite you as an internal tester for <strong>InvoPocket</strong> on Android. Your account is now whitelisted on Google Play, and you can download the app to start creating invoices and quotations securely.</p>
  
  <div class="steps">
    <div class="step-item">
      <span class="step-num">1.</span> Tap the "Download on Google Play" button below or open the testing link.
    </div>
    <div class="step-item">
      <span class="step-num">2.</span> Make sure you are signed in with the Google Account you registered with.
    </div>
    <div class="step-item">
      <span class="step-num">3.</span> Accept the invite and install the app from the Play Store.
    </div>
  </div>
  
  <div class="btn-area">
    <a href="{join_link}" class="btn" target="_blank">Download on Google Play</a>
  </div>
  
  <p>If you encounter any issues or have feedback to share, feel free to reply directly to this email.</p>
  
  <div class="footer">
    <p>&copy; 2026 InvoPocket. Secure, offline-first invoices.</p>
  </div>
</div>
</body>
</html>
"""

def parse_csv(csv_path):
    """Find and parse name and email columns in the CSV."""
    testers = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        # Detect delimiter (comma or semicolon)
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().has_header(sample) and csv.excel or csv.excel
        if ';' in sample and ',' not in sample:
            reader = csv.reader(f, delimiter=';')
        else:
            reader = csv.reader(f, delimiter=',')
            
        rows = list(reader)
        if not rows:
            return testers
            
        headers = [h.strip().lower() for h in rows[0]]
        
        # Try to locate Name and Email columns
        name_idx, email_idx = -1, -1
        for i, header in enumerate(headers):
            if any(term in header for term in ['name', 'full name', 'fullname']):
                name_idx = i
            if any(term in header for term in ['email', 'email address', 'email_address', 'mail']):
                email_idx = i
                
        # Fallbacks if headers match poorly
        if email_idx == -1:
            # Assume first column that contains '@' in the first data row is email
            for r_idx in range(1, min(len(rows), 5)):
                for c_idx, val in enumerate(rows[r_idx]):
                    if '@' in val:
                        email_idx = c_idx
                        break
                if email_idx != -1:
                    break
                    
        if name_idx == -1:
            # Assume the other column is name
            name_idx = 0 if email_idx != 0 else 1
            
        if email_idx == -1:
            print("Error: Could not locate an Email column in the CSV.")
            return []
            
        # Parse data rows
        for row in rows[1:]:
            if len(row) > max(name_idx, email_idx):
                name = row[name_idx].strip()
                email = row[email_idx].strip()
                if email and '@' in email:
                    # Default name if empty
                    if not name:
                        name = "Tester"
                    testers.append({"name": name, "email": email})
                    
    return testers

def main():
    print("=" * 60)
    print("           InvoPocket - Tester Email Automation")
    print("=" * 60)
    
    # Load configuration
    env = load_env()
    
    # Check SMTP configuration
    smtp_server = env.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(env.get("SMTP_PORT", "465"))
    sender_email = env.get("SENDER_EMAIL", "")
    sender_password = env.get("SENDER_PASSWORD", "")
    join_link = env.get("PLAY_STORE_JOIN_LINK", DEFAULT_JOIN_LINK)
    
    # Prompt user if config is missing
    if not sender_email:
        sender_email = input("Enter your Gmail address: ").strip()
        env["SENDER_EMAIL"] = sender_email
        
    if not sender_password:
        print("\nNote: For Gmail accounts, you MUST use an 'App Password'.")
        print("Set one up at: https://myaccount.google.com/apppasswords")
        sender_password = getpass.getpass("Enter your Gmail App Password: ").strip()
        env["SENDER_PASSWORD"] = sender_password
        
    # Ask if user wants to save configuration
    if not os.path.exists(ENV_FILE) or env.get("SENDER_PASSWORD") != env.get("SENDER_PASSWORD"):
        save_opt = input("\nSave credentials in .env file for future runs? (y/n): ").strip().lower()
        if save_opt == 'y':
            env["SMTP_SERVER"] = smtp_server
            env["SMTP_PORT"] = str(smtp_port)
            env["PLAY_STORE_JOIN_LINK"] = join_link
            save_env(env)
            print("Credentials saved to .env securely.")

    # Get CSV path
    csv_path = ""
    while not csv_path or not os.path.exists(csv_path):
        csv_path = input("\nDrag-and-drop or enter path to Netlify CSV file: ").strip().strip('"').strip("'")
        if not os.path.exists(csv_path):
            print("File not found. Please try again.")

    # Parse CSV
    print("\nParsing CSV file...")
    testers = parse_csv(csv_path)
    if not testers:
        print("No valid testers found in the CSV.")
        return
        
    print(f"Found {len(testers)} total testers in CSV.")
    
    # Load already sent tracker
    sent_emails = load_sent_emails()
    
    # Filter out already sent
    new_testers = [t for t in testers if t["email"] not in sent_emails]
    print(f"Already sent emails: {len(sent_emails)}")
    print(f"New testers to email: {len(new_testers)}")
    
    if not new_testers:
        resend_opt = input("\nNo new testers found. Do you want to resend to ALL testers in the CSV? (y/n): ").strip().lower()
        if resend_opt == 'y':
            new_testers = testers
        else:
            print("Exiting. No emails sent.")
            return

    # Confirm sending
    confirm = input(f"\nReady to send {len(new_testers)} emails using {sender_email}. Proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Start SMTP session
    print("\nConnecting to SMTP server...")
    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(sender_email, sender_password)
        print("Login successful!")
    except Exception as e:
        print(f"Failed to connect or login to SMTP server: {e}")
        return

    # Send emails
    sent_count = 0
    for t in new_testers:
        name = t["name"]
        email = t["email"]
        
        print(f"Sending to {name} <{email}>...", end="", flush=True)
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Invitation: Test InvoPocket on Google Play"
            msg['From'] = f"InvoPocket Team <{sender_email}>"
            msg['To'] = email
            
            # Simple text backup
            text_body = f"Hi {name},\n\nYou are invited to test InvoPocket on Google Play!\n\nOpen this link to install early access:\n{join_link}\n\nSign in with the email {email}.\n\nBest,\nInvoPocket Team"
            html_body = get_html_template(name, join_link)
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send
            server.sendmail(sender_email, email, msg.as_string())
            print(" Sent!")
            
            # Record tracking
            sent_emails.add(email)
            sent_count += 1
        except Exception as e:
            print(f" Failed! Error: {e}")
            
    # Cleanup
    try:
        server.quit()
    except Exception:
        pass
        
    save_sent_emails(sent_emails)
    print(f"\nDone! Successfully sent {sent_count} of {len(new_testers)} invitation emails.")
    print("Testing tracking list has been updated.")

if __name__ == "__main__":
    main()
