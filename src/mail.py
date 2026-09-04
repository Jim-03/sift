import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from src.dto import Job, Metadata
from src.ui import template

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("APP_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")


def send_email(jobs: list[Job], metadata: list[Metadata]):
  """Sends an email containing the job postings and their notes

  Args:
    metadata (list[Metadata]): A list of notes for each job
    jobs (list[Job]): A list of extracted jobs
  """
  if not sender_email or not app_password or not receiver_email:
    raise Exception("Provide the email  credentials")

  msg = MIMEMultipart()
  msg["From"] = sender_email
  msg["To"] = receiver_email
  msg["Subject"] = "Sift Findings"
  msg.attach(MIMEText(template(jobs, metadata), "html"))
  try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
      server.login(sender_email, app_password)
      server.sendmail(sender_email, receiver_email, msg.as_string())
      print("Email sent successfully")
  except Exception as e:
    print(f"An error has occurred when sending the email: {e}")
    raise
