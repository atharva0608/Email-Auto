from flask import Flask, render_template, request, redirect
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE = 'email_automation.db'
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM logs WHERE status='failed'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM hr_contacts WHERE email NOT IN (SELECT email FROM logs)").fetchone()[0]
    return render_template('dashboard.html', total=total, failed=failed, pending=pending)

@app.route('/bulk_upload', methods=['GET','POST'])
def bulk_upload():
    message = ''
    if request.method=='POST':
        data = request.form['bulk_data']
        lines = data.strip().split('\n')
        conn = get_db()
        added=0
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts)!=3: continue
            email,name,company = parts
            exists = conn.execute("SELECT 1 FROM hr_contacts WHERE email=?", (email,)).fetchone()
            if exists: continue
            conn.execute("INSERT INTO hr_contacts(email,name,company) VALUES(?,?,?)",(email,name,company))
            added+=1
        conn.commit()
        message=f"Added {added} contacts"
    return render_template('bulk_upload.html', message=message)

@app.route('/config', methods=['GET','POST'])
def config():
    message = ''
    if request.method=='POST':
        # config update logic here
        pass
    return render_template('config_editor.html', message=message)

@app.route('/template', methods=['GET','POST'])
def template_editor():
    message = ''
    if request.method=='POST':
        content = request.form['template']
        with open(os.getenv('EMAIL_TEMPLATE_FILE'),'w') as f:
            f.write(content)
        message = 'Template updated'
    with open(os.getenv('EMAIL_TEMPLATE_FILE')) as f:
        content = f.read()
    return render_template('email_template_editor.html', template=content, message=message)

@app.route('/logs')
def logs():
    conn = get_db()
    logs = conn.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100").fetchall()
    return render_template('logs.html', logs=logs)

if __name__=='__main__':
    app.run(host='0.0.0.0')
