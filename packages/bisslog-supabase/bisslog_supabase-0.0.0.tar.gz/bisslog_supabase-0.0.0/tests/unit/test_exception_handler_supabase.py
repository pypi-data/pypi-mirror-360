import pytest
from httpx import HTTPStatusError, TimeoutException, RequestError, Response, Request
from bisslog_supabase.exception_handler import bisslog_exc_mapper_supabase

from bisslog.exceptions.external_interactions_errors import (
    InvalidDataExtException, IntegrityErrorExtException, ProgrammingErrorExtException,
    ConfigurationExtException, TimeoutExtException, ConnectionExtException,
    OperationalErrorExtException, ExternalInteractionError
)


def make_http_status_error(status_code: int):
    req = Request("GET", "https://example.supabase.co/test")
    res = Response(status_code=status_code, request=req)
    return HTTPStatusError("Error", request=req, response=res)


@pytest.mark.parametrize("status_code,expected_exception", [
    (400, InvalidDataExtException),
    (401, ConfigurationExtException),
    (403, ProgrammingErrorExtException),
    (404, ProgrammingErrorExtException),
    (409, IntegrityErrorExtException),
    (500, OperationalErrorExtException),
    (502, OperationalErrorExtException),
    (418, ExternalInteractionError),  # Unknown code
])
def test_http_status_error_mapping(status_code, expected_exception):
    @bisslog_exc_mapper_supabase
    def failing_function():
        raise make_http_status_error(status_code)

    with pytest.raises(expected_exception):
        failing_function()


def test_timeout_exception_mapping():
    @bisslog_exc_mapper_supabase
    def failing_function():
        raise TimeoutException("Timeout")

    with pytest.raises(TimeoutExtException):
        failing_function()


def test_request_error_mapping():
    @bisslog_exc_mapper_supabase
    def failing_function():
        raise RequestError("Connection error")

    with pytest.raises(ConnectionExtException):
        failing_function()


def test_generic_exception_mapping():
    @bisslog_exc_mapper_supabase
    def failing_function():
        raise ValueError("Unexpected error")

    with pytest.raises(ExternalInteractionError):
        failing_function()


def test_successful_execution():
    @bisslog_exc_mapper_supabase
    def successful_function():
        return "ok"

    assert successful_function() == "ok"
