import smtplib, ssl
import log

import smtplib
from pathlib import Path
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

# takes a subject line and an attachment to email
def run(subject, files=[]):
    log.main("send email")

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "agweatherhistoricaldb@gmail.com"
    password = "consecutivevaluecheck917"
    receiver_email = "Timi.Ojo@gov.mb.ca"

    message = "This is an automated message regarding the historical weather database.\n\n"

    msg = MIMEMultipart()

    msg = MIMEMultipart()
    msg['From'] = "Mb Ag Weather Historical Database"
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(Path(path).name))
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())