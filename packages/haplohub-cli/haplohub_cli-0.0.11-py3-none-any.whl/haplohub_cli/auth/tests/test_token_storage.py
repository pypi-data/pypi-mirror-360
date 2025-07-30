import json

from pyfakefs.fake_filesystem_unittest import TestCase

from haplohub_cli.auth.token_storage import TokenStorage


class TokenStorageTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setUpClassPyfakefs()
        cls.instance = TokenStorage("/tmp/test_token_storage.json")

    def test_credentials_exist_should_return_false_when_file_does_not_exist(self):
        self.assertFalse(self.instance.credentials_exist)

    def test_credentials_exist_should_return_true_when_file_exists(self):
        with open(self.instance.token_file, "w"):
            pass

        self.assertTrue(self.instance.credentials_exist)

    def test_store_credentials_should_save_credentials_to_file(self):
        creds = {"test": True}

        self.instance.store_credentials(creds)

        with open(self.instance.token_file, "r") as f:
            self.assertEqual(json.load(f), creds)

    def test_get_credentials_should_return_credentials_from_file(self):
        creds = {"test": True}

        self.instance.store_credentials(creds)

        self.assertEqual(self.instance.get_credentials(), creds)

    def test_get_access_token_should_return_access_token_from_credentials(self):
        creds = {"access_token": "123456"}

        self.instance.store_credentials(creds)

        self.assertEqual(self.instance.get_access_token(), "123456")
