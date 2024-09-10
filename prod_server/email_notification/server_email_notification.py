import datetime
import json
import smtplib
from email.mime.text import MIMEText
import requests

email_sender = "mbagWeather@outlook.com"
email_recipient = ["Mark.Lysack@gov.mb.ca", "lysackm@myumanitoba.ca", "a_sass3@hotmail.com", "alison.sass@gov.mb.ca"]
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587

email_password = open("program_var.txt", "r").read()


def has_sent_mail():
    with open("metadata.json") as file:
        metadata = json.load(file)
        sent_mail = metadata["sent_mail"]
    return sent_mail


def get_curr_date():
    r = requests.get("https://mbagweather.ca/partners/rtmc/Current.png")
    return datetime.datetime.strptime(r.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z")


def save_metadata(sent_mail):
    metadata = json.loads('{ "sent_mail": ' + sent_mail + ' }')
    with open("metadata.json", "w") as file:
        json.dump(metadata, file)


def send_email(date):
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_sender, email_password)

        for recipient in email_recipient:
            msg = MIMEText('Ag Weather server seems to be down, last reported update at ' + date)
            msg['Subject'] = 'Ag Weather prod server down'
            msg['From'] = email_sender
            msg['To'] = recipient
            server.sendmail(email_sender, recipient, msg.as_string())


def main():
    live_page_date = get_curr_date()
    date = datetime.datetime.now()

    date_delta = date - live_page_date
    two_hours = datetime.timedelta(hours=2)

    if date_delta >= two_hours:
        if not has_sent_mail():
            print("sending email")
            send_email(str(live_page_date))
            save_metadata("true")
    else:
        save_metadata("false")


if __name__ == "__main__":
    main()
