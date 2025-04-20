import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from config import EMAIL_USERNAME, EMAIL_PASSWORD


def send_email(report_subject: str):
    server = smtplib.SMTP(host="smtp.gmail.com", port=587)
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

    receiver = "automacaosiberia@gmail.com"
    subject = report_subject

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver
    msg["Subject"] = subject

    text = """Olá!\n\nSegue em anexo os relatórios gerados.\n"""
    msg.attach(MIMEText(text, "plain"))

    folder = "email-reports"

    if os.path.exists(folder):
        files = os.listdir(folder)
        if not files:
            print("Nenhum relatório encontrado na pasta.")
        else:
            for file_name in files:
                file_path = os.path.join(folder, file_name)

                with open(file_path, "rb") as file:
                    attachment = MIMEApplication(file.read(), _subtype="txt")
                    attachment.add_header(
                        "Content-Disposition", "attachment", filename=file_name
                    )
                    msg.attach(attachment)

    else:
        print(f"A pasta '{folder}' não existe.")

    server.send_message(msg)
    server.quit()

    print("E-mail enviado com sucesso!")
