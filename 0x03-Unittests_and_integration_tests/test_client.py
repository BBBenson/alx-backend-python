#!/usr/bin/env python3
"""
Unit and integration tests for the client module.
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from typing import Dict, List, Any, Tuple

import client
import fixtures
import requests # Required for MockResponse and HTTPError in integration test

class TestGithubOrgClient(unittest.TestCase):
  """
  Tests for the GithubOrgClient class.
  """

  @parameterized.expand([
      ("google",),
      ("abc",),
  ])
  @patch('client.get_json')
  def test_org(self, org_name: str, mock_get_json: Mock) -> None:
      """
      Tests that GithubOrgClient.org returns the correct value and
      get_json is called once with the expected argument.
      """
      expected_url = f"https://api.github.com/orgs/{org_name}"
      mock_get_json.return_value = {"login": org_name} # Mock a simple response

      github_client = client.GithubOrgClient(org_name)
      result = github_client.org

      self.assertEqual(result, {"login": org_name})
      mock_get_json.assert_called_once_with(expected_url)

  def test_public_repos_url(self) -> None:
      """
      Tests that _public_repos_url returns the expected URL based on
      the mocked org payload.
      """
      test_payload = {"repos_url": "http://example.com/repos"}
      with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
          mock_org.return_value = test_payload
          github_client = client.GithubOrgClient("test_org")
          self.assertEqual(github_client._public_repos_url, "http://example.com/repos")
          mock_org.assert_called_once()

  @patch('client.get_json')
  def test_public_repos(self, mock_get_json: Mock) -> None:
      """
      Tests that public_repos returns the expected list of repository names
      and that mocked methods are called once.
      """
      # Mock the return value of get_json for the repos payload
      mock_get_json.return_value = [
          {"name": "repo1", "private": False, "license": {"key": "apache-2.0"}},
          {"name": "repo2", "private": False, "license": {"key": "mit"}},
          {"name": "private_repo", "private": True, "license": None},
      ]
      
      # Mock the _public_repos_url property
      with patch('client.GithubOrgClient._public_repos_url', new_callable=PropertyMock) as mock_public_repos_url:
          mock_public_repos_url.return_value = "http://example.com/repos"

          github_client = client.GithubOrgClient("test_org")
          
          # Test without license filter
          repos = github_client.public_repos()
          self.assertEqual(repos, ["repo1", "repo2"])
          
          # Test with license filter
          apache_repos = github_client.public_repos(license="apache-2.0")
          self.assertEqual(apache_repos, ["repo1"])

          # Assert that mocked methods were called
          mock_public_repos_url.assert_called() # Called twice (once for each public_repos call)
          mock_get_json.assert_called() # Called twice (once for each public_repos call)


  @parameterized.expand([
      ({"license": {"key": "my_license"}}, "my_license", True),
      ({"license": {"key": "other_license"}}, "my_license", False),
      ({"license": None}, "my_license", False),
      ({}, "my_license", False),
  ])
  def test_has_license(self, repo: Dict[str, Any], license_key: str, expected_result: bool) -> None:
      """
      Tests that has_license returns the correct boolean value.
      """
      result = client.GithubOrgClient.has_license(repo, license_key)
      self.assertEqual(result, expected_result)


class MockResponse:
  """Helper class to mock requests.Response objects."""
  def __init__(self, json_data: Dict, status_code: int = 200) -> None:
      """Initializes MockResponse."""
      self.json_data = json_data
      self.status_code = status_code

  def json(self) -> Dict:
      """Returns the mocked JSON data."""
      return self.json_data

  def raise_for_status(self) -> None:
      """Mocks raise_for_status to raise HTTPError for bad status codes."""
      if self.status_code >= 400:
          raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")


@parameterized_class([
  {
      "org_payload": fixtures.org_payload,
      "repos_payload": fixtures.repos_payload,
      "expected_repos": fixtures.expected_repos,
      "apache2_repos": fixtures.apache2_repos,
  }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
  """
  Integration tests for the GithubOrgClient.public_repos method.
  """
  org_payload: Dict[str, Any]
  repos_payload: List[Dict[str, Any]]
  expected_repos: List[str]
  apache2_repos: List[str]

  @classmethod
  def setUpClass(cls) -> None:
      """
      Sets up the class for integration tests by mocking requests.get.
      """
      cls.get_patcher = patch('requests.get')
      cls.mock_get = cls.get_patcher.start()

      def side_effect_func(url: str) -> MockResponse:
          """
          Custom side effect function to return different payloads based on URL.
          """
          if url == cls.org_payload["url"]:
              return MockResponse(cls.org_payload)
          elif url == cls.org_payload["repos_url"]:
              return MockResponse(cls.repos_payload)
          return MockResponse({}, 404) # Default for other URLs

      cls.mock_get.side_effect = side_effect_func

  @classmethod
  def tearDownClass(cls) -> None:
      """
      Tears down the class by stopping the requests.get patcher.
      """
      cls.get_patcher.stop()

  def test_public_repos(self) -> None:
      """
      Tests the public_repos method in an integration setting without license.
      """
      github_client = client.GithubOrgClient("google")
      self.assertEqual(github_client.public_repos(), self.expected_repos)
      self.mock_get.assert_called() # Ensure calls were made

  def test_public_repos_with_license(self) -> None:
      """
      Tests the public_repos method in an integration setting with license.
      """
      github_client = client.GithubOrgClient("google")
      self.assertEqual(github_client.public_repos(license="apache-2.0"), self.apache2_repos)
      self.mock_get.assert_called() # Ensure calls were made
