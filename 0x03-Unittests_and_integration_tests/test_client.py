#!/usr/bin/env python3
"""Unit test for GithubOrgClient.org"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
import sys
import os

# Ensure current dir is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test that GithubOrgClient.org returns the expected payload
        and that get_json is called exactly once with the correct URL.
        """
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org  # GithubOrgClient.org being tested explicitly here

        # Check that the returned value matches the mocked payload
        self.assertEqual(result, expected_payload)

        # Ensure get_json was called exactly once with the expected URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )


if __name__ == "__main__":
    unittest.main()
