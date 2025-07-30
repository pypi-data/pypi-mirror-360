# SarvClient API Interaction Module

## Overview

The **SarvClient** module provides a Python interface for interacting with the SarvCRM API. It simplifies authentication, CRUD operations, and module-specific functionalities for seamless integration with SarvCRM.

[SarvCRM API Documents](https://app.sarvcrm.com/webservice/)

## Features
- **Authentication**: Log in and manage sessions with the SarvCRM API.
- **CRUD Operations**: Perform Create, Read, Update, and Delete transactions via simple methods.
- **Context Manager Support**: Automatically handle login and logout within `with` statements.
- **Localization**: Supports specifying the desired language for API interactions.
- **Utility Methods**: Format dates, times, and other helper functionalities compliant with SarvCRM standards.

---

## Installation

1. Ensure you have Python 3.9+ installed.
2. Make Sure pip and git are installed
3. Install the package
   ```bash
   pip install py-sarvcrm-api
   ```

---

## Quick Start

### Example Usage

```python
from sarvcrm_api import SarvClient, SarvURL

# SarvURL = 'https://app.sarvcrm.com/API.php'

# Initialize the client
client = SarvClient(
    url=SarvURL, # specify your own url if you have local server
    utype="your_utype",
    username="your_username",
    password="your_password",
    language="en_US",
    is_password_md5=True, # if your password is already md5
)

# Use as a context manager for clean execution
print(f'Connecting to {SarvURL}')
with client:
    # Create new item in Accounts
    uid = client.Accounts.create(type='Corporate', name='RadinSystem', numbers=['02145885000'])
    print(f'New Account Created: {uid}')
    
    # Read one item record
    record = clinet.Accounts.read_record(uid)
    print(f'Single Account record: {record}')

    # Read List of items
    records = client.Accounts.read_list(order_by='name')
    print('Accounts list:')
    for account in Accounts:
        print(f' - {account}')

    # Update an item
    updated_item = client.Accounts.update(uid, name='Radin-System')
    print(f'Updated item id: {updated_item}')

    # Search for data by phone number
    result = client.search_by_number(number="02145885000", module=client.Accounts) # module is optional
    print(f'Search by number result: {result}')

    # Delete Item
    deleted_item = client.Accounts.delete(uid)
    print(f'Deleted item: {deleted_item}')

```
## Additional Features

- **Error Handling**: Raise `SarvException` for API errors.
- **Secure Defaults**: Passwords are hashed with MD5 unless explicitly provided as pre-hashed.
- **Easy Intraction**: Added all modules and methods for easy intraction.

---

## Developers

### Testing
  - **Pytest Support**: For testing create the `.env` file from `.env_example` and use pytest for start testing.
  - **Test Cases**: For now simple test methods are used and more test cases will be add soon.

## License

This module is licensed for Radin System. For details, see the [LICENSE](LICENSE) file.
