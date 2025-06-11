import psutil
import time
import platform
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import socket

def send_email_alert(subject, message, recipient, sender_email, sender_password):
    """
    Send an email alert.
    
    Args:
        subject: Critical : System Usage Alert  
        message: CPU and Memory usage
        recipient: elaganesh25@gmail.com
        sender_email: elaganesh25@gmail.com
        sender_password: password
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add hostname and timestamp to message
        hostname = socket.gethostname()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"Host: {hostname}\nTime: {timestamp}\n\n{message}"
        
        msg.attach(MIMEText(full_message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"Email alert sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def alert(message, alert_type="INFO", email_config=None):
    """
    Display an alert message and optionally send an email.
    
    Args:
        message: Alert message to display
        alert_type: Type of alert (INFO, WARNING, CRITICAL)
        email_config: Dictionary with email configuration
    """
    # ANSI color codes for terminal output
    colors = {
        "INFO": "\033[94m",      # Blue
        "WARNING": "\033[93m",   # Yellow
        "CRITICAL": "\033[91m",  # Red
        "RESET": "\033[0m"       # Reset color
    }
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Print colored alert on terminal
    print(f"{colors[alert_type]}[{alert_type}] {timestamp}: {message}{colors['RESET']}")
    
    # Send email for WARNING and CRITICAL alerts if email config is provided
    if email_config and alert_type in ["WARNING", "CRITICAL"]:
        subject = f"System Alert [{alert_type}] - {socket.gethostname()}"
        send_email_alert(
            subject, 
            message, 
            email_config['recipient'],
            email_config['sender_email'],
            email_config['sender_password']
        )
    
    # On Windows, you might want to add a sound alert
    if platform.system() == "Windows" and alert_type == "CRITICAL":
        try:
            import winsound
            winsound.Beep(1000, 500)  # Frequency: 1000Hz, Duration: 500ms
        except Exception:
            pass

def monitor_system(interval=1, duration=10, cpu_threshold=5, memory_threshold=40, email_config=None):
    """
    Monitor system CPU and memory usage with alerts.
    
    Args:
        interval: Time between measurements in seconds
        duration: Total monitoring time in seconds
        cpu_threshold: CPU usage percentage threshold for alerts
        memory_threshold: Memory usage percentage threshold for alerts
        email_config: Dictionary with email configuration
    """
    print(f"{'Time':^8} | {'CPU %':^10} | {'Memory %':^10} | {'Memory Used':^12} | {'Status':^10}")
    print("-" * 70)
    
    alert_count = 0
    
    for i in range(duration):
        # Get CPU and memory usage
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Determine status
        status = "OK"
        if cpu_percent >= cpu_threshold:
            status = "CPU HIGH"
            alert(f"High CPU usage: {cpu_percent:.1f}%", "WARNING", email_config)
            alert_count += 1
        
        if memory.percent >= memory_threshold:
            status = "MEM HIGH"
            alert(f"High memory usage: {memory.percent:.1f}%", "WARNING", email_config)
            alert_count += 1
            
        if cpu_percent >= cpu_threshold and memory.percent >= memory_threshold:
            status = "CRITICAL"
            alert(f"CRITICAL: Both CPU ({cpu_percent:.1f}%) and Memory ({memory.percent:.1f}%) are high!", "CRITICAL", email_config)
            alert_count += 1
        
        # Print formatted output
        print(f"{i*interval:^8} | {cpu_percent:^10.1f} | {memory.percent:^10.1f} | {memory.used/1024/1024/1024:^12.2f} GB | {status:^10}")
        
        time.sleep(interval)
    
    # Summary
    if alert_count > 0:
        alert(f"Monitoring complete. {alert_count} alerts triggered during this session.", "INFO", email_config)
    else:
        alert("Monitoring complete. No alerts triggered during this session.", "INFO", email_config)

def log_to_file(log_file="system_monitor.log"):
    """
    Set up logging to a file.
    
    Args:
        log_file: Path to the log file
    """
    import sys
    
    # Create a class to duplicate stdout to a file
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "a")
            
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message.replace("\033[94m", "").replace("\033[93m", "").replace("\033[91m", "").replace("\033[0m", ""))
            
        def flush(self):
            self.terminal.flush()
            self.log.flush()
    
    sys.stdout = Logger(log_file)

if __name__ == "__main__":
    # Email configuration
    # For Gmail, you need to use an App Password if 2FA is enabled
    # See: https://support.google.com/accounts/answer/185833
    email_config = {
        'sender_email': 'elaganesh25@gmail.com',
       # 'sender_password': 'fugqrodzecwgltvl',
        'sender_password': 'TestAdmin@123',
        'recipient': 'ganesh06_25@yahoo.com' 
    }
    
    # Comment out the email_config line below to disable email alerts
    # email_config = None
    
    # Uncomment to enable logging to file
    # log_to_file()
    
    print("Starting system monitoring with alerts...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        # You can adjust these thresholds based on your system
        monitor_system(
            interval=1, 
            duration=2, 
            cpu_threshold=50, 
            memory_threshold=80,
            email_config=email_config
        )
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

