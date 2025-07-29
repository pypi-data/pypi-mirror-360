import socket
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .user_agent import get_random_user_agent
from .utils import *

class Grabio:
    def __init__(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.url = url
        self.parsed = urlparse(url)
        self.domain = self.parsed.hostname
        self.headers = {'User-Agent': get_random_user_agent()}
        self.results = {}

    def ip(self):
        try:
            return socket.gethostbyname(self.domain)
        except:
            return 'Unavailable'

    def whois_info(self):
        return get_whois_info(self.domain)

    def ssl_info(self):
        try:
            response = requests.get('https://' + self.domain, headers=self.headers, timeout=5, verify=True)
            cert = response.raw.connection.sock.getpeercert()
            expiry = cert.get('notAfter')
            return {'ssl_enabled': True, 'ssl_valid': True, 'ssl_expiry_date': expiry, 'issuer': cert.get('issuer')}
        except:
            return {'ssl_enabled': False, 'ssl_valid': False, 'ssl_expiry_date': 'Unavailable', 'issuer': 'Unknown'}

    def server_type(self):
        try:
            response = requests.head(self.url, headers=self.headers, timeout=5)
            return response.headers.get('Server', 'Unknown')
        except:
            return 'Unknown'

    def host_location(self):
        try:
            ip = self.ip()
            res = requests.get(f'http://ip-api.com/json/{ip}').json()
            return {'country': res.get('country'), 'region': res.get('regionName'), 'city': res.get('city'), 'org': res.get('org')}
        except:
            return 'Unavailable'

    def response_time(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5)
            return response.elapsed.total_seconds()
        except:
            return 'Unavailable'

    def security_headers(self):
        try:
            response = requests.head(self.url, headers=self.headers, timeout=5)
            return get_security_headers(response.headers)
        except:
            return {}

    def all_images(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            return [img.get('src') for img in soup.find_all('img') if img.get('src')]
        except:
            return []

    def meta_info(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            description = soup.find('meta', attrs={'name': 'description'})
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            return {'description': description['content'] if description else 'Not Found',
                    'keywords': keywords['content'] if keywords else 'Not Found'}
        except:
            return {'description': 'Not Found', 'keywords': 'Not Found'}

    def page_size(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5)
            return len(response.content) / 1024
        except:
            return 'Unavailable'

    def check_robots_txt(self):
        try:
            response = requests.get(f'{self.parsed.scheme}://{self.domain}/robots.txt', headers=self.headers, timeout=5)
            if response.status_code == 200:
                return {'robots_txt': True, 'content': response.text[:500]}
            else:
                return {'robots_txt': False, 'content': 'Not Found'}
        except:
            return {'robots_txt': False, 'content': 'Error'}

    def cdn_provider(self):
        server = self.server_type()
        return detect_cdn(server)

    def emails_found(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5)
            return extract_emails(response.text)
        except:
            return []

    def forms_found(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5)
            return extract_forms(response.text)
        except:
            return 0

    def redirect(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=5, allow_redirects=True)
            return {'redirected': len(response.history) > 0, 'final_url': response.url}
        except:
            return {'redirected': False, 'final_url': self.url}

    def is_online(self):
        return is_site_online(self.url, self.headers)

    def info(self):
        threads = []
        functions = {
            'ip_address': self.ip,
            'whois_info': self.whois_info,
            'ssl_info': self.ssl_info,
            'server_type': self.server_type,
            'host_location': self.host_location,
            'response_time_sec': self.response_time,
            'security_headers': self.security_headers,
            'all_images': self.all_images,
            'meta_info': self.meta_info,
            'page_size_kb': self.page_size,
            'robots_txt': self.check_robots_txt,
            'cdn_provider': self.cdn_provider,
            'emails_found': self.emails_found,
            'forms_found': self.forms_found,
            'redirect_info': self.redirect,
            'is_online': self.is_online
        }

        def run_and_store(key, func):
            self.results[key] = func()

        for key, func in functions.items():
            t = threading.Thread(target=run_and_store, args=(key, func))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return self.results

    def show_info(self):
        import json
        info = self.info()
        print(json.dumps(info, indent=4))
        with open(f'result_{self.domain}.json', 'w') as f:
            json.dump(info, f, indent=4)