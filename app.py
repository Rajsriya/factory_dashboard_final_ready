from flask import Flask, render_template
import ssl
import smtplib

app = Flask(__name__)

@app.route("/")
def index():
    return "App is running with SSL verification disabled for internal SMTP."

def send_email():
    context = ssl._create_unverified_context()  # WARNING: Only for internal mail servers
    with smtplib.SMTP_SSL("mail.rajsriya.com", 465, context=context) as server:
        server.login("rajsriyahosur@rajsriya.com", "hsr@123")
        server.sendmail("rajsriyahosur@rajsriya.com", "receiver@example.com", "Test Email")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
