from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import smtplib, ssl
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'rajsriya_secret'

USERNAME = 'admin'
PASSWORD = 'rajsriya123'

SMTP_SERVER = "mail.rajsriya.com"
SMTP_PORT = 465
SENDER_EMAIL = "rajsriyahosur@rajsriya.com"
SENDER_PASSWORD = "hsr@123"
RECEIVER_EMAIL = "rajsriyahosur@rajsriya.com"

def send_email(alert_df):
    if alert_df.empty:
        return
    message = "<h3>🔔 Expiry Alert Notification</h3><table border='1' cellpadding='5'><tr><th>Description</th><th>Valid To</th>"
    if 'Status' in alert_df.columns:
        message += "<th>Status</th>"
    message += "</tr>"
    for _, row in alert_df.iterrows():
        message += f"<tr><td>{row.get('Description', '')}</td><td>{row.get('Valid To', '')}</td>"
        if 'Status' in row:
            message += f"<td>{row['Status']}</td>"
        message += "</tr>"
    message += "</table><p>Regards,<br><b>Rajsriya IT Support</b></p>"
    msg = MIMEText(message, 'html')
    msg['Subject'] = "Expiry Alerts Summary"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == USERNAME and request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    data = []
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            df['Status'] = 'Unknown'
            today = pd.Timestamp.now().normalize()
            alert_rows = []
            for i, row in df.iterrows():
                try:
                    valid_to = pd.to_datetime(row['Valid To']).normalize()
                    delta = (valid_to - today).days
                    if delta < 0:
                        status = 'Expired'
                    elif delta <= 30:
                        status = 'Expiring Soon'
                    else:
                        status = 'Valid'
                except:
                    status = 'Invalid Date'
                df.at[i, 'Status'] = status
                if status in ['Expired', 'Expiring Soon']:
                    alert_rows.append(row)
            data = df.to_dict(orient='records')
            send_email(pd.DataFrame(alert_rows))
    return render_template('dashboard.html', data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)