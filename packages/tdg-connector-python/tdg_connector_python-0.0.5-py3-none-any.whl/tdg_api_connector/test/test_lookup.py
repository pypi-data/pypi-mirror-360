import os
import sys
import unittest
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from api.lookup import LookupAPI
from utilities.helpers import get_all_keys

class TestLookupAPI(unittest.TestCase):

    api_key = os.environ['tdg_api_key']
    base_url = 'https://api.tdg1.io/v2/lookup/'
    lookup_api = LookupAPI(api_key)

    def test_validate_details_by_contact_number_results(self):
        contact_number = 5555555555
        expected_keys = [
            'House', 'PreDir', 'Street', 'StrType', 'PostDir', 'AptType', 'AptNbr', 'City', 
            'ValDate', 'Phone', 'Phone', 'PhoneType', 'DID', 'RecType', 'IDate', 'ODate', 
            'State', 'Zip', 'Z4', 'DPC', 'CRTE', 'CNTY', 'Z4Type', 'DPV', 'Deliverable', 
            'Person', 'Name', 'LName', 'FName', 'MName', 'BusName', 'Address',
            'TelcoName', 'PHV', 'DACode', 'Source'
        ]

        result = self.lookup_api.get_phone(contact_number)
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

    def test_validate_details_by_email_response_results(self):
        email = "abc@gmail.com"
        expected_keys = [
            'Street', 'StrType', 'PostDir', 'AptType', 'AptNbr', 'City', 'State', 'Zip', 
            'Name', 'LName', 'FName', 'MName', 'BusName', 'Address', 'House', 'PreDir', 
            'Z4', 'DPC', 'CRTE', 'CNTY', 'Z4Type', 'DPV', 'Deliverable', 'ValDate', 
            'Email', 'Suppression'
        ]

        result = self.lookup_api.get_email(email)
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

if __name__ == '__main__':
    unittest.main()
