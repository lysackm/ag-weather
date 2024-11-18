import smtplib
from email.mime.text import MIMEText


def send_email(recipients: list, subject: str, message: str, sender="mbagWeather@outlook.com"):
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587

    email_password = open("program_var.txt", "r").read()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, email_password)

        for recipient in recipients:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            server.sendmail(sender, recipient, msg.as_string())
