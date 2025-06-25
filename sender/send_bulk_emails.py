import sqlite3
import pandas as pd
import smtplib
from email.message import EmailMessage
import ssl
import os
import time
from dotenv import load_dotenv

load_dotenv()
DB = 'email_automation.db'
def get_db():
    conn = sqlite3.connect(DB)
    return conn

def create_email(email, name, company):
    with open(os.getenv('EMAIL_TEMPLATE_FILE')) as f:
        body = f.read().format(name=name, company=company)
    msg = EmailMessage()
    msg['Subject'] = f"Application for DevOps Engineer at {company}"
    msg['From'] = os.getenv('GMAIL_USER')
    msg['To'] = email
    msg.set_content(body)
    with open(os.getenv('RESUME_FILE'),'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='resume.pdf')
    return msg

def log_status(email, status):
    conn = get_db()
    conn.execute("INSERT INTO logs(email,status) VALUES(?,?)", (email, status))
    conn.commit()

def main():
    conn = get_db()
    df = pd.read_excel(os.getenv('EXCEL_FILE'))
    sent = conn.execute("SELECT email FROM logs").fetchall()
    sent_emails = set([e[0] for e in sent])
    for index, row in df.iterrows():
        email, name, company = row['Email'], row['Name'], row['Company']
        if email in sent_emails:
            continue
        msg = create_email(email, name, company)
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as server:
                server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
                server.send_message(msg)
            log_status(email, 'sent')
        except Exception:
            log_status(email, 'failed')
        time.sleep(int(os.getenv('EMAIL_DELAY')))
        if (index+1)%int(os.getenv('BATCH_SIZE'))==0:
            time.sleep(int(os.getenv('BATCH_DELAY')))

if __name__=='__main__':
    main()
