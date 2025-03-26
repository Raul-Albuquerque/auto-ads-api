import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

load_dotenv(override=True)
username = os.getenv("EMAIL_USERNAME")
password = os.getenv("EMAIL_PASSWORD")

def send_email():
    # Configuração do servidor SMTP
    server = smtplib.SMTP(host="smtp.gmail.com", port=587)
    server.starttls()
    server.login(username, password)

    receiver = "automacaosiberia@gmail.com"
    subject = "Relatórios Gerados"

    # Criando o e-mail
    msg = MIMEMultipart()
    msg["From"] = username
    msg["To"] = receiver
    msg["Subject"] = subject

    # Corpo do e-mail
    text = """Olá!\n\nSegue em anexo os relatórios gerados.\n"""
    msg.attach(MIMEText(text, "plain"))

    # Pasta onde os relatórios estão armazenados
    folder = "email-reports"

    # Verifica se a pasta existe
    if os.path.exists(folder):
      files = os.listdir(folder)  # Lista os arquivos na pasta
      if not files:
        print("Nenhum relatório encontrado na pasta.")
      else:
        for file_name in files:
          file_path = os.path.join(folder, file_name)

          # Anexa cada arquivo encontrado
          with open(file_path, "rb") as file:
            attachment = MIMEApplication(file.read(), _subtype="txt")
            attachment.add_header("Content-Disposition", "attachment", filename=file_name)
            msg.attach(attachment)

    else:
      print(f"A pasta '{folder}' não existe.")

    # Envia o e-mail
    server.send_message(msg)
    server.quit()
    
    print("E-mail enviado com sucesso!")