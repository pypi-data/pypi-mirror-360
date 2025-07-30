import pytest
from unittest.mock import MagicMock

from bisslog_supabase.basic_helper import BasicSupabaseHelper


@pytest.fixture
def mock_supabase_client():
    return MagicMock()


@pytest.fixture
def helper(mock_supabase_client):
    return BasicSupabaseHelper(client=mock_supabase_client)


def test_insert_one_returns_data(helper, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'id': 1, 'name': 'test'}]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    result = helper.insert_one('test_table', {'name': 'test'})

    assert result == {'id': 1, 'name': 'test'}
    mock_supabase_client.table.assert_called_with('test_table')


def test_insert_one_returns_none(helper, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    result = helper.insert_one('test_table', {'name': 'test'})

    assert result is None


def test_find_one_returns_result(helper, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'id': 5, 'email': 'test@example.com'}]

    query_mock = MagicMock()
    query_mock.eq.return_value = query_mock
    query_mock.limit.return_value.execute.return_value = mock_response

    mock_supabase_client.table.return_value = query_mock

    result = helper.find_one('users', {'email': 'test@example.com'})

    assert result == {'id': 5, 'email': 'test@example.com'}
    query_mock.eq.assert_called_with('email', 'test@example.com')


def test_find_one_returns_none(helper, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = []

    query_mock = MagicMock()
    query_mock.eq.return_value = query_mock
    query_mock.limit.return_value.execute.return_value = mock_response

    mock_supabase_client.table.return_value = query_mock

    result = helper.find_one('users', {'email': 'notfound@example.com'})

    assert result is None


def test_get_length_with_filters(helper, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.count = 42

    query_mock = MagicMock()
    query_mock.eq.return_value = query_mock
    query_mock.select.return_value = query_mock
    query_mock.execute.return_value = mock_response

    mock_supabase_client.table.return_value = query_mock

    result = helper.get_length('orders', {'status': 'paid'})

    assert result == 42
    query_mock.eq.assert_called_with('status', 'paid')


def test_get_length_without_filters(helper, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.count = 7

    query_mock = MagicMock()
    query_mock.select.return_value = query_mock
    query_mock.execute.return_value = mock_response

    mock_supabase_client.table.return_value = query_mock

    result = helper.get_length('orders')

    assert result == 7
