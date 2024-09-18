import datetime
import json
import smtplib
from email.mime.text import MIMEText
import requests
import hashlib
import cv2
import numpy as np

email_sender = "mbagWeather@outlook.com"
email_recipient = ["Mark.Lysack@gov.mb.ca", "lysackm@myumanitoba.ca", "a_sass3@hotmail.com", "alison.sass@gov.mb.ca"]
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587

email_password = open("program_var.txt", "r").read()


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
    cv2.imshow("img", crop_img)
    cv2.waitKey(0)
    exit()

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
    metadata = get_metadata()

    # check time diff
    live_page_date = get_last_updated_date(metadata)
    date = datetime.datetime.now()
    date_string = date.strftime("%Y-%m-%d %H:%M:%S")
    image_hash = get_curr_image_hash()

    date_delta = date - live_page_date
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
    main()
