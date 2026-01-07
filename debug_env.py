from dotenv import load_dotenv
import os
import socket
from urllib.parse import urlparse

load_dotenv()

url = os.getenv("SUPABASE_URL")
if not url:
    print("SUPABASE_URL is not set")
else:
    print(f"SUPABASE_URL is set to: {url}")
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            print("Could not parse hostname from URL")
        else:
            print(f"Hostname: {hostname}")
            try:
                ip = socket.gethostbyname(hostname)
                print(f"Resolved IP: {ip}")
            except socket.gaierror as e:
                print(f"DNS Resolution failed: {e}")
    except Exception as e:
        print(f"Error parsing URL: {e}")
