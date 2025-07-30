from unittest.mock import patch

import pytest
from jira import JIRAError

from jf_ingest.config import JiraAuthConfig
from jf_ingest.jf_jira.auth import (
    JiraAuthenticationException,
    JiraAuthMethod,
    get_jira_connection,
)
from jf_ingest.jf_jira.exceptions import JiraRetryLimitExceeded


def _get_jira_auth_config(args):
    company_slug = "test_company"
    url = "https://test-co.atlassian.net/"
    return JiraAuthConfig(company_slug=company_slug, url=url, gdpr_active=True, **args)


def test_jira_conn_basic_auth_no_auth():
    config = _get_jira_auth_config({"available_auth_methods": [JiraAuthMethod.BasicAuth]})

    with pytest.raises(RuntimeError) as excinfo:
        get_jira_connection(config)

    assert (
        str(excinfo.value)
        == f"No valid basic authentication mechanism for {config.url} - need a username/password combo or a personal access token"
    )


def test_jira_conn_basic_auth_user_password():
    config = _get_jira_auth_config(
        {
            "available_auth_methods": [JiraAuthMethod.BasicAuth],
            "user": "jira_user@test.co",
            "password": "test_password",  # pragma: allowlist secret
        }
    )

    # TEST BASIC AUTH ERROR LOGIC
    with patch("jf_ingest.jf_jira.auth.JIRA", side_effect=JIRAError(status_code=401)):
        with pytest.raises(JiraAuthenticationException):
            get_jira_connection(config, max_retries=0)

    # TEST BASIC AUTH ERROR LOGIC
    with patch("jf_ingest.jf_jira.auth.JIRA", side_effect=JIRAError(status_code=403)):
        with pytest.raises(JiraAuthenticationException):
            get_jira_connection(config, max_retries=0)


def test_jira_conn_basic_auth_personal_access_token():
    config = _get_jira_auth_config(
        {
            "available_auth_methods": [JiraAuthMethod.BasicAuth],
            "personal_access_token": "a_PAT",
        }
    )

    # TEST BASIC AUTH ERROR LOGIC
    with patch("jf_ingest.jf_jira.auth.JIRA", side_effect=JIRAError(status_code=401)):
        with pytest.raises(JiraAuthenticationException):
            get_jira_connection(config, max_retries=0)

    # TEST BASIC AUTH ERROR LOGIC
    with patch("jf_ingest.jf_jira.auth.JIRA", side_effect=JIRAError(status_code=403)):
        with pytest.raises(JiraAuthenticationException):
            get_jira_connection(config, max_retries=0)
