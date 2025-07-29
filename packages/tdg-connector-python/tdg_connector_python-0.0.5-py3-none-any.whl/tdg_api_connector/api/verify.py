import os
import sys
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utilities.helpers import get_data

class VerifyAPI:
    """
    VerifyApi is a library that interacts with the Verify API to verify the validity of 
    consumer contact information and offering tcpa identity verification. 
    To utilize this class, an API key is required for authentication.

    Attributes:
        - BASE_URL (str): The base URL for the Phone Lookup API.
        - headers (dict): Contains the API key in dictionary format.

    Methods:
        - get_id(first_name: str=None, last_name: str=None, 
                    address: int=None, zip_number: int=None, 
                    phone: str=None, email: str=None) -> dict

        - get_tcpa_info(self, phone: int=None, last_name: str=None) -> dict
    
    Example Usage:
        obj = VerifyAPI('api_key')
        obj.get_verification_score(first_name='TOM', last_name='SMITH')
    """

    def __init__(self, api_key: str) -> None:
        self.base_url = 'https://api.tdg1.io/v2/verify/'
        self.headers = {
            "x-api-key": api_key
        }

    def get_id(self, first_name: str=None, last_name: str=None,
                    address: int=None, zip_number: int=None,
                    phone: str=None, email: str=None) -> dict:
        """
        This function is used to assess the validity of consumer contact information, 
        identify potential risks or fraud, and make informed decisions based on the 
        verification scores and summaries provided by the service.

        Parameters(ATLEAST 2 PARAMETERS WITH ANY COMBINATION REQUIRED TO CHECK THE ACCURACY SCORE):
            - first_name: str
                The first name of the individual. Maximum 15 characters.
            - last_name: str
                The last name of the individual. Maximum 20 characters.
            - address: str
                The address of the individual. Maximum 64 characters.
            - zip_number: int
                The 5-digit numeric USPS zip code. Either City/State or Zip is required.
            - phone: str
                The 10-digit numeric phone number without spaces, dashes, or parentheses.
            - email: str
                The email address of the individual. Maximum 100 characters.

        Returns:
            dict
                A dictionary containing the details of the retrieved response.
        """

        return get_data(
            base_url=self.base_url,
            request_type='POST',
            endpoint='id',
            payload={
                "FName": first_name,
                "LName": last_name,
                "Address1": address,
                "Zip": zip_number,
                "Phone": phone,
                "Email": email
            },
            headers=self.headers
        )

    def get_tcpa_info(self, phone: int=None, last_name: str=None) -> dict:
        """
        function to make a request to the TCPA Verify endpoint to mitigate 
        TCPA risk by identifying wireless numbers and offering identity verification 
        for called party consent.

        Parameters:
            - phone (Required)  
                10 digit numeric phone number (without spaces, dashes, or parentheses)  
            
            - last_name (Required)
                The last name of the individual. Maximum 20 characters.

        Returns:
            dict
                A dictionary containing the details of the retrieved response.
        """

        return get_data(
            base_url=self.base_url,
            request_type='POST',
            endpoint='tcpa',
            payload={
                "phone": phone,
                "last_name": last_name
            },
            headers=self.headers
        )

def get_email(self, email: str) -> dict:
    """
    A function that gets the details by email.

    Parameters:
        - email: str, (REQUIRED)
            100 characters max.

    Returns:
        A dictionary containing the details of the email.

    Raises:
        ValueError: If email is not valid.
    """

    if '@' not in email:
        raise ValueError("Invalid email address.")

    return get_data(
        base_url=self.base_url,
        request_type='POST',
        endpoint='email',
        payload={
            "Email": email
        },
        headers=self.headers
    )
