import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Dict
from unittest.mock import patch

import pytest
import pytz
from requests import Request
import requests_mock
from jira import JIRAError

from jf_ingest.constants import Constants
from jf_ingest.jf_jira.downloaders import (
    IssueMetadata,
    _download_issue_page,
    _expand_changelog,
    _filter_changelogs,
    _get_all_project_issue_counts,
    _get_issue_count_for_jql,
    generate_jql_for_batch_of_ids,
    generate_project_pull_from_bulk_jql,
    generate_project_pull_from_jql,
    get_fields_spec,
    get_jira_search_batch_size,
    pull_jira_issues_by_jira_ids,
)
from jf_ingest.jf_jira.utils import JiraFieldIdentifier
from jf_ingest.utils import batch_iterable
from tests.jf_jira.utils import (
    _register_jira_uri,
    _register_jira_uri_with_file,
    get_jira_mock_connection,
)

logger = logging.getLogger(__name__)


def _generate_mock_address_for_issue_jql(
    m: requests_mock.Mocker,
    jql_query: str,
    issue_count: int,
    start_at: int,
    max_results: int,
    issues: list[dict],
):
    _issues = [issue for issue in issues[start_at : min(start_at + max_results, len(issues))]]
    jira_return_val = f'{{"expand":"names,schema","startAt":{start_at},"maxResults":{max_results},"total":{issue_count},"issues":{json.dumps(_issues)}}}'

    endpoint = (
        f"search?jql={jql_query}&startAt={start_at}&validateQuery=True&maxResults={max_results}"
    )
    _register_jira_uri(
        m,
        endpoint=endpoint,
        return_value=jira_return_val,
    )


def _mock_jira_issue_by_date_endpoints(
    m: requests_mock.Mocker,
    project_keys_to_issue_counts: dict[str, int],
    pull_from: datetime,
    batch_size: int,
    issues_updated_value: datetime = pytz.utc.localize(datetime.min),
    expand_fields: list[str] = ["*all"],
):
    def generate_issues(project_key, count):
        _fields = {}
        if "*all" in expand_fields:
            _fields["updated"] = issues_updated_value.strftime("%Y-%m-%dT%H:%M:%S.000-0000")
        else:
            if "updated" in expand_fields:
                _fields["updated"] = issues_updated_value.strftime("%Y-%m-%dT%H:%M:%S.000-0000")
        return [
            {
                "expand": "operations,versionedRepresentations,editmeta,changelog",
                "id": f"{i}",
                "self": "https://test-co.atlassian.net/rest/api/2/issue/63847",
                "key": f"{project_key}-{i}",
                "fields": _fields,
            }
            for i in range(count)
        ]

    for project_key, count in project_keys_to_issue_counts.items():
        issues = generate_issues(project_key=project_key, count=count)
        jql_query = generate_project_pull_from_jql(project_key=project_key, pull_from=pull_from)
        # Generate one call for getting hte 'first' page (for issue counts)
        _generate_mock_address_for_issue_jql(
            m=m,
            jql_query=jql_query,
            issue_count=count,
            start_at=0,
            issues=issues,
            max_results=1,
        )
        for start_at in range(0, count, batch_size):
            _generate_mock_address_for_issue_jql(
                m=m,
                jql_query=jql_query,
                issue_count=count,
                start_at=start_at,
                max_results=batch_size,
                issues=issues,
            )


def test_get_issue_count_for_jql():
    pull_from = datetime.min
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 5123
    project_key_to_count = {PROJECT_KEY: PROJECT_ISSUE_COUNT}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_key_to_count,
            pull_from=pull_from,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=generate_project_pull_from_jql(project_key=PROJECT_KEY, pull_from=pull_from),
        )
        assert count_for_jql == project_key_to_count[PROJECT_KEY]


def test_get_issue_count_for_jql_400_level_error_handling():
    """Assert that when we raise 400 level errors, we always return 0"""
    for status_code in range(400, 500):
        with patch(
            "jf_ingest.jf_jira.downloaders.retry_for_status",
            side_effect=JIRAError(status_code=status_code),
        ):
            logger.info(
                f"Attempting to test _get_issue_count_for_jql when a {status_code} error is thrown"
            )
            count_for_jql = _get_issue_count_for_jql(get_jira_mock_connection(), jql_query="")
            assert count_for_jql == 0


def test_get_issue_count_for_jql_500_level_error_handling():
    for status_code in range(500, 600):
        logger.info(f"Checking to see if we raise 500 level errors...")
        with patch(
            "jf_ingest.jf_jira.downloaders.retry_for_status",
            side_effect=JIRAError(status_code=status_code),
        ):
            with pytest.raises(JIRAError):
                _get_issue_count_for_jql(get_jira_mock_connection(), jql_query="")


def test_get_all_project_issue_counts():
    pull_from = datetime.min
    project_keys_to_counts = {"PROJ": 151, "COLLAGE": 512}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_keys_to_counts,
            pull_from=pull_from,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        project_keys_to_pull_from = {
            project_key: pull_from for project_key in project_keys_to_counts.keys()
        }
        project_issue_counts = _get_all_project_issue_counts(
            get_jira_mock_connection(mocker),
            project_key_to_pull_from=project_keys_to_pull_from,
            num_parallel_threads=1,
            jql_filter=None,
        )

        assert project_issue_counts == project_keys_to_counts


def _mock_jira_issue_by_ids(
    m: requests_mock.Mocker(),
    issue_ids: list[str],
    batch_size: int,
    issues_updated_value: datetime = datetime.min,
    expand_fields: list[str] = ["*all"],
):
    def _generate_issues(ids_batch):
        _fields = {}
        if "*all" in expand_fields:
            _fields["updated"] = issues_updated_value.isoformat()
            _fields["parent"] = {"id": "PARENT", "key": f"PROJ-PARENT"}
        else:
            if "updated" in expand_fields:
                _fields["updated"] = issues_updated_value.isoformat()
            if "parent" in expand_fields:
                _fields["parent"] = {"id": "PARENT", "key": f"PROJ-PARENT"}

        return [
            {
                "expand": "operations,versionedRepresentations,editmeta,changelog",
                "id": f"{id}",
                "self": "https://test-co.atlassian.net/rest/api/2/issue/63847",
                "key": f"PROJ-{i}",
                "fields": _fields,
            }
            for i, id in enumerate(ids_batch)
        ]

    for id_batch in batch_iterable(sorted(issue_ids, key=int), batch_size=batch_size):
        jql_query = generate_jql_for_batch_of_ids(id_batch)
        _generate_mock_address_for_issue_jql(
            m=m,
            jql_query=jql_query,
            issue_count=len(id_batch),
            start_at=0,
            issues=_generate_issues(id_batch),
            max_results=batch_size,
        )
        
def test_generate_jql_for_batch_ids():
    ids = ["1", "2", "3", "4", "5"]
    jql_query = generate_jql_for_batch_of_ids(ids)
    assert jql_query == 'id in (1,2,3,4,5) order by id asc'
        
def test_generate_jql_for_batch_ids_with_pull_from():
    ids = ["1", "2", "3", "4", "5"]
    pull_from = datetime(2024, 12, 29, 17, 20, 1)
    jql_query = generate_jql_for_batch_of_ids(ids, pull_from)
    assert jql_query == 'id in (1,2,3,4,5) AND updated > "2024-12-29" order by id asc'


def test_get_jira_batch_size():
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":{returned_batch_size},"total":0,"issues":[]}}'

            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield mocker

    optimistic_batch_size = 1000
    for jira_batch_size_return in [0, 10, Constants.MAX_ISSUE_API_BATCH_SIZE, 1000, 1235]:
        with _mocked_jira_return(
            requested_batch_size=optimistic_batch_size,
            returned_batch_size=jira_batch_size_return,
        ) as mocker:
            # Check when fields is left out (it should default to [*all])
            jira_issues_batch_size = get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
            )

            assert jira_issues_batch_size == jira_batch_size_return


def test_get_jira_batch_size_with_variable_field_argument():
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":{returned_batch_size},"total":0,"issues":[]}}'

            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield mocker

    optimistic_batch_size = 1000
    for jira_batch_size_return in [0, 10, Constants.MAX_ISSUE_API_BATCH_SIZE, 1000, 1235]:
        with _mocked_jira_return(
            requested_batch_size=optimistic_batch_size,
            returned_batch_size=jira_batch_size_return,
        ) as mocker:
            # Check when fields is left out (it should default to [*all])
            get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
            )

            def _get_request_body():
                return json.loads(mocker.request_history[-1]._request.body)

            print(json.loads(mocker.request_history[-1]._request.body)['fields'])
            assert _get_request_body()['fields'] == ['*all']

            # Check when fields is set to ['id', 'key']
            fields = ['key', 'id']
            get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
                fields=fields,
            )

            assert _get_request_body()['fields'] == fields

            # Check when fields is set to ['*all'] manually
            fields = ['*all']
            get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
                fields=fields,
            )
            assert _get_request_body()['fields'] == fields


def test_get_fields_spec():
    assert get_fields_spec(include_fields=[], exclude_fields=[]) == ["*all"]
    assert get_fields_spec(include_fields=["updated"], exclude_fields=[]) == ["updated"]
    assert get_fields_spec(include_fields=["updated", "parent"], exclude_fields=[]) == [
        "updated",
        "parent",
    ]
    assert get_fields_spec(include_fields=["updated"], exclude_fields=["parent"]) == [
        "updated",
        "-parent",
    ]


def get_issues_through_test_fixture():
    issue_ids = sorted(["18447", "18404", "18031", "18018", "18016"], key=int)
    jql_query = generate_jql_for_batch_of_ids(issue_ids)
    with requests_mock.Mocker() as m:
        # Register one endpoint that this will hit
        uri = f"search?jql={jql_query}&startAt=0&validateQuery=True&fields=%2Aall&expand=changelog&maxResults=5"
        _register_jira_uri_with_file(m, endpoint=uri, fixture_path="api_responses/issues.json")

        return [
            i
            for i in pull_jira_issues_by_jira_ids(
                jira_connection=get_jira_mock_connection(),
                jira_ids=issue_ids,
                num_parallel_threads=10,
                batch_size=len(issue_ids),
                expand_fields=["changelog"],
                include_fields=[],
                exclude_fields=[],
            )
        ]

CUSTOM_FIELDS_FOR_FILTERING = tuple(["customfield_10051", "customfield_10057", "customfield_10009"])
JFI_FIELDS_FOR_FILTERING = tuple([
    JiraFieldIdentifier(jira_field_id=jira_id, jira_field_name=f'Name: {jira_id}')
    for jira_id in CUSTOM_FIELDS_FOR_FILTERING
])
def test_filter_changelogs_no_filtering():
    issues = get_issues_through_test_fixture()
    issues_without_filtering = _filter_changelogs(issues, [], [])

    for issue in issues_without_filtering:
        for history in issue["changelog"]["histories"]:
            assert len(history["items"]) != 0
            for item in history["items"]:
                if "fieldId" in item:
                    assert item["fieldId"] in CUSTOM_FIELDS_FOR_FILTERING


def test_filter_changelogs_inclusion_filtering_for_madeup_field():
    issues = get_issues_through_test_fixture()
    issues_with_filtering_field_in = _filter_changelogs(issues, [JiraFieldIdentifier(jira_field_id="madeup_field", jira_field_name='Made up Field')], [])
    assert len(issues) == len(issues_with_filtering_field_in)
    for issue in issues_with_filtering_field_in:
        for history in issue["changelog"]["histories"]:
            assert len(history["items"]) == 0

def test_filter_changelogs_exclusion_filtering_for_madeup_field():
    issues = get_issues_through_test_fixture()
    issues_with_filtering_field_in = _filter_changelogs(issues, [], [JiraFieldIdentifier(jira_field_id="madeup_field", jira_field_name='Made up Field')])
    assert len(issues) == len(issues_with_filtering_field_in)
    for issue, filtered_issue in zip(issues, issues_with_filtering_field_in):
        assert len(issue['changelog']['histories']) == len(filtered_issue['changelog']['histories'])
        for history, filtered_history in zip(issue["changelog"]["histories"], filtered_issue['changelog']['histories']):
            assert len(history["items"]) == len(filtered_history['items'])

def test_filter_changelogs_inclusion_filtering_by_id():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'fieldId': field_id_1,
                                'field': field_name_1,
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    include_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_1, jira_field_name=field_name_1)
    ]
    filtered_issue = _filter_changelogs([issue], include_fields, [])[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['fieldId'] == field_id_1
        
def test_filter_changelogs_inclusion_filtering_by_name():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'field': field_name_1,
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    include_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_1, jira_field_name=field_name_1)
    ]
    filtered_issue = _filter_changelogs([issue], include_fields, [])[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['field'] == field_name_1
        
def test_filter_changelogs_exclusion_filtering_by_id():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'field': field_name_1,
                                'fieldId': field_id_1
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    exclude_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_2, jira_field_name=field_name_2)
    ]
    filtered_issue = _filter_changelogs([issue], [], exclude_fields)[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['fieldId'] == field_id_1
        
def test_filter_changelogs_exclusion_filtering_by_name():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'field': field_name_1,
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    exclude_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_2, jira_field_name=field_name_2)
    ]
    filtered_issue = _filter_changelogs([issue], [], exclude_fields)[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['field'] == field_name_1

@pytest.mark.skip(reason="need to mock serverInfo endpoint too")
def test_expand_changelog():
    total_changelog_histories = 5
    batch_size = 1

    def _mock_api_endpoint_for_changelog(m: requests_mock.Mocker, change_log_num: int):
        mock_return = {
            "self": "https://test-co.atlassian.net/rest/api/2/issue/TS-4/changelog?maxResults=1&startAt=1",
            "nextPage": "https://test-co.atlassian.net/rest/api/2/issue/TS-4/changelog?maxResults=1&startAt=2",
            "maxResults": batch_size,
            "startAt": change_log_num - 1,
            "total": total_changelog_histories,
            "isLast": False,
            "values": [
                {
                    "id": f"{change_log_num}",
                    "author": {},
                    "created": "2020-06-29T16:01:51.141-0400",
                    "items": [
                        {
                            "field": "Spelunking CustomField v2",
                            "fieldtype": "custom",
                            "fieldId": "customfield_10057",
                            "from": None,
                            "fromString": None,
                            "to": "10072",
                            "toString": "hello",
                        }
                    ],
                }
            ],
        }
        _register_jira_uri(
            m,
            endpoint=f"issue/1/changelog?startAt={change_log_num - 1}&maxResults={batch_size}",
            return_value=json.dumps(mock_return),
        )

    with requests_mock.Mocker() as m:
        for change_log_num in range(0, total_changelog_histories + 1):
            _mock_api_endpoint_for_changelog(m, change_log_num)
        spoofed_issue_raw: dict = {
            "id": "1",
            "key": "spoof-1",
            "changelog": {
                "total": total_changelog_histories,
                "maxResults": 0,
                "histories": [],
            },
        }

        spoofed_issue_no_more_results_raw: dict = {
            "id": "2",
            "key": "spoof-2",
            "changelog": {"total": 0, "maxResults": 0, "histories": []},
        }

        _expand_changelog(
            get_jira_mock_connection(),
            jira_issues=[spoofed_issue_raw, spoofed_issue_no_more_results_raw],
            batch_size=1,
        )

        assert len(spoofed_issue_raw["changelog"]["histories"]) == total_changelog_histories
        assert len(spoofed_issue_no_more_results_raw["changelog"]["histories"]) == 0


@contextmanager
def _mock_for_full_issue_test(
    jf_issue_metadata: list[IssueMetadata],
    project_key: str = "PROJ",
    pull_from: datetime = datetime.min,
    issues_updated_value: datetime = datetime(2020, 1, 1),
    batch_size: int = Constants.MAX_ISSUE_API_BATCH_SIZE,
):
    expand_fields = ["*all"]

    with requests_mock.Mocker() as mocker:
        # Register the 'Batch Size' query return
        _register_jira_uri(
            mocker,
            endpoint=f"search?jql=&startAt=0&validateQuery=True&fields=%2Aall&maxResults={Constants.MAX_ISSUE_API_BATCH_SIZE}",
            return_value=f'{{"expand":"schema,names","startAt":0,"maxResults":{batch_size},"total":{len(jf_issue_metadata)},"issues":[]}}',
        )

        # Register the 'pull from' dates
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts={project_key: len(jf_issue_metadata)},
            pull_from=pull_from,
            issues_updated_value=issues_updated_value,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )

        _mock_jira_issue_by_ids(
            m=mocker,
            issue_ids=[
                issue_metadata.id
                for issue_metadata in jf_issue_metadata
                if issues_updated_value > issue_metadata.updated
            ],
            batch_size=batch_size,
            issues_updated_value=issues_updated_value,
            expand_fields=expand_fields,
        )
        yield mocker


def test_download_issue_page_ensure_error_never_raised():
    """
    The _download_issue_page should NEVER raise an error.
    """
    with patch(
        "jf_ingest.jf_jira.downloaders.retry_for_status",
        side_effect=JIRAError(status_code=500),
    ):
        issues = _download_issue_page(
            jira_connection=get_jira_mock_connection(), jql_query='', start_at=0, batch_size=100
        )
        assert len(issues) == 0

    with patch(
        "jf_ingest.jf_jira.downloaders.retry_for_status",
        side_effect=Exception('random exception'),
    ):
        issues = _download_issue_page(
            jira_connection=get_jira_mock_connection(), jql_query='', start_at=0, batch_size=100
        )
        assert len(issues) == 0

def test_download_issue_page_ensure_fields_not_ignored():
    """
    The _download_issue_page should NEVER raise an error.
    """
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":0,"total":0,"issues":[]}}'
            jira_mock_connection = get_jira_mock_connection(mocker)
            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield jira_mock_connection, mocker
    
    with _mocked_jira_return(requested_batch_size=0, returned_batch_size=0) as (jira_conn, mocker):
        _download_issue_page(
            jira_connection=jira_conn, jql_query='', start_at=0, batch_size=0, expand_fields=[], include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='ID')
            ]
        )
        print(vars(mocker.request_history[0]))
        post_found = False
        for request in mocker.request_history:
            request: Request = request._request
            if request.method == 'POST':
                post_found = True
                request_body = json.loads(request.body)
                assert request_body['fields'] == ['id']
        assert post_found
        
def test_download_issue_page_ensure_fields_not_ignored_more():
    """
    The _download_issue_page should NEVER raise an error.
    """
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":0,"total":0,"issues":[]}}'
            jira_mock_connection = get_jira_mock_connection(mocker)
            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield jira_mock_connection, mocker
    
    with _mocked_jira_return(requested_batch_size=0, returned_batch_size=0) as (jira_conn, mocker):
        _download_issue_page(
            jira_connection=jira_conn, jql_query='', start_at=0, batch_size=0, expand_fields=[], include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='ID'),
                JiraFieldIdentifier(jira_field_id='customfield_101234', jira_field_name='Sprint'),
                JiraFieldIdentifier(jira_field_id='customfield_201244', jira_field_name='Thing'),
            ]
        )
        print(vars(mocker.request_history[0]))
        post_found = False
        for request in mocker.request_history:
            request: Request = request._request
            if request.method == 'POST':
                post_found = True
                request_body = json.loads(request.body)
                assert request_body['fields'] == ['id', 'customfield_101234', 'customfield_201244']
        assert post_found

def test_generate_project_pull_from_bulk_jql_base():
    project_keys = ['A', 'B', 'C', 'D', 'E', 'F']
    project_key_to_pull_from = {
        'A': datetime(2024, 10, 1),
        'B': datetime(2024, 10, 2),
        'C': datetime(2024, 10, 3),
        'D': datetime(2024, 10, 4),
        'E': datetime(2024, 10, 5),
        'F': datetime(2024, 10, 6),
    }
    jql_filters = [
        generate_project_pull_from_bulk_jql(project_keys=project_key_batch, project_key_to_pull_from=project_key_to_pull_from)
        for project_key_batch in batch_iterable(project_keys, batch_size=3)
    ]
    
    assert len(jql_filters) == 2
    assert jql_filters[0] == '(project = A AND updated > "2024-10-01") OR (project = B AND updated > "2024-10-02") OR (project = C AND updated > "2024-10-03") order by id asc'
    assert jql_filters[1] == '(project = D AND updated > "2024-10-04") OR (project = E AND updated > "2024-10-05") OR (project = F AND updated > "2024-10-06") order by id asc'

def test_generate_project_pull_from_bulk_jql_with_issue_filter():
    project_keys = ['A', 'B', 'C', 'D', 'E', 'F']
    project_key_to_pull_from = {
        'A': datetime(2024, 10, 1),
        'B': datetime(2024, 10, 2),
        'C': datetime(2024, 10, 3),
        'D': datetime(2024, 10, 4),
        'E': datetime(2024, 10, 5),
        'F': datetime(2024, 10, 6),
    }
    jql_filter = generate_project_pull_from_bulk_jql(project_keys=project_keys, project_key_to_pull_from=project_key_to_pull_from, jql_filter='issuetype != "Secret Type"')
    assert jql_filter == (
        '(project = A AND updated > "2024-10-01") OR (project = B AND updated > "2024-10-02") OR (project = C AND updated > "2024-10-03") OR (project = D AND updated > "2024-10-04") OR (project = E AND updated > "2024-10-05") OR (project = F AND updated > "2024-10-06") AND (issuetype != "Secret Type") order by id asc'
    )
    
