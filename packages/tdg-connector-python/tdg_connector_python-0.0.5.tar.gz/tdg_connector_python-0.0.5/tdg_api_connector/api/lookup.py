import os
import sys
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utilities.helpers import get_data

class LookupAPI:
    """
    LookupAPI is a library that interacts with the Phone Lookup API to fetch details related to 
    phone numbers and emails. To utilize this class, an API key is required for authentication.

    Attributes:
        - BASE_URL (str): The base URL for the Phone Lookup API.
        - headers (dict): Contains the API key in dictionary format.

    Methods:
        - get_phone(phone_number: int) -> dict:
            Retrieves details for a single phone  number.

        - get_phone_number_details_in_bulk(phone_numbers_list: list) -> list:
            Retrieves details for multiple phone  numbers in bulk.

        - get_email(email) -> dict:
            Retrieves details for a single email.

        - get_email_details_in_bulk(email_list) -> lis:
            Retrieves details for multiple emails.
    
    Example Usage:
        obj = LookupAPI('api_key')
        obj.get_details_by_phone_number(phone_number=5555555555)
    """

    def __init__(self, api_key: str) -> None:
        self.base_url = 'https://testapi.tdg1.io/v3/lookup/'
        self.headers = {
            "x-api-key": api_key
        }

    def get_phone(self, phone_number: int) -> dict:

        """
        A function that gets the details for a single phone number.
        
        Parameters:
            - phone_number: int, (REQUIRED)
                10-digit numeric phone number (without spaces, dashes, or parentheses).

        Returns:
            A dictionary containing the details of the phone  number.

        Raises:
            ValueError: If phone_number is not a 10-digit number.
        """
        if len(str(phone_number)) != 10:
            len(str(phone_number))
            raise ValueError("Contact number must be a 10-digit numeric phone number.")


        return get_data(
            base_url=self.base_url,
            request_type='POST',
            endpoint='phone',
            payload={
                "Phone": phone_number
            },
            headers=self.headers
        )
    

    def get_phone_details_in_bulk(self, phone_numbers_list: list) -> list:
        """
        A function that gets the details for multiple phone  numbers in bulk.
        
        Parameters:
            - phone_numbers: list, (REQUIRED)
                List of 10-digit numeric phone numbers (without spaces, dashes, or parentheses), 
                not greater than 100 numbers in a list

        Returns:
            A list of dictionaries containing the details of the phone  numbers.
        
        Raises:
            ValueError: If any phone  number in the list is not a 10-digit number.
        """
        if len(phone_numbers_list) > 100:
            raise ValueError("Maximum range of allowed numbers are 100.")

        for phone_number in phone_numbers_list:
            if len(str(phone_number)) != 10:
                raise ValueError(f"phone number: {phone_number} is not a 10 digit number, \
                All phone  numbers in the list must be 10-digit numeric phone numbers.")

        output_data = [
                        get_data(
                            base_url=self.base_url,
                            headers=self.headers,
                            request_type='POST',
                            endpoint='phone',
                            payload={
                                "Phone": phone 
                            }
                        ) for phone in phone_numbers_list
                    ]

        return output_data

    def get_email(self, email: str) -> dict:
        """
        A function that gets the details by email.
        
        Parameters:
            - email: str, (REQUIRED)
                100 characters max.

        Returns:
            A dictionary containing the details of the email.

        Raises:
            ValueError: If email is not a 10-digit number.
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

    def get_email_details_in_bulk(self, email_list: list) -> list:
        """
        A function that gets the details for multiple emails in bulk.
        
        Parameters:
            - email_list: list, (REQUIRED)
                list of valid emails not greater than 100 emails in a list
        Returns:
            A list of dictionaries containing the details of the phone numbers.
        
        Raises:
            ValueError: If any phone number in the list is not a 10-digit number.
        """
        if len(email_list) > 100:
            raise ValueError("Maximum range of allowed emails are 100 .")

        for email in email_list:
            if '@' not in email:
                raise ValueError(f"email: {email} is not valid.")

        output_data = [
                        get_data(
                            base_url=self.base_url,
                            headers=self.headers,
                            request_type='POST',
                            endpoint='email',
                            payload={
                                "Email": email
                            }
                        ) for email in email_list
                    ]

        return output_data
