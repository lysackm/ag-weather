import datetime
import json
import smtplib
from email.mime.text import MIMEText
import requests
import hashlib

email_sender = "mbagWeather@outlook.com"
email_recipient = ["Mark.Lysack@gov.mb.ca", "lysackm@myumanitoba.ca", "a_sass3@hotmail.com", "alison.sass@gov.mb.ca"]
# email_recipient = ["Mark.Lysack@gov.mb.ca"]
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587

email_password = open("program_var.txt", "r").read()


def get_metadata():
    with open("metadata.json") as file:
        return json.load(file)


def has_sent_mail(metadata):
    return metadata["sent_mail"]


def get_curr_image_hash():
    r = requests.get("https://mbagweather.ca/partners/rtmc/Carman12.png")
    new_image = r.content
    # save new file
    with open("new_image.jpg", "wb") as file:
        file.write(new_image)

    with open("new_image.jpg", "r") as file:
        image_hash = hashlib.sha256(new_image).hexdigest()

    return image_hash


def same_image_hashes(metadata):
    old_hash = metadata["image_hash"]
    new_hash = get_curr_image_hash()

    return old_hash == new_hash


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
    two_hours = datetime.timedelta(hours=2)

    if date_delta >= two_hours:
        # check if the hash is different
        if same_image_hashes(metadata):
            # check if an email has already been sent
            if not has_sent_mail(metadata):
                print("sending email")
                send_email(str(live_page_date))
                # sent mail, same, same
                save_metadata("true", metadata["last_updated"], metadata["image_hash"])
        else:
            # has not sent mail, update date, hash is different
            save_metadata("false", date_string, image_hash)
    else:
        if not same_image_hashes(metadata):
            # not sent mail, update date, update hash
            save_metadata("false", date_string, image_hash)


if __name__ == "__main__":
    main()
