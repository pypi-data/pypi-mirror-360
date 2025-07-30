"""Limited functionality Consul Python client."""
import base64
from dataclasses import dataclass, field
from functools import wraps
import json
from logging import getLogger

import requests


logger = getLogger(__name__)


def managed_request_json(func):
    """Handle an http response, and return response json of 200 responses.
    Raise an HTTPError if a non-200 response is returned.

    Can be expanded in future to handle different kinds of responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if not str(response.status_code).startswith('20'):
            response.raise_for_status()
        return response.json()
    return wrapper


@dataclass
class ConsulClient:

    host: str = field(repr=True, default='')
    token: str = field(repr=False, default='')
    port: int = field(repr=True, default=None)
    url_scheme: int = field(repr=True, default='https')

    def __post_init__(self):
        """Set tokens Authorization header and add it to request sessions."""
        self.endpoint = f'{self.url_scheme}://{self.host}'
        if self.port:
            self.endpoint = f'{self.endpoint}:{self.port}'

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.session.verify = True

        self.kv = KVClient(self.session, self.endpoint)
        # In future, this can be extended to include other API endpoints.

    def __str__(self):
        return self.__class__.__name__


@dataclass
class KVClient:

    session: type(requests.session)
    endpoint: str

    @managed_request_json
    def delete_one(self, key_prefix):
        response = self.session.delete(f'{self.endpoint}/v1/kv/{key_prefix}')
        return response

    @managed_request_json
    def _get_data_many(self, key_prefix):
        """Get Data from all keys with prefix.

        Args:
            key_prefix (str): prefix of keys to search.

        Returns:
            list: Raw data returned for all matching keys.
        """
        response = self.session.get(
            f'{self.endpoint}/v1/kv/{key_prefix}',
            params=dict(recurse=True),
        )
        return response

    @managed_request_json
    def _get_data_one(self, key):
        """Get Data for a single key.

        Args:
            key (str): Key to search

        Returns:
            list: single raw data item returned for the key searched.
        """
        response = self.session.get(f'{self.endpoint}/v1/kv/{key}')
        return response

    @managed_request_json
    def _set_data_one(self, key, value):
        """Set value for data stored at a single key location.

        Args:
            key (str): Key to use
            key (Any): Value to set

        Returns:
            bool: True if response was successful.
        """
        payload = json.dumps(value).encode()
        response = self.session.put(
            f'{self.endpoint}/v1/kv/{key}',
            data=payload,
        )
        return response

    def get_many(self, key_prefix):
        """Return decoded key: value pairs of all entries matching a key prefix.

        Args:
            key_prefix (str): key prefix to search.

        Returns:
            dict: {key: decoded_value} for each key with the prefix searched.
        """
        data = self._get_data_many(key_prefix)

        return {
            item["Key"]: json.loads(
                base64.b64decode(item["Value"]).decode('utf8')
            ) for item in data
        }

    def get_value(self, key):
        """Get a single value a specific key.

        Args:
            key (str): Key to search against.

        Returns:
            Any: The decoded value stored with that key.
        """
        try:
            item = self._get_data_one(key)[0]
        except (IndexError, TypeError) as e:
            return logger.error(f'Error when calling get_value(): {e}')

        return json.loads(base64.b64decode(item["Value"]).decode('utf8'))

    def set_value(self, key, value):
        response = self._set_data_one(key, value)
        if not response:
            raise ValueError('Value not set')

    @managed_request_json
    def get_keys(self, key_prefix):
        """Fetch only the keys that match a given prefix.

        Args:
            key_prefix (str): Key prefix to search.

        Returns:
            list: All keys that start with the key prefix.
        """
        response = self.session.get(
            f'{self.endpoint}/v1/kv/{key_prefix}',
            params=dict(keys=True),
        )
        return response

    def get_service_codes(self, service_type='metrics'):
        return set(
            key.split('/')[1] for key in self.get_keys(service_type)
        )

    @staticmethod
    def compile_service_settings(key_base, settings):
        """Compile all service settings into a single tree / dictionary.

        Args:
            key_base (str): Common key prefix to remove from final result.
            settings (dict): Key: value pairs of settings, as stored in consul.

        Returns:
            dict: Single dict containing all settings matching a given prefix.
        """
        settings_tree = {}
        key_base = key_base.rstrip('/')
        base_index = len(key_base) + 1 if key_base else 0

        for key, value in settings.items():
            useful_key = key[base_index:]
            key_parts = useful_key.split('/')
            working_dict = settings_tree

            # Traverse through key_parts and build the nested dictionary
            for part in key_parts[:-1]:
                working_dict = working_dict.setdefault(part, {})

            working_dict[key_parts[-1]] = value

        return settings_tree
