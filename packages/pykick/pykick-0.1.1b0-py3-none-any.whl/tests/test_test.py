from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import unittest
import unittest.mock as mock

import src.kickpy as kickpy

from src.kickpy import models
from tests.data import ALL_SCOPES, PK_1


class TestExample(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.client_ut = kickpy.KickClient(
            "test_client_id",
            "test_client_secret",
            scopes=ALL_SCOPES,
            http_client_cls=mock.AsyncMock  # Mocking the HTTP client for testing
        )

        self.client_ut._token = kickpy.Token(client=self.client_ut, data={}, cache_id="test_cache_id")
        self.client_ut._kick_http_client = mock.Mock()

    def test_version_exists(self):
        self.assertIsNotNone(kickpy.__version__)

    async def test_example(self):
        pkr = models.PublicKeyResponse(public_key=PK_1)

        self.client_ut._kick_http_client.fetch_public_key = mock.AsyncMock(return_value=pkr)

        should_be_cryptographic_type = await self.client_ut.oauth.fetch_public_key()

        self.assertIsInstance(should_be_cryptographic_type, rsa.RSAPublicKey)
        self.assertEqual(
            should_be_cryptographic_type.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo),
            pkr.public_key.encode("utf-8")
        )

    def test_another_example(self):
        self.assertTrue(True)

    def test_failure_example(self):
        self.assertEqual(1 + 1, 3)
