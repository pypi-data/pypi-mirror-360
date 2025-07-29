import time

import requests
from requests import JSONDecodeError

from autowebx import AccountError
from autowebx.account import Account


def domains():
    return [element['domain'] for element in requests.get('https://api.mail.tm/domains').json()['hydra:member']]


class MailTMAccount(Account):

    def __init__(
            self, **kwargs
    ):
        super().__init__(**kwargs)
        data = {
            'address': self.email.lower(),
            'password': self.password
        }
        while True:
            try:
                response = requests.post('https://api.mail.tm/accounts', json=data).json()
                self.id = response['id']
                break
            except KeyError:
                raise AccountError()
            except JSONDecodeError:
                pass
        while True:
            try:
                token = requests.post('https://api.mail.tm/token', json=data).json()['token']
                break
            except JSONDecodeError:
                pass
        self.headers = {'Authorization': f"Bearer {token}"}

    def messages(self, timeout: float = 30):
        start = time.time()
        while True:
            while True:
                try:
                    response = requests.get('https://api.mail.tm/messages', headers=self.headers).json()
                    break
                except JSONDecodeError:
                    pass
                if time.time() - start > timeout:
                    raise TimeoutError
            if response['hydra:totalItems'] > 0:
                messages = []
                for member in response['hydra:member']:
                    url = f'https://api.mail.tm/messages/{member["id"]}'
                    while True:
                        try:
                            messages.append(requests.get(url, headers=self.headers).json()['html'])
                            break
                        except JSONDecodeError:
                            pass

                print(messages)
                if response['hydra:totalItems'] == 1:
                    return messages[0][0]
                else:
                    return messages[0]
            if time.time() - start > timeout:
                raise TimeoutError('No message received')
