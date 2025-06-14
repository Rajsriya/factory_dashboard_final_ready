from flask import Flask, render_template, request
import pandas as pd
import smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)

SMTP_SERVER = "mail.rajsriya.com"
SMTP_PORT = 465
SENDER_EMAIL = "rajsriyahosur@rajsriya.com"
SENDER_PASSWORD = "hsr@123"
RECEIVER_EMAIL = "rajsriyahosur@rajsriya.com"

def send_email(alert_rows):
    if not alert_rows:
        return
    message = "<h3>🔔 Expiry Alert Notification</h3><table border='1' cellpadding='5'><tr><th>Description</th><th>Valid To</th><th>Status</th></tr>"
    for row in alert_rows:
        message += f"<tr><td>{row['Description']}</td><td>{row['Valid To']}</td><td>{row['Status']}</td></tr>"
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
def index():
    data = []
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
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
            send_email(alert_rows)
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)