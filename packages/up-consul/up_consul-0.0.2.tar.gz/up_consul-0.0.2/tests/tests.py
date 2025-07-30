import unittest

from up_consul.client import KVClient


class TestCompileServiceSettings(unittest.TestCase):

    def test_kv_compile_service_settings__basic(self):
        """Test basic functionality with a simple key-value pair structure."""
        settings = {
            'services/my-service/config/timeout': '30',
            'services/my-service/config/retries': '5'
        }
        expected_output = {
            'config': {
                'timeout': '30',
                'retries': '5'
            }
        }
        self.assertEqual(
            KVClient.compile_service_settings('services/my-service', settings),
            expected_output
        )

    def test_kv_compile_service_settings__nested_structure(self):
        """Test this function handles nested dictionary structures correctly."""
        settings = {
            'services/my-service/config/database/host': 'localhost',
            'services/my-service/config/database/port': '5432'
        }
        expected_output = {
            'config': {
                'database': {
                    'host': 'localhost',
                    'port': '5432'
                }
            }
        }
        self.assertEqual(
            KVClient.compile_service_settings('services/my-service', settings),
            expected_output
        )

    def test_kv_compile_service_settings__no_key_base(self):
        """Test this function still works when no key_base is given."""
        settings = {
            'config/database/host': 'localhost',
            'config/database/port': '5432'
        }
        expected_output = {
            'config': {
                'database': {
                    'host': 'localhost',
                    'port': '5432'
                }
            }
        }
        self.assertEqual(
            KVClient.compile_service_settings('', settings),
            expected_output
        )

    def test_kv_compile_service_settings__single_setting(self):
        """Test this function works correctly with just one setting."""
        settings = {
            'services/my-service/config/timeout': '30'
        }
        expected_output = {
            'config': {
                'timeout': '30'
            }
        }
        self.assertEqual(
            KVClient.compile_service_settings('services/my-service', settings),
            expected_output
        )

    def test_kv_compile_service_settings__empty_settings(self):
        """Test this function handles empty settings correctly."""
        settings = {}
        expected_output = {}
        self.assertEqual(
            KVClient.compile_service_settings('services/my-service', settings),
            expected_output
        )

    # ## TODO: This test currently fails
    # def test_kv_compile_service_settings__mismatched_key_base(self):
    #     """Test functionality when incorrect key_base is given."""
    #     settings = {
    #         'other-service/config/timeout': '30',
    #     }
    #     expected_output = {
    #         'other-service/config/timeout': '30'
    #     }
    #     self.assertEqual(
    #         KVClient.compile_service_settings('services/my-service', settings),
    #         expected_output
    #     )

    def test_kv_compile_service_settings__multiple_key_levels(self):
        """Test function behaviour with a deeply nested key structure."""
        key_base = "app/config"
        settings = {
            "app/config/service/database/host": "localhost",
            "app/config/service/database/port": "5432",
            "app/config/service/worker/threads": "10"
        }
        expected_output = {
            "service": {
                "database": {
                    "host": "localhost",
                    "port": "5432"
                },
                "worker": {
                    "threads": "10"
                }
            }
        }
        result = KVClient.compile_service_settings(key_base, settings)
        self.assertEqual(result, expected_output)
