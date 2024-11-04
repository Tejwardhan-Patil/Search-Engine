import datetime
from typing import Dict, List
import json
import os

# Define constants for compliance policies
GDPR_CONSENT_CATEGORIES = ['analytics', 'marketing', 'functional']
CCPA_CONSENT_CATEGORIES = ['sale_of_personal_data', 'data_sharing']

class ConsentError(Exception):
    """Custom exception for consent management errors."""
    pass

class ConsentRecord:
    """Represents a user's consent record."""
    def __init__(self, user_id: str, consent_given: Dict[str, bool], timestamp: datetime.datetime):
        self.user_id = user_id
        self.consent_given = consent_given
        self.timestamp = timestamp

    def to_dict(self) -> Dict:
        """Convert consent record to dictionary."""
        return {
            "user_id": self.user_id,
            "consent_given": self.consent_given,
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'ConsentRecord':
        """Create a consent record from dictionary."""
        return ConsentRecord(
            user_id=data['user_id'],
            consent_given=data['consent_given'],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])
        )

class ConsentManager:
    """Manages user consent for data collection."""
    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.load_consent_records()

    def load_consent_records(self):
        """Load consent records from the storage file."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as file:
                data = json.load(file)
                for record_data in data:
                    record = ConsentRecord.from_dict(record_data)
                    self.consent_records[record.user_id] = record

    def save_consent_records(self):
        """Save all consent records to the storage file."""
        with open(self.storage_file, 'w') as file:
            data = [record.to_dict() for record in self.consent_records.values()]
            json.dump(data, file, indent=4)

    def get_user_consent(self, user_id: str) -> Dict[str, bool]:
        """Retrieve consent status for a user."""
        if user_id in self.consent_records:
            return self.consent_records[user_id].consent_given
        return {}

    def update_user_consent(self, user_id: str, consent_data: Dict[str, bool]):
        """Update the consent data for a user."""
        if not consent_data:
            raise ConsentError("Consent data cannot be empty.")
        
        current_time = datetime.datetime.now()
        consent_record = ConsentRecord(user_id, consent_data, current_time)
        self.consent_records[user_id] = consent_record
        self.save_consent_records()

    def revoke_user_consent(self, user_id: str):
        """Revoke all consent for a user."""
        if user_id in self.consent_records:
            del self.consent_records[user_id]
            self.save_consent_records()

    def verify_consent(self, user_id: str, consent_category: str) -> bool:
        """Verify if the user has provided consent for a specific category."""
        consent_status = self.get_user_consent(user_id)
        return consent_status.get(consent_category, False)

class ConsentComplianceChecker:
    """Checks for compliance with privacy laws (GDPR, CCPA)."""
    def __init__(self, consent_manager: ConsentManager):
        self.consent_manager = consent_manager

    def check_gdpr_compliance(self, user_id: str) -> bool:
        """Check if the user's consent complies with GDPR."""
        consent_status = self.consent_manager.get_user_consent(user_id)
        for category in GDPR_CONSENT_CATEGORIES:
            if category not in consent_status or not consent_status[category]:
                return False
        return True

    def check_ccpa_compliance(self, user_id: str) -> bool:
        """Check if the user's consent complies with CCPA."""
        consent_status = self.consent_manager.get_user_consent(user_id)
        for category in CCPA_CONSENT_CATEGORIES:
            if category not in consent_status or not consent_status[category]:
                return False
        return True

class ConsentService:
    """Service for managing and verifying user consent."""
    def __init__(self, consent_manager: ConsentManager, compliance_checker: ConsentComplianceChecker):
        self.consent_manager = consent_manager
        self.compliance_checker = compliance_checker

    def handle_consent_request(self, user_id: str, consent_data: Dict[str, bool]):
        """Handle consent request and update consent data."""
        self.consent_manager.update_user_consent(user_id, consent_data)
        print(f"Consent updated for user {user_id}")

    def revoke_consent(self, user_id: str):
        """Revoke user's consent."""
        self.consent_manager.revoke_user_consent(user_id)
        print(f"Consent revoked for user {user_id}")

    def check_gdpr(self, user_id: str) -> bool:
        """Check if user is GDPR compliant."""
        return self.compliance_checker.check_gdpr_compliance(user_id)

    def check_ccpa(self, user_id: str) -> bool:
        """Check if user is CCPA compliant."""
        return self.compliance_checker.check_ccpa_compliance(user_id)

# Usage of the consent management system
def main():
    storage_file = "user_consent_records.json"
    consent_manager = ConsentManager(storage_file)
    compliance_checker = ConsentComplianceChecker(consent_manager)
    consent_service = ConsentService(consent_manager, compliance_checker)

    # Simulating user consent update
    user_consent_data = {
        "analytics": True,
        "marketing": False,
        "functional": True
    }
    user_id = "user123"
    consent_service.handle_consent_request(user_id, user_consent_data)

    # Check GDPR compliance
    is_gdpr_compliant = consent_service.check_gdpr(user_id)
    print(f"User GDPR compliance: {is_gdpr_compliant}")

    # Check CCPA compliance
    is_ccpa_compliant = consent_service.check_ccpa(user_id)
    print(f"User CCPA compliance: {is_ccpa_compliant}")

    # Revoke consent
    consent_service.revoke_consent(user_id)

if __name__ == "__main__":
    main()