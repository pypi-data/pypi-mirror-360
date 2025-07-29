import os
import sys
import unittest
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from api.verify import VerifyAPI
from utilities.helpers import get_all_keys

class TestVerifyAPI(unittest.TestCase):

    api_key = os.environ['tdg_api_key']
    base_url = 'https://api.tdg1.io/v2/verify/'
    verify_api = VerifyAPI(api_key)

    def test_validation_verification_score_results(self):
        phone = 5555555555
        expected_keys = [
            'RiskFlagCount', 'ValidationSummary', 'LinkageSummary', 'RiskFlagSummary',
            'IDScores', 'ValidAddress', 'ValidPhone', 'ValidEmail', 'ValidName', 'ValidZip', 
            'Phone2ConfidenceScore', 'AddressConfidenceScore', 'ValidCount', 'LinkageCount', 
            'Deceased', 'NameToPhone', 'NameToEmail', 'NameToAddress', 'AddressToPhone', 
            'AddressToEmail', 'PhoneToEmail', 'ZipToPhone', 'USLocation', 'ValidPhone2', 'IDVerifyScore',
            'NameToPhone2', 'AddressToPhone2', 'Phone2ToEmail', 'PhoneConfidenceScore', 
            ]

        result = self.verify_api.get_id(phone=phone)
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

    def test_validation_verify_tcpa_info_results(self):
        phone=5555555555
        last_name='Smith'
        expected_keys = ["verification_code", "phone_type"]

        result = self.verify_api.get_tcpa_info(phone=phone, last_name=last_name)
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

if __name__ == '__main__':
    unittest.main()
