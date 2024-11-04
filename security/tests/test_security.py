import unittest
import requests
from security.authentication.api_key_auth import validate_api_key
from security.encryption.data_encryption import encrypt_data, decrypt_data
from security.access_control.rbac import check_access
from cryptography.fernet import Fernet

class SecurityTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_key = "api_key_123"
        cls.invalid_api_key = "invalid_api_key_456"
        cls.base_url = "https://website.com/api/"
        cls.encryption_key = Fernet.generate_key()
        cls.fernet = Fernet(cls.encryption_key)

    def test_api_authentication_valid_key(self):
        """Test API authentication with a valid API key."""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(f'{self.base_url}secure-endpoint', headers=headers)
        self.assertEqual(response.status_code, 200, "API authentication failed with valid key")

    def test_api_authentication_invalid_key(self):
        """Test API authentication with an invalid API key."""
        headers = {'Authorization': f'Bearer {self.invalid_api_key}'}
        response = requests.get(f'{self.base_url}secure-endpoint', headers=headers)
        self.assertEqual(response.status_code, 403, "API did not block invalid key access")

    def test_api_authentication_missing_key(self):
        """Test API authentication without an API key."""
        response = requests.get(f'{self.base_url}secure-endpoint')
        self.assertEqual(response.status_code, 401, "API did not block missing key access")

    def test_encrypt_decrypt_data(self):
        """Test data encryption and decryption."""
        original_data = "Sensitive user information"
        encrypted_data = encrypt_data(self.fernet, original_data)
        decrypted_data = decrypt_data(self.fernet, encrypted_data)
        self.assertEqual(decrypted_data, original_data, "Data decryption failed after encryption")

    def test_decrypt_invalid_data(self):
        """Test decryption with invalid data."""
        with self.assertRaises(Exception, msg="Decryption should fail with invalid data"):
            decrypt_data(self.fernet, b"invalid_encrypted_data")

    def test_rbac_admin_access(self):
        """Test RBAC for admin role."""
        user_role = "admin"
        resource = "confidential_reports"
        has_access = check_access(user_role, resource)
        self.assertTrue(has_access, "Admin should have access to confidential reports")

    def test_rbac_user_access(self):
        """Test RBAC for normal user role."""
        user_role = "user"
        resource = "confidential_reports"
        has_access = check_access(user_role, resource)
        self.assertFalse(has_access, "Normal user should not have access to confidential reports")

    def test_rbac_invalid_role(self):
        """Test RBAC with an invalid role."""
        user_role = "guest"
        resource = "confidential_reports"
        has_access = check_access(user_role, resource)
        self.assertFalse(has_access, "Invalid role should not have any access")

    def test_data_in_transit_encryption(self):
        """Test if data is encrypted while in transit."""
        original_message = "This is a test message."
        encrypted_message = encrypt_data(self.fernet, original_message)
        # Simulate sending over the network
        transmitted_message = encrypted_message
        decrypted_message = decrypt_data(self.fernet, transmitted_message)
        self.assertEqual(decrypted_message, original_message, "Data was not encrypted during transit")

    def test_data_at_rest_encryption(self):
        """Test encryption of data at rest."""
        sensitive_data = "Stored sensitive information"
        encrypted_data = encrypt_data(self.fernet, sensitive_data)
        decrypted_data = decrypt_data(self.fernet, encrypted_data)
        self.assertEqual(decrypted_data, sensitive_data, "Data at rest encryption failed")

    def test_vulnerability_scan_sql_injection(self):
        """Simulate a test for SQL injection vulnerability."""
        vulnerable_query = "SELECT * FROM users WHERE name = 'Person' OR '1'='1';"
        response = requests.post(f'{self.base_url}search', data={'query': vulnerable_query})
        self.assertNotIn("Person", response.text, "SQL Injection vulnerability detected")

    def test_vulnerability_scan_xss(self):
        """Simulate a test for Cross-Site Scripting (XSS) vulnerability."""
        xss_payload = "<script>alert('XSS')</script>"
        response = requests.post(f'{self.base_url}comments', data={'comment': xss_payload})
        self.assertNotIn("<script>", response.text, "XSS vulnerability detected")

    def test_brute_force_protection(self):
        """Test for brute force attack protection by simulating multiple failed logins."""
        login_url = f'{self.base_url}login'
        credentials = {'username': 'Person', 'password': 'wrong_password'}
        for _ in range(10):
            response = requests.post(login_url, data=credentials)
        self.assertEqual(response.status_code, 429, "Brute force protection did not trigger")

    def test_rate_limiting(self):
        """Test API rate limiting mechanism."""
        for _ in range(20):
            response = requests.get(f'{self.base_url}rate-limited-endpoint', headers={'Authorization': f'Bearer {self.api_key}'})
        self.assertEqual(response.status_code, 429, "API rate limiting did not work correctly")

    def test_privacy_policy_compliance(self):
        """Test if privacy policy compliance mechanisms are in place."""
        consent_url = f'{self.base_url}user-consent'
        response = requests.get(consent_url, headers={'Authorization': f'Bearer {self.api_key}'})
        self.assertEqual(response.status_code, 200, "Privacy policy compliance failed")

    def test_data_anonymization(self):
        """Test data anonymization to ensure compliance with privacy laws."""
        sensitive_user_data = {'name': 'Person', 'email': 'person@website.com'}
        anonymized_data = requests.post(f'{self.base_url}anonymize', json=sensitive_user_data)
        self.assertNotIn('name', anonymized_data.json(), "Data anonymization failed")
        self.assertNotIn('email', anonymized_data.json(), "Data anonymization failed")

if __name__ == "__main__":
    unittest.main()