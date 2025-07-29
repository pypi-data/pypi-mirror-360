import os
import sys
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utilities.helpers import get_data

class AppendAPI:
    """
    AppendAPI is a library that interacts with the Append API to fetch details related to phones 
    and emails. To utilize this class, an API key is required for authentication.

    Attributes:
        - BASE_URL (str): The base URL for the Phone Lookup API.
        - headers (dict): Contains the API key in dictionary format.

    Methods:
        - get_phone(first_name: str, 
                        last_name: str, address: str, 
                        zip_number: int) -> dict

        - get_email(first_name: str, 
                        last_name: str, address: str, 
                        zip_number: int) -> dict

        - get_demographic(first_name: str=None, 
                            last_name: str=None, address: str=None, 
                            zip_number: int=None, phone: int=None, 
                            email: str=None, city: str=None, 
                            state: str=None) -> dict

        - get_auto(full_name: str=None, address: str=None, 
                        zip_number: int=None, first_name: str=None, 
                        last_name: str=None, email: str=None, phone: str=None) -> dict:
    
    Example Usage:
        obj = AppendAPI('api_key')
        obj.get_phone_number_details_by_names_and_addresses(
            first_name='first_name',
            last_name='last_name',
            address='address',
            zip_number='zip_number'
        )
    """


    def __init__(self, api_key: str) -> None:
        self.base_url = 'https://api.tdg1.io/v2/append/'
        self.new_base_url = 'https://testapi.tdg1.io/v3/append/'
        self.headers = {
            "x-api-key": api_key
        }

    def get_phone(self, first_name: str,
                        last_name: str, address: str,
                        zip_number: int) -> dict:
        """
        A function that allows users to query for phone numbers matching names and addresses
        by providing certain input fields such as first name, last name, address, and zip 
        code. The API then returns appended telephone numbers along with other phone 
        attributes such as record type, telephone confidence score, and directory assistance flag.

        Parameters:
            - first_name: str, (REQUIRED)
                The first name of the individual (up to 15 characters).
            - last_name: str, (REQUIRED)
                The last name of the individual (up to 15 characters).
            - address: str, (REQUIRED)
                The address of the individual (up to 60 characters).
            - zip_number: int, (REQUIRED)
                5-digit numeric USPS zip code. Either City/State or Zip is required.
        Returns:
            dict
                A dictionary containing the details of the retrieved response.
        """

        return get_data(
            base_url=self.new_base_url,
            request_type='POST',
            endpoint='phone',
            payload={
                "FName": first_name,
                "LName": last_name,
                "Address1": address,
                "Zip": zip_number
            },
            headers=self.headers
        )

    def get_email(self, first_name: str,
                                last_name: str, address: str,
                                zip_number: int) -> dict:
        """
        A function that retrieves email details based on names and addresses.
        The Api returns appended email when suppression is False along with other attributes 
        score, category, suppression

        Parameters:
            - first_name: str, (REQUIRED)
                The first name of the individual (up to 15 characters).
            - last_name: str, (REQUIRED)
                The last name of the individual (up to 20 characters).
            - address: str, (REQUIRED)
                The address of the individual (up to 64 characters).
            - zip_number: int, (REQUIRED)
                5-digit numeric USPS zip code.

        Returns:
            dict
                A dictionary containing the details of the retrieved response.
        """

        return get_data(
            base_url=self.new_base_url,
            request_type='POST',
            endpoint='email',
            payload={
                "FName": first_name,
                "LName": last_name,
                "Address1": address,
                "Zip": zip_number
            },
            headers=self.headers
        )

    def get_demographic(self, first_name: str,
                                    last_name: str, address: str, zip_number: int,
                                    phone: int=None, email: str=None, city: str=None,
                                    state: str=None):
        """      
        A function that retrieves details demographic details based on 
        names, addresses, (email or phone number).

        Parameters:
            - first_name: str, (Should be a combination of FName, LName, Zip, and 
                Address parameters; Phone or Email is REQUIRED)
                The first name of the individual (up to 15 characters).
            - last_name: str, (Should be a combination of FName, LName, Zip, and 
                Address parameters; Phone or Email is REQUIRED)
                The last name of the individual (up to 20 characters).            
            - address: str, (Should be a combination of FName, LName, Zip, and 
                Address parameters; Phone or Email is REQUIRED)
                Address 64 characters max.
            - zip_number: int, (Should be a combination of FName, LName, Zip, and 
                Address parameters; Phone or Email is REQUIRED)
                5-digit numeric USPS zip code. * Either City/State or Zip is required.
            - phone: int, (REQUIRED if Email is not included and other parameters are included)
                10 digit numeric phone number (without spaces, dashes, or parentheses)
            - email: str, (REQUIRED if phone is not included and other parameters are included)
                Email address, 100 characters max
            - city: (OPTIONAL)
                City name, 28 characters max. * Either City/State or Zip is required.
            - state: (OPTIONAL)
                2 character state abbreviation. * Either City/State or Zip is required.

        Returns:
            dict
                A dictionary containing the details of the retrieved response.

        Raises:
            ValueError: either one of phone or email is missing.
        """

        if not phone and not email:
            raise ValueError("Either of phone or email is required")

        return get_data(
            base_url=self.base_url,
            request_type='POST',
            endpoint='demographic',
            payload={
                "FName": first_name,
                "LName": last_name,
                "Address1": address,
                "Zip": zip_number,
                "Phone": phone,
                "Email": email,
                "City": city,
                "State": state
            },
            headers=self.headers
        )

    def get_auto(self, full_name: str, address: str,
                    zip_number: int, email: str=None, phone: str=None) -> dict:
        """
        A function that retrieves Auto details based on names and addresses.

        Parameters:
            - full_name: str, (REQUIRED)
                The full name of the individual
            - address: str, (REQUIRED)
                The address of the individual (up to 64 characters).
            - zip_number: int, (REQUIRED)
                5-digit numeric USPS zip code.
            - phone: int, (REQUIRED if Email is not included and other parameters are included)
                10 digit numeric phone number (without spaces, dashes, or parentheses)
            - email: str, (REQUIRED if phone is not included and other parameters are included)
                Email address, 100 characters max
        Returns:
            dict
                A dictionary containing the details of the retrieved response.
        """

        return get_data(
            base_url=self.base_url,
            request_type='POST',
            endpoint='auto',
            payload={
                "Address1": address,
                "Zip": zip_number,
                "FullName": full_name,
                "Phone": phone,
                "Email": email
            },
            headers=self.headers
        )
