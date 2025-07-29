
# Grabio 🔍

Grabio is a fast and simple Python library to extract detailed information from websites.

It can retrieve IP addresses, SSL details, WHOIS info, server type, page metadata, emails, forms, and more — all with multi-threading for speed and efficiency.

---

## 🚀 Features
- ✅ Extract IP address
- ✅ WHOIS information
- ✅ SSL certificate details
- ✅ Server type detection
- ✅ Host location (Country, Region, City, Organization)
- ✅ Website response time
- ✅ Security headers extraction
- ✅ CDN detection
- ✅ Redirect detection
- ✅ Extract all image URLs
- ✅ Extract emails from the page
- ✅ Count forms on the page
- ✅ Meta description & keywords
- ✅ Page size in KB
- ✅ Robots.txt detection
- ✅ Multi-threading for fast data retrieval
- ✅ CLI Support
- ✅ User-Agent randomization

---

## 📦 Installation
```bash
pip install grabio

Or clone the repository:

git clone https://github.com/xr-xr4/grabio.git
cd grabio
pip install -r requirements.txt


---

🛠️ Usage (Python)

from grabio import Grabio

# Initialize
g = Grabio('https://example.com')

# Extract specific info
print("IP Address:", g.ip())
print("WHOIS Info:", g.whois_info())
print("SSL Info:", g.ssl_info())

# Extract full info
full_info = g.info()
print(full_info)

# Save info as JSON
g.show_info()


---

🖥️ CLI Usage

python cli.py --url example.com --info       # Full information
python cli.py --url example.com --ip         # Only IP address
python cli.py --url example.com --whois      # Only WHOIS info


---

🗂️ Project Structure

grabio/
├── grabio/
│   ├── __init__.py
│   ├── extractor.py
│   ├── utils.py
│   └── user_agent.py
│
├── cli.py
├── setup.py
├── requirements.txt
├── README.md
└── .gitignore


---

✅ Requirements

Python 3.6+

requests

beautifulsoup4

user_agent

python-whois


Install all requirements:

pip install -r requirements.txt


---

📄 License

This project is licensed under the MIT License.


---

🙋 Author

Ahmed Saoud

GitHub: @xr-xr4

Telegram: @xr_xr4

Telegram Channel: @xr_xr4_dev



---

💬 Contributions

Contributions are welcome!
Feel free to fork the repo and submit pull requests 🚀.

---