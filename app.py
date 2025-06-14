from flask import Flask, render_template, request, redirect
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

def send_alert_email(alerts):
    if not alerts:
        return
    body = "<h3>🔔 Expiry Alerts</h3><ul>"
    for item in alerts:
        body += f"<li><b>{item['Description']}</b> expiring on {item['Valid To']}</li>"
    body += "</ul><p>Regards,<br>Rajsriya IT Support</p>"
    msg = MIMEText(body, 'html')
    msg['Subject'] = 'Expiry Alert - Action Needed'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

@app.route("/", methods=["GET", "POST"])
def index():
    alerts = []
    data = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            df = pd.read_excel(file)
            today = pd.Timestamp.now().normalize()
            for _, row in df.iterrows():
                try:
                    valid_to = pd.to_datetime(row["Valid To"]).normalize()
                    delta = (valid_to - today).days
                    status = "Valid"
                    if delta <= 30:
                        status = "Expiring Soon"
                        alerts.append(row)
                    df.at[_, "Status"] = status
                except:
                    df.at[_, "Status"] = "Invalid Date"
            data = df.to_dict(orient="records")
            send_alert_email(alerts)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)