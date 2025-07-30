import requests
import os

from .APIRepo import APIRepo


class MailsRepo(APIRepo):
    def send(self, body):
        return requests.post(self.url + "mails/send", json=body, stream=True)
