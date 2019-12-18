""" Mailgun Module """

import time
import datetime
import email

import requests

# CONSTANTS
class Mailgun:
    """
    Mailgun API wrapper.

    :param domain: Mailgun Domain
    :api_key:      Mailgun API Key
    :retry:        Number of times to retry
    """
    DELIVERY_SUCCESS = 'delivered'
    DELIVERY_FAILURE = 'failed'
    STATUS_UNDELIVERABLE = 'undeliverable'

    def __init__(self, domain, api_key, retry_limit=5):
        """
        Constructor
        """
        self.__domain = domain  
        self.__api_key = api_key
        self.__retry_limit = retry_limit
        self.__retry_interval = 5
        self.__base_url = 'https://api.mailgun.net'
        self.__send_api_version = 'v3'
        self.__validate_api_version = 'v4'
        self.__mail_from = None

    def __http_get(self, url, params):
        """
        Send a Http GET request.
        """
        return requests.get(
            url=url,
            params=params,
            auth=('api', self.__api_key)
        )

    def __http_post(self, url, data):
        """
        Send a Http POST request.
        """
        return requests.post(
            url=url,
            data=data,
            auth=('api', self.__api_key)
        )

    def __get_validate_api_url(self):
        """
        Get URL for the validate API.
        """
        return '{endpoint}/{version}/address/validate'.format(
            endpoint=self.__base_url,
            version=self.__validate_api_version
        )

    def __get_messages_api_url(self):
        """
        Get URL for the messages API.
        """
        return '{endpoint}/{version}/{domain}/messages'.format(
            endpoint=self.__base_url,
            version=self.__send_api_version,
            domain=self.__domain
        )

    def __get_events_api_url(self):
        """
        Get URL for the events API.
        """
        return '{endpoint}/{version}/{domain}/events'.format(
            endpoint=self.__base_url,
            version=self.__send_api_version,
            domain=self.__domain
        )

    def __retry(self, func, params=None):
        """
        Retry the specified function while below conditions are met.

        1. It returns False
        2. Retry count is less than retry limit
        """
        is_success = False
        retry_count = 0
        while not is_success and retry_count < self.__retry_limit:
            try:
                is_success = func(params)
            except ConnectionResetError:
                print('{} Retry {}/{}...'.format(
                    __name__,
                    retry_count,
                    self.__retry_limit
                ))
                continue
            finally:
                time.sleep(self.__retry_interval)
                retry_count += 1
        return is_success

    def __is_delivered(self, target_email):
        """
        Check if the specified email is delivered or not.
        """
        items = self.events(
            target_email=target_email,
            event=self.DELIVERY_SUCCESS
        )['items']
        return len(items) > 0 and items[0]['event'] == self.DELIVERY_SUCCESS

    def __is_failed(self, target_email):
        """
        Check if the specified email is failed or not.
        """
        items = self.events(
            target_email=target_email,
            event='rejected OR failed'
        )['items']
        return len(items) > 0 and items[0]['event'] == self.DELIVERY_FAILURE

    @property
    def mail_from(self):
        """
        Get an email for the 'From' email header.
        """
        return self.__mail_from

    @mail_from.setter
    def mail_from(self, mail_from):
        """
        Set an email for the 'From' email header.
        """
        self.__mail_from = mail_from

    def validate(self, target_email):
        """
        Verify whether the specified email is valid or not.

        Calls mailgun's validate API.
        """
        return self.__http_get(
            url=self.__get_validate_api_url(),
            params={ 'address': target_email }
        ).json()

    def messages(self, to, subject, html, text):
        """
        Send an email to the specified address.

        Calls mailgun's messages API.
        """
        if self.__mail_from is None:
            raise Exception('"From" header is not set.')
        return self.__http_post(
            url=self.__get_messages_api_url(),
            data={
                'to': to,
                'subject': subject,
                'from': self.__mail_from,
                'html': html,
                'text': text
            }
        ).json()

    def events(self, target_email, event):
        """
        Check the event status of the specified email.

        Calls mailgun's events API.
        """
        last_hour = datetime.datetime.now() - datetime.timedelta(hours=1)
        timestamp = time.mktime(last_hour.timetuple())
        return self.__http_get(
            url=self.__get_events_api_url(),
            params={
                'begin': email.utils.formatdate(timestamp),
                'ascending': 'yes',
                'limit': 300,
                'pretty': 'yes',
                'event': event,
                'recipient': target_email
            }
        ).json()

    def is_valid(self, target_email):
        """
        Check if the specified email is valid or not.
        """
        response = self.validate(target_email)
        if 'result' in response.keys():
            return response['result'] != self.STATUS_UNDELIVERABLE
        return False

    def is_delivered(self, target_email):
        """
        Check if the specified email is delivered or not.
        """
        return self.__retry(self.__is_delivered, target_email)

    def is_failed(self, target_email):
        """
        Check if the specified email delivery is failed or not.
        """
        return self.__retry(self.__is_failed, target_email)
