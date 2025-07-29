import email
import imaplib
import smtplib
from datetime import datetime
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import chardet


def get_header_content(raw, key):
    header = raw.get(key)
    if header:
        content, encoding = decode_header(header)[0]
        if encoding:
            content = content.decode(encoding)
        return content
    return None


class Email:
    def __init__(self, address, password, smtp_host, smtp_port, imap_host, imap_port, sender_name=None, timeout=10):
        self.address = address
        self.password = password
        self.smtp_server = smtp_host
        self.smtp_port = smtp_port
        self.imap_server = imap_host
        self.imap_port = imap_port
        self.sender_name = sender_name
        self.timeout = timeout

    def send_text(self, to: str, subject: str, text: str):
        msg = MIMEMultipart()
        msg["From"] = f"{self.sender_name or self.address} <{self.address}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain", "utf-8"))

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout) as connection:
            connection.login(self.address, self.password)
            connection.sendmail(self.address, to, msg.as_string())

    def search_ids(self, count: int, *criteria: str):
        with imaplib.IMAP4_SSL(self.imap_server, self.imap_port, timeout=self.timeout) as connection:
            connection.login(self.address, self.password)
            connection.select()
            _, [ids] = connection.uid("search", None, *criteria)
            return ids.decode("utf-8").split()[-count:]

    def fetch(self, message_id: str, content_type: str = None):
        with imaplib.IMAP4_SSL(self.imap_server, self.imap_port, timeout=self.timeout) as connection:
            connection.login(self.address, self.password)
            connection.select()
            _, msg_data = connection.uid("fetch", message_id, "(RFC822)")
            if not msg_data[0]:
                return None
            raw = email.message_from_bytes(msg_data[0][1])
            mail_info = {}
            mail_info["subject"] = get_header_content(raw, "Subject")
            mail_info["from"] = get_header_content(raw, "From")
            mail_info["to"] = get_header_content(raw, "To")
            date = get_header_content(raw, "Date")
            if date:
                mail_info["date"] = datetime.strptime(date.split("(")[0].strip(), "%a, %d %b %Y %H:%M:%S %z")
            else:
                mail_info["date"] = datetime.strptime(get_header_content(raw, "Received").split(";")[1].strip(), "%a, %d %b %Y %H:%M:%S %z")
            for part in raw.walk():
                if content_type:
                    if part.get_content_type() != content_type:
                        continue
                else:
                    if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html":
                        continue
                payload = part.get_payload(decode=True)
                charset = chardet.detect(payload)["encoding"]
                if charset == "GB2312":
                    charset = "GBK"
                mail_info["charset"] = charset
                mail_info["content"] = payload.decode(charset)
                break
            return mail_info

    def search(self, count: int, content_type: str, *criteria: str):
        messages = []
        for message_id in self.search_ids(count, *criteria):
            message = self.fetch(message_id, content_type)
            if message:
                messages.append(message)
        return messages
