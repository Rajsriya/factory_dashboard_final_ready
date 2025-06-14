from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta
import os
import smtplib, ssl
from email.message import EmailMessage

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

EMAIL_SENDER = "rajsriyahosur@rajsriya.com"
EMAIL_PASSWORD = "hsr@123"
SMTP_SERVER = "192.168.221.6"
SMTP_PORT = 465

def classify_status(valid_to_date):
    today = datetime.today().date()
    if pd.isna(valid_to_date):
        return "Unknown"
    if valid_to_date < today:
        return "Expired"
    elif valid_to_date <= today + timedelta(days=30):
        return "Expiring Soon"
    else:
        return "Valid"

def send_alert_email(rows):
    msg = EmailMessage()
    msg['Subject'] = "⚠️ Factory Expiry Alerts"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_SENDER

    message = "Dear Team,\n\nThe following entries are Expiring Soon or Expired:\n\n"
    for r in rows:
        message += "- {} (Valid To: {}, Status: {})\n".format(
            r['Description'], r['Valid To'], r['Status']
        )
    message += "\nRegards,\nRajsriya IT Support\n"
    msg.set_content(message)

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    data = []
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".xlsx"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            df = pd.read_excel(filepath)
            if "Valid To" in df.columns and "Description" in df.columns:
                df["Valid To"] = pd.to_datetime(df["Valid To"], errors="coerce").dt.date
                df["Status"] = df["Valid To"].apply(classify_status)
                data = df.to_dict(orient="records")
                alerts = [row for row in data if row["Status"] in ["Expired", "Expiring Soon"]]
                if alerts:
                    send_alert_email(alerts)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
