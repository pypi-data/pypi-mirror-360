import re
import requests
from bs4 import BeautifulSoup
import whois

def is_site_online(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_security_headers(headers):
    security_headers = ['X-Frame-Options', 'Content-Security-Policy', 'Strict-Transport-Security']
    return {header: headers.get(header, 'Missing') for header in security_headers}

def detect_cdn(server_type):
    cdn_providers = ['cloudflare', 'akamai', 'fastly']
    for cdn in cdn_providers:
        if cdn in server_type.lower():
            return cdn.capitalize()
    return 'Not Detected'

def extract_emails(content):
    return list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)))

def extract_forms(content):
    soup = BeautifulSoup(content, 'html.parser')
    forms = soup.find_all('form')
    return len(forms)

def get_whois_info(domain):
    try:
        return whois.whois(domain)
    except:
        return 'Whois information is protected or unavailable.'