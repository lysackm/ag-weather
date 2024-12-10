import base64
import datetime
import json
from email.mime.text import MIMEText
import requests
import hashlib
import cv2
import numpy as np
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient import discovery

email_sender = "mbagweather1@gmail.com"
email_recipient = ["Mark.Lysack@gov.mb.ca", "lysackm@myumanitoba.ca", "a_sass3@hotmail.com", "alison.sass@gov.mb.ca"]
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Gmail API Python Send Email"


def get_metadata():
    with open("metadata.json") as file:
        return json.load(file)


def has_sent_mail(metadata):
    return metadata["sent_mail"]


def get_curr_image_hash():
    r = requests.get("https://mbagweather.ca/partners/rtmc/Inwood516.png")
    new_image = r.content

    arr = np.asarray(bytearray(new_image), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # crop the image so only the header appears. Only should change if the time changes on the chart
    crop_img = img[0:60, :]

    image_hash = hashlib.sha256(crop_img).hexdigest()

    return image_hash


def save_metadata(sent_mail, last_updated, image_hash):
    print()
    metadata = json.loads('{ "sent_mail": ' + sent_mail +
                          ', "last_updated": "' + last_updated +
                          '", "image_hash": "' + image_hash + '" }')
    with open("metadata.json", "w") as file:
        json.dump(metadata, file)


def get_last_updated_date(metadata):
    date_string = metadata["last_updated"]
    return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def refresh_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def make_email(recipient, email_sender, date, subject="", message=""):
    if message == "":
        msg = MIMEText('Ag Weather server seems to be down, last reported update at ' + date)
    else:
        msg = MIMEText(message + ' Message sent on: ' + date)

    if subject == "":
        msg['Subject'] = 'Ag Weather prod server down'
    else:
        msg['Subject'] = subject
    msg['From'] = email_sender
    msg['To'] = recipient
    return {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}


# deprecated
def send_email(date, subject="", message=""):
    credentials = get_credentials()
    service = discovery.build('gmail', 'v1', credentials=credentials)

    for recipient in email_recipient:
        msg = make_email(recipient, email_sender, date, subject, message)
        service.users().messages().send(userId=email_sender, body=msg).execute()


def send_friday_email():
    global email_recipient
    email_recipient = ["Mark.Lysack@gov.mb.ca", "alison.sass@gov.mb.ca"]
    message = "As of now the prod server notification is still operational"
    subject = "Prod email still working"

    today = datetime.datetime.today()
    weekday = today.weekday()
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute

    if weekday == 4 and hour == 8 and 0 <= minute <= 15:
        send_email(str(today), subject, message)


def main():
    metadata = get_metadata()

    # check time diff
    live_page_date = get_last_updated_date(metadata)
    date = datetime.datetime.now()
    date_string = date.strftime("%Y-%m-%d %H:%M:%S")
    image_hash = get_curr_image_hash()

    date_delta = date - live_page_date
    # change the time_threshold to change how long the program should wait before sending an email notifying that
    # the prod server is down
    time_threshold = datetime.timedelta(minutes=19)

    if image_hash != metadata["image_hash"]:
        # dont send mail, update data
        save_metadata("false", date_string, image_hash)
    else:
        if date_delta >= time_threshold and not metadata["sent_mail"]:
            print("sending email")
            send_email(str(live_page_date))
            save_metadata("true", metadata["last_updated"], metadata["image_hash"])


if __name__ == "__main__":
    refresh_credentials()
    main()
    send_friday_email()
