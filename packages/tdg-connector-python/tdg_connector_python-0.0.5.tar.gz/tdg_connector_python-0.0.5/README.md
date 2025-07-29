# Project description
## tdg-api-connector Python Client

This Python Client is the official Python Wrapper around the TDG API.

### Installation
Install from pip:

```
pip install tdg-connector
```

### Usage

All the API calls are wrapped in the tdg_api_connector package 

In your Python application, import the packages with __import tdg_api_connector.api__ with the required api and pass authentication information to initialize it:


```
from tdg_api_connector.api.append import AppendAPI
data = AppendAPI('api-key')
```


### AppendAPI


* __get_phone__ :-
> A function that allows users to query for phone numbers matching names and addresses
by providing certain input fields such as first name, last name, address, and zip 
code. The API then returns appended telephone numbers along with other phone 
attributes such as record type, telephone confidence score, and directory assistance flag.
>
**Parameters:**

>   - `first_name`: str, (REQUIRED)
        The first name of the individual (up to 15 characters).\n
>    - `last_name`: str, (REQUIRED)
        The last name of the individual (up to 15 characters).
>    - `address`: str, (REQUIRED)
        The address of the individual (up to 60 characters).
>   - `zip_number`: int, (REQUIRED)
        5-digit numeric USPS zip code. Either City/State or Zip is required.

```
from tdg_api_connector.api.append import AppendAPI
connector = AppendAPI('api-key')
data = connector.get_phone('first_name', 'last_name', 'address', 'zip_number')
```

---
* __get_email__ :-
> A function that retrieves email details based on names and addresses.
The Api returns appended email when suppression is False along with other attributes 
score, category, suppression.
>
**Parameters:**

>   - `first_name`: str, (REQUIRED)
        The first name of the individual (up to 15 characters).
>   - `last_name`: str, (REQUIRED)
        The last name of the individual (up to 20 characters).
>   - `address`: str, (REQUIRED)
        The address of the individual (up to 64 characters).
>   - `zip_number`: int, (REQUIRED)
        5-digit numeric USPS zip code.

```
from tdg_api_connector.api.append import AppendAPI
connector = AppendAPI('api-key')
data = connector.get_email('first_name', 'last_name', 'address', 'zip_number')
```

---
* __get_demographic__ :-
> A function that retrieves details demographic details based on 
names, addresses, (email or phone number).
>
**Parameters:**

>    - `first_name`: str, (Should be a combination of FName, LName, Zip, and 
        Address parameters; Phone or Email is REQUIRED)
        The first name of the individual (up to 15 characters).
>    - `last_name`: str, (Should be a combination of FName, LName, Zip, and 
        Address parameters; Phone or Email is REQUIRED)
        The last name of the individual (up to 20 characters).            
>    - `address`: str, (Should be a combination of FName, LName, Zip, and 
        Address parameters; Phone or Email is REQUIRED)
        Address 64 characters max.
>    - `zip_number`: int, (Should be a combination of FName, LName, Zip, and 
        Address parameters; Phone or Email is REQUIRED)
        5-digit numeric USPS zip code. * Either City/State or Zip is required.
>    - `phone`: int, (REQUIRED if Email is not included and other parameters are included)
        10 digit numeric phone number (without spaces, dashes, or parentheses)
>    - `email`: str, (REQUIRED if phone is not included and other parameters are included)
        Email address, 100 characters max
>    - `city`: (OPTIONAL)
        City name, 28 characters max. * Either City/State or Zip is required.
>    - `state`: (OPTIONAL)
        2 character state abbreviation. * Either City/State or Zip is required.

 
```
from tdg_api_connector.api.append import AppendAPI
connector = AppendAPI('api-key')
data = connector.get_demographic('first_name', 'last_name', 'address', 'zip_number', 'phone', 'email')
```

---
* __get_auto__ :-
>A function that retrieves Auto/Vehicles details based on names and addresses.
>
**Parameters:**
   
>    - `full_name`: str, (REQUIRED)
        The full name of the individual 
>    - `address`: str, (REQUIRED)
        The address of the individual (up to 64 characters).
>    - `zip_number`: int, (REQUIRED)
        5-digit numeric USPS zip code.
>    - `phone`: int, (REQUIRED if Email is not included and other parameters are included)
        10 digit numeric phone number (without spaces, dashes, or parentheses)
>    - `email`: str, (REQUIRED if phone is not included and other parameters are included)
        Email address, 100 characters max
```
from tdg_api_connector.api.append import AppendAPI
connector = AppendAPI('api-key')
data = connector.get_auto('full_name', 'address', 'zip_number', 'phone', 'email')
```
---


### LookupAPI

* __get_phone__ :-
>A function that gets the details for a single phone number.
>
**Parameters**:

>    - `phone_number`: int, (REQUIRED)
        10-digit numeric phone number (without spaces, dashes, or parentheses).
```
from tdg_api_connector.api.lookup import LookupAPI
connector = LookupAPI('api-key')
data = connector.get_phone('phone')
```
---

* __get_email__ :-
>A function that gets the details by email.
>
**Parameters**:

>    - `email`: str, (REQUIRED)
        100 characters max.

```
from tdg_api_connector.api.lookup import LookupAPI
connector = LookupAPI('api-key')
data = connector.get_email('email')
```
---
* __get_email_details_in_bulk__ :-
>A function that gets the details for multiple emails in bulk.
>
**Parameters**:

>    - `email_list`: list, (REQUIRED)
        list of valid emails not greater than 100 emails in a list
```
from tdg_api_connector.api.lookup import LookupAPI
connector = LookupAPI('api-key')
data = connector.get_email_details_in_bulk(['email@abc.com', 'email2@abc.com'])
```
---
* __get_phone_details_in_bulk__ :-
>A function that gets the details for multiple phone  numbers in bulk.
>
**Parameters**:

>    - `phone_numbers`: list, (REQUIRED)
                    List of 10-digit numeric phone numbers (without spaces, dashes, or parentheses), 
                    not greater than 100 numbers in a list

```
from tdg_api_connector.api.lookup import LookupAPI
connector = LookupAPI('api-key')
data = connector.get_phone_details_in_bulk([5555555555, 5555555555])
```
---

### VerifyAPI
* __get_id__ 
>This function is used to assess the validity of consumer contact information, 
identify potential risks or fraud, and make informed decisions based on the 
verification scores and summaries provided by the service. 
>
**Parameters**: 
        (ATLEAST 2 PARAMETERS WITH ANY COMBINATION REQUIRED TO CHECK THE ACCURACY SCORE):

>    - `first_name`: str
        The first name of the individual. Maximum 15 characters.
>    - `last_name`: str
        The last name of the individual. Maximum 20 characters.
>    - `address`: str
        The address of the individual. Maximum 64 characters.
>    - `zip_number`: int
        The 5-digit numeric USPS zip code. Either City/State or Zip is required.
>    - `phone`: str
        The 10-digit numeric phone number without spaces, dashes, or parentheses.
>    - `email`: str
        The email address of the individual. Maximum 100 characters.

```
from tdg_api_connector.api.verify import VerifyAPI
connector = VerifyAPI('api-key')
data = connector.get_id('first_name', 'last_name')
```
---
* __get_tcpa_info__ 
>Function to make a request to the TCPA Verify endpoint to mitigate 
TCPA risk by identifying wireless numbers and offering identity verification 
for called party consent.
>
**Parameters**: 

>    - `phone` (Required)  
        10 digit numeric phone number (without spaces, dashes, or parentheses)
>    - `last_name` (Required)
        The last name of the individual. Maximum 20 characters.

```
from tdg_api_connector.api.verify import VerifyAPI
connector = VerifyAPI('api-key')
data = connector.get_tcpa_info('phone', 'last_name')
```
---
* __get_email__ 
>Function  is responsible for validating whether a given email address is correctly formatted and optionally whether it exists or can receive emails. It can be used to prevent invalid or disposable email addresses from being submitted to the system.
>
**Parameters**:

>    - `email`: str (Required)  
        The email address to verify. Maximum 100 characters.

```
from tdg_api_connector.api.verify import VerifyAPI
connector = VerifyAPI('api-key')
data = connector.get_email('email')
```
---

