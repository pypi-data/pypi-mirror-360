# samhiqmailer/SamhiqMailer.py
import smtplib, threading, time, os, json, sys, openpyxl, requests
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext, ttk
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from samhiqmailer import __version__

CONFIG_FILE = 'user_config.json'
CURRENT_VERSION = __version__
os.makedirs('drafts', exist_ok=True)

NOTIFICATION_URL = 'https://raw.githubusercontent.com/samhiq/SamhiqMailer/main/notifications.json'
FEEDBACK_EMAIL = 'contact.samhiq@gmail.com'


html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Email from {sender_name}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #f5f7fa;
      font-family: 'Segoe UI', Roboto, sans-serif;
      color: #333333;
    }}
    .container {{
      max-width: 620px;
      margin: 40px auto;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
      overflow: hidden;
    }}
    .header {{
      background: linear-gradient(135deg, #004e92, #000428);
      color: #ffffff;
      padding: 35px 20px;
      text-align: center;
      font-size: 26px;
      font-weight: bold;
      letter-spacing: 1px;
      border-top-left-radius: 12px;
      border-top-right-radius: 12px;
    }}
    .body {{
      padding: 40px 30px 20px 30px;
    }}
    .body h2 {{
      color: #004e92;
      font-size: 22px;
      margin-bottom: 20px;
    }}
    .body p {{
      font-size: 16px;
      line-height: 1.7;
      margin-bottom: 20px;
    }}
    .signature {{
      font-size: 16px;
      margin-top: 40px;
      font-weight: 500;
    }}
    .signature strong {{
      color: #000428;
    }}
    .footer {{
      background: #f1f3f6;
      padding: 18px;
      text-align: center;
      font-size: 13px;
      color: #777777;
      border-bottom-left-radius: 12px;
      border-bottom-right-radius: 12px;
    }}
    .footer span {{
      color: #004e92;
      font-weight: bold;
    }}
    @media (max-width: 640px) {{
      .body, .header, .footer {{
        padding-left: 15px !important;
        padding-right: 15px !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      {sender_name}
    </div>
    <div class="body">
      <h2>Dear {name},</h2>
      <p>{content}</p><br>

      <div class="signature">
        Warm Regards,<br>
        <strong>{sender_name}</strong>
      </div>
    </div>
    <div class="footer">
      Sent using <span>Samhiq Mailer</span> – Designed & Developed by<br> Md Sameer Iqbal (Samhiq)
    </div>
  </div>
</body>
</html>
"""

# --- Feedback HTML Template ---
feedback_html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Feedback Mail</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 0;
    }}
    .container {{
      max-width: 600px;
      margin: 30px auto;
      background: #ffffff;
      border-radius: 10px;
      padding: 30px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #0052cc;
      font-size: 22px;
      margin-bottom: 20px;
    }}
    p {{
      font-size: 16px;
      margin-bottom: 10px;
      color: #333;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #777;
      text-align: center;
    }}
    .footer span {{
      color: #0052cc;
      font-weight: bold;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>📬 New Feedback Received</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Mobile No:</strong> {mobile}</p>
    <p><strong>Message:</strong></p>
    <p>{message}</p>

    <div class="footer">
      Sent via <span>Samhiq Mailer</span> – Feedback System
    </div>
  </div>
</body>
</html>
"""

def load_config():
    return json.load(open(CONFIG_FILE, 'r', encoding='utf-8')) if os.path.exists(CONFIG_FILE) else {}

def save_config(config):
    json.dump(config, open(CONFIG_FILE, 'w', encoding='utf-8'), indent=4)

config = load_config()
EMAIL_ADDRESS = config.get("email", "")
EMAIL_PASSWORD = config.get("password", "")
SENDER_NAME = config.get("sender_name", "Samhiq Mailer")
SMTP_SERVER = config.get("smtp", "smtp.gmail.com")
SMTP_PORT = int(config.get("port", 587))

class SamhiqMailerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Samhiq Mailer - Pro Desktop")
        self.root.geometry("900x850")
        self.root.configure(bg="#e6ecf0")
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        self.attachments, self.recipients = [], []

        self.tabs = ttk.Notebook(root)
        self.mail_tab = Frame(self.tabs, bg="#e6ecf0")
        self.notification_tab = Frame(self.tabs, bg="#e6ecf0")
        self.feedback_tab = Frame(self.tabs, bg="#e6ecf0")
        self.tabs.add(self.mail_tab, text="📧 Mailer")
        self.tabs.add(self.notification_tab, text="🔔 Notifications")
        self.tabs.add(self.feedback_tab, text="💬 Feedback")
        self.tabs.pack(expand=1, fill="both")

        self.build_tabs()

    def build_tabs(self):
        self.build_mailer_tab()
        self.build_notification_tab()
        self.build_feedback_tab()

    def build_mailer_tab(self):
        top = Frame(self.mail_tab, bg="#e6ecf0")
        top.pack(pady=10)

        Button(top, text="⚙️ Change Settings", command=self.configure_user_credentials, bg="#FFA500", fg="black").grid(row=0, column=0, padx=5)
        Button(top, text="📁 Import Excel", command=self.import_excel, bg="#E0E0E0").grid(row=0, column=1, padx=5)
        Button(top, text="📌 Add Attachment", command=self.add_attachment, bg="#E0E0E0").grid(row=0, column=2, padx=5)
        Button(top, text="🩹 Clear All", command=self.clear_all, bg="#E0E0E0").grid(row=0, column=3, padx=5)
        Button(top, text="🚀 Send Emails", command=self.start_sending, bg="#4CAF50", fg="white").grid(row=0, column=4, padx=5)

        Label(self.mail_tab, text="Recipient Email (optional):", bg="#e6ecf0", font=('Segoe UI', 10)).pack()
        self.email_entry = Entry(self.mail_tab, width=80)
        self.email_entry.pack()

        Label(self.mail_tab, text="Recipient Name (optional):", bg="#e6ecf0", font=('Segoe UI', 10)).pack()
        self.name_entry = Entry(self.mail_tab, width=80)
        self.name_entry.pack()

        Label(self.mail_tab, text="Subject:", bg="#e6ecf0", font=('Segoe UI', 10)).pack()
        self.subject_entry = Entry(self.mail_tab, width=80)
        self.subject_entry.pack()

        Label(self.mail_tab, text="Message Body (use {name}):", bg="#e6ecf0", font=('Segoe UI', 10)).pack()
        self.body_text = scrolledtext.ScrolledText(self.mail_tab, width=90, height=15, bg="#f5f7fa", fg="#111", font=("Segoe UI Emoji", 10), insertbackground="#000000", wrap=WORD, borderwidth=2, relief=GROOVE)
        self.body_text.pack()

        self.progress = ttk.Progressbar(self.mail_tab, length=400)
        self.progress.pack(pady=5)
        self.status_label = Label(self.mail_tab, text="", bg="#e6ecf0", font=('Segoe UI', 9))
        self.status_label.pack()

        self.log_area = scrolledtext.ScrolledText(self.mail_tab, width=90, height=8, state='disabled', bg="#f9f9f9", fg="#111", font=("Consolas", 9))
        self.log_area.pack(pady=10)

    def build_notification_tab(self):
        self.notification_area = scrolledtext.ScrolledText(self.notification_tab, width=90, height=35, bg="#ffffff", fg="#111", font=("Segoe UI", 10))
        self.notification_area.pack(pady=20)
        Button(self.notification_tab, text="🔄 Refresh", command=self.fetch_notifications, bg="#FFA500").pack(pady=5)
        self.fetch_notifications()

    def build_feedback_tab(self):
        Label(self.feedback_tab, text="Your Name:", bg="#e6ecf0", font=('Segoe UI', 10)).pack(pady=(20, 0))
        self.fb_name = Entry(self.feedback_tab, width=60)
        self.fb_name.pack()

        Label(self.feedback_tab, text="Mobile Number:", bg="#e6ecf0", font=('Segoe UI', 10)).pack()
        self.fb_mobile = Entry(self.feedback_tab, width=60)
        self.fb_mobile.pack()

        Label(self.feedback_tab, text="Your Feedback:", bg="#e6ecf0", font=('Segoe UI', 10)).pack()
        self.fb_message = scrolledtext.ScrolledText(self.feedback_tab, width=70, height=10, bg="#ffffff", fg="#111", font=("Segoe UI", 10))
        self.fb_message.pack(pady=5)

        Button(self.feedback_tab, text="📨 Submit Feedback", command=self.send_feedback, bg="#2196F3", fg="white").pack(pady=10)

    def fetch_notifications(self):
        try:
            res = requests.get(NOTIFICATION_URL)
            data = res.json()
            self.notification_area.delete("1.0", END)
            if isinstance(data, dict):
                data = data.get("notifications", [])
            if not isinstance(data, list):
                raise ValueError("Invalid notification format")
            for item in data:
                if isinstance(item, dict):
                    date = item.get('date', '')
                    title = item.get('title', 'No Title')
                    message = item.get('message', 'No Content')
                    self.notification_area.insert(
                        END, f"📅 {date}\n📌 {title}\n{message}\n{'-'*80}\n"
                    )
                else:
                    self.notification_area.insert(END, f"📌 {str(item)}\n{'-'*80}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch notifications: {e}")

    def configure_user_credentials(self):
        top = Toplevel(self.root)
        top.title("Configure Email Credentials")
        top.lift()
        top.attributes("-topmost", True)

        Label(top, text="Email Address:").grid(row=0, column=0)
        email_entry = Entry(top, width=40)
        email_entry.insert(0, EMAIL_ADDRESS)
        email_entry.grid(row=0, column=1)

        Label(top, text="App Password:").grid(row=1, column=0)
        pass_entry = Entry(top, show='*', width=40)
        pass_entry.insert(0, EMAIL_PASSWORD)
        pass_entry.grid(row=1, column=1)

        Label(top, text="Sender / Organization Name:").grid(row=2, column=0)
        name_entry = Entry(top, width=40)
        name_entry.insert(0, SENDER_NAME)
        name_entry.grid(row=2, column=1)

        def save_and_reload():
            config['email'] = email_entry.get().strip()
            config['password'] = pass_entry.get().strip()
            config['sender_name'] = name_entry.get().strip()
            save_config(config)
            messagebox.showinfo("Saved", "Credentials updated. Please restart the app to apply changes.")
            top.destroy()

        Button(top, text="Save", command=save_and_reload, bg="green", fg="white").grid(row=3, columnspan=2, pady=10)

    def import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        wb = openpyxl.load_workbook(path)
        sheet = wb.active
        self.recipients = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            email, name = row[:2]
            if email:
                self.recipients.append((email, name or ""))
        messagebox.showinfo("Imported", f"Imported {len(self.recipients)} recipients.")

    def add_attachment(self):
        files = filedialog.askopenfilenames()
        self.attachments.extend(files)
        messagebox.showinfo("Attached", f"Added {len(files)} file(s).")

    def clear_all(self):
        self.subject_entry.delete(0, END)
        self.body_text.delete('1.0', END)
        self.attachments.clear()
        self.recipients.clear()
        self.email_entry.delete(0, END)
        self.name_entry.delete(0, END)
        self.progress['value'] = 0
        self.status_label.config(text="")
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', END)
        self.log_area.config(state='disabled')

    def start_sending(self):
        threading.Thread(target=self.send_emails).start()

    def send_emails(self):
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", END).strip()
        manual_email = self.email_entry.get().strip()
        manual_name = self.name_entry.get().strip() or "User"
        if manual_email:
            self.recipients.append((manual_email, manual_name))
        total = len(self.recipients)
        if not subject or not body or total == 0:
            messagebox.showwarning("Missing Info", "Enter subject, body, and at least one recipient.")
            return

        self.log("Connecting to SMTP server...")
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            self.log("✅ Logged in successfully.")
        except Exception as e:
            self.log(f"❌ Failed to connect: {e}")
            return

        now = time.localtime()
        dt = {
            "{date}": time.strftime("%d-%m-%Y", now),
            "{time}": time.strftime("%H:%M:%S", now),
            "{sender_name}": SENDER_NAME,
            "{current_version}": CURRENT_VERSION,
        }

        for i, (email, name) in enumerate(self.recipients):
            msg = MIMEMultipart()
            msg['From'] = formataddr((SENDER_NAME, EMAIL_ADDRESS))
            msg['To'] = email
            msg['Subject'] = subject

            personalized_body = body
            for tag, value in dt.items():
                personalized_body = personalized_body.replace(tag, value)
            personalized_body = personalized_body.replace("{name}", name)

            content_html = html_template.format(name=name, content=personalized_body, sender_name=SENDER_NAME)
            msg.attach(MIMEText(content_html, 'html'))

            for filepath in self.attachments:
                with open(filepath, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                    msg.attach(part)

            for attempt in range(3):
                try:
                    self.log(f"Sending to {email} (Attempt {attempt+1}/3)...")
                    server.send_message(msg)
                    self.log(f"✅ Email sent to {email}")
                    break
                except Exception as e:
                    self.log(f"Retry {attempt+1} failed for {email}: {e}")
                    if attempt == 2:
                        self.log(f"❌ Failed to send to {email} after 3 attempts")

            self.progress['value'] = ((i + 1) / total) * 100
            self.status_label.config(text=f"Sending... ({i + 1}/{total})")
            self.root.update_idletasks()
            time.sleep(0.3)

        server.quit()
        self.status_label.config(text=f"✅ Sent {total} emails successfully.")
        self.log("All emails sent successfully.")
        messagebox.showinfo("Done", f"Sent {total} emails successfully.")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(END, f"{message}\n")
        self.log_area.see(END)
        self.log_area.config(state='disabled')

    def send_feedback(self):
        name = self.fb_name.get().strip()
        mobile = self.fb_mobile.get().strip()
        message = self.fb_message.get("1.0", END).strip()
        if not name or not mobile or not message:
            messagebox.showwarning("Missing", "All feedback fields are required.")
            return
        try:
            feedback_msg = MIMEMultipart()
            feedback_msg['From'] = formataddr((SENDER_NAME, EMAIL_ADDRESS))
            feedback_msg['To'] = FEEDBACK_EMAIL
            feedback_msg['Subject'] = "User Feedback from Samhiq Mailer"
            feedback_html = feedback_html_template.format(name=name, mobile=mobile, message=message)
            feedback_msg.attach(MIMEText(feedback_html, 'html'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(feedback_msg)
            server.quit()

            messagebox.showinfo("Submitted", "Developer has received your request and will reply at the earliest.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send feedback: {e}")

def main():
    root = Tk()
    app = SamhiqMailerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
