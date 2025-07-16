# 0x03-Unittests_and_integration_tests

This project focuses on understanding and implementing unit tests and integration tests in Python using the `unittest` framework. It covers key testing concepts such as mocking, parametrization, and fixtures.

## Project Structure

-   `utils.py`: Contains utility functions for nested dictionary access, fetching JSON from URLs, and a memoization decorator.
-   `client.py`: Implements a `GithubOrgClient` class to interact with the GitHub API, utilizing the `utils` functions.
-   `fixtures.py`: Provides predefined payloads and expected results for testing the `GithubOrgClient`.
-   `test_utils.py`: Contains unit tests for the functions defined in `utils.py`.
-   `test_client.py`: Contains unit and integration tests for the `GithubOrgClient` class in `client.py`.

## How to Run Tests

To run the tests, navigate to the root of the project directory and execute the following commands:

\`\`\`bash
python3 -m unittest test_utils.py
python3 -m unittest test_client.py
\`\`\`

Or to run all tests:

\`\`\`bash
python3 -m unittest discover .
\`\`\`

## Learning Objectives

By completing this project, you should be able to:
-   Differentiate between unit tests and integration tests.
-   Apply common testing patterns like mocking external calls.
-   Use parametrization to test functions with multiple inputs.
-   Understand and utilize fixtures for setting up test environments.
