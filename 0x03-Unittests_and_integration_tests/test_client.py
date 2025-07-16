#!/usr/bin/env python3
"""Unit & integration tests for client.py"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from typing import Dict, List
import requests
import sys
import os

# Ensure current dir is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Test org returns correct data"""
        mock_get_json.return_value = {"login": org_name}
        client_instance = GithubOrgClient(org_name)
        self.assertEqual(client_instance.org, {"login": org_name})
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org: PropertyMock) -> None:
        """Test _public_repos_url returns expected URL"""
        mock_org.return_value = {"repos_url": "http://some.url"}
        client_instance = GithubOrgClient("google")
        self.assertEqual(client_instance._public_repos_url, "http://some.url")

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test public_repos"""
        mock_get_json.return_value = TEST_PAYLOAD[0][1]
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "http://some.url"
            client_instance = GithubOrgClient("google")
            self.assertEqual(
                client_instance.public_repos(),
                TEST_PAYLOAD[0][2]
            )
            mock_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str,
                         expected: bool) -> None:
        """Test has_license returns expected result"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key), expected
        )


class MockResponse:
    """Helper class to mock requests.Response objects."""

    def __init__(self, json_data: Dict, status_code: int = 200) -> None:
        self.json_data = json_data
        self.status_code = status_code

    def json(self) -> Dict:
        return self.json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests"""
    org_payload: Dict
    repos_payload: List
    expected_repos: List
    apache2_repos: List

    @classmethod
    def setUpClass(cls) -> None:
        """Setup mocks"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def side_effect_func(url: str) -> MockResponse:
            if url == f"https://api.github.com/orgs/google":
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                return MockResponse(cls.repos_payload)
            return MockResponse({}, 404)

        cls.mock_get.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test public_repos output"""
        client_instance = GithubOrgClient("google")
        self.assertEqual(client_instance.public_repos(), self.expected_repos)

        calls = self.mock_get.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args[0],
                         "https://api.github.com/orgs/google")
        self.assertEqual(calls[1].args[0],
                         self.org_payload["repos_url"])

    def test_public_repos_with_license(self) -> None:
        """Test public_repos with license"""
        client_instance = GithubOrgClient("google")
        self.assertEqual(
            client_instance.public_repos(license="apache-2.0"),
            self.apache2_repos
        )

        calls = self.mock_get.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args[0],
                         "https://api.github.com/orgs/google")
        self.assertEqual(calls[1].args[0],
                         self.org_payload["repos_url"])


if __name__ == "__main__":
    unittest.main()
