import os
import sys
import unittest
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from api.append import AppendAPI
from utilities.helpers import get_all_keys

class TestAppendAPI(unittest.TestCase):

    api_key = os.environ['tdg_api_key']
    base_url = 'https://api.tdg1.io/v2/append/'
    append_api = AppendAPI(api_key)

    def test_validate_get_phone_results(self):
        expected_keys = [
            'phone', 'phoneType', 'DID', 'recType', 'iDate', 
            'oDate', 'telcoName', 'PHV', 'daCode'
        ]

        result = self.append_api.get_phone(
            first_name="Tom",
            last_name="Smith",
            address="123 Main St",
            zip_number="96162"
        )
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

    def test_validate_get_email_results(self):
        expected_keys = ['email', 'suppression', 'score', 'category']

        result = self.append_api.get_email(
            first_name='',
            last_name='',
            address='656 long lake driv2e',
            zip_number='32765'
        )
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

    def test_validate_get_demographic_results(self):
        expected_keys = [
            'PctBlk', 'PctWht', 'PctHsp', 'PctAsi', 'PctEngSpeak', 'PctSpnSpeak', 'PctAsiaSpeak', 
            'Ethnicity', 'ChildCd', 'ChildAgeCd', 'ChildNbrCd', 'VehLux', 'VehSuv', 'VehTrk', 
            'HHNBRSR', 'CreditCard', 'WealthScr', 'CharityDnr', 'MrktHomeVal', 'Education', 
            'DwellType', 'Married', 'MedYrBld', 'MobHome', 'Pool', 'FirePl', 'SglParent', 
            'PctSFDU', 'PctMFDU', 'MHV', 'MOR', 'PctAuto', 'MedSchl', 'PctWhiteCollar', 
            'Demographics', 'Gender', 'Age', 'DOB', 'LOR', 'Homeowner', 'EHI', 
            'PctBlueCollar', 'PctOccO', 'DemoLvl'
        ]

        result = self.append_api.get_demographic(
            first_name='',
            last_name='',
            address='',
            zip_number='',
            phone='5555555555'
        )
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

    def test_validate_get_auto_results(self):
        expected_keys = [
            'Make', 'Model', 'Year', 'ClassCD', 'FuelTypeCD', 'MFGCD', 'StyleCD', 'Mileages',
            'ClassCD', 'FuelTypeCD', 'MFGCD', 'StyleCD', 'Mileages', 'ODate', 'Vehicle4', 
            'Name', 'FName', 'LName', 'MName', 'Suffix', 'Address', 'House', 'ODate',
            'Year', 'ClassCD', 'FuelTypeCD', 'MFGCD', 'StyleCD', 'Mileages', 'ODate', 
            'State', 'Zip', 'Z4', 'DPC', 'CRTE', 'CNTY', 'Z4Type', 'DPV', 'Vacant', 
            'MSA', 'CBSA', 'IDS', 'PID', 'AID', 'HHID', 'Vehicle', 'Make', 'Model', 
            'PreDir', 'Street', 'StrType', 'PostDir', 'AptType', 'AptNbr', 'City', 
            'Vehicle2', 'Make', 'Model', 'Year', 'ClassCD', 'FuelTypeCD', 'MFGCD', 
            'StyleCD', 'Mileages', 'ODate', 'Vehicle3', 'Make', 'Model', 'Year'
        ]

        result = self.append_api.get_auto(
            full_name='',
            address='',
            zip_number='',
            phone='5555555555'
        )
        keys_extracted = get_all_keys(result)
        expected_keys.sort()
        self.assertEqual(keys_extracted, expected_keys)

if __name__ == '__main__':
    unittest.main()
