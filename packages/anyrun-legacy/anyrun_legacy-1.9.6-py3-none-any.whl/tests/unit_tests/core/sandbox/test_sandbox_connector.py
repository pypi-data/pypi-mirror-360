import pytest

from anyrun.connectors import SandboxConnector
from anyrun.utils.exceptions import RunTimeException
from tests.conftest import MockAiohttpClientResponse


@pytest.mark.asyncio
async def test_generate_multipart_request_body_correctly_saves_file_payload():
    connector = SandboxConnector.windows('mock_api_key')

    # Use filepath
    multipart_body = await connector._generate_multipart_request_body(
        filepath='tests/suspicious_file.txt'
    )

    body_iterator = iter(multipart_body)

    payload = next(body_iterator)[0]
    assert payload.headers.get('Content-Disposition').split('"')[3] == 'suspicious_file.txt'
    assert payload._value.decode() == 'malware'

    # Use file_content and filename
    multipart_body = await connector._generate_multipart_request_body(
        filename='suspicious_file.txt',
        file_content=b'malware'
    )

    body_iterator = iter(multipart_body)

    payload = next(body_iterator)[0]
    assert payload.headers.get('Content-Disposition').split('"')[3] == 'suspicious_file.txt'
    assert payload._value.decode() == 'malware'


@pytest.mark.asyncio
async def test_generate_multipart_request_body_deletes_none_and_false_parameters():
    connector = SandboxConnector.windows('mock_api_key')

    multipart_body = await connector._generate_multipart_request_body(
        filepath='tests/suspicious_file.txt',
        obj_ext_cmd=None,
        obj_ext_extension=False
    )

    body_iterator = iter(multipart_body)
    # Skip file payload
    next(body_iterator)

    parsed_body_payload = ','.join(
        [
            '{}:{}'.format(payload[0].headers.get('Content-Disposition').split('=')[1], payload[0]._value.decode())
            for payload in body_iterator
        ]
    )

    # Check if obj_ext_cmd parameter is not in payload
    assert parsed_body_payload == '"obj_type":file'

@pytest.mark.asyncio
async def test_generate_request_body_deletes_none_and_false_parameters():
    connector = SandboxConnector.windows('mock_api_key')

    body = await connector._generate_request_body(
        'url',
        obj_ext_cmd=None,
        obj_ext_extension=False
    )

    assert 'obj_ext_cmd' not in body
    assert 'obj_ext_extension' not in body


@pytest.mark.asyncio
async def test_prepare_response_returns_a_valid_simplified_dict_if_simplify_is_specified():
    connector = SandboxConnector.windows('mock_api_key')

    response = await connector._prepare_response(
        b'data: {"task": {"status": 50, "remaining": "30.123123"}, "some_other_data": "hello!"}',
        True,
        'task_uuid'
    )

    assert response == {
        "status": "RUNNING",
        "seconds_remaining": "30.123123",
        "info": "For interactive analysis follow: https://app.any.run/tasks/task_uuid"
    }

@pytest.mark.asyncio
async def test_prepare_response_returns_an_entire_dict_if_simplify_is_not_specified():
    connector = SandboxConnector.windows('mock_api_key')


    response = await connector._prepare_response(
        b'data: {"task": {"status": 50, "remaining": "30.123123"}, "some_other_data": "hello!"}',
        False,
        'task_uuid'
    )

    assert response == {"task": {"status": 50, "remaining": "30.123123"}, "some_other_data": "hello!"}


@pytest.mark.asyncio
async def test_check_response_content_type_raises_exception_if_event_stream_content_is_not_received():
    connector = SandboxConnector.windows('mock_api_key')

    with pytest.raises(RunTimeException) as exception:
        await connector._check_response_content_type('application/json', MockAiohttpClientResponse('application/json'))

    assert exception.value.json == {'description': 'Error message', 'code': 401}


@pytest.mark.asyncio
async def test_check_response_content_type_returns_none_if_event_stream_content_is_received():
    connector = SandboxConnector.windows('mock_api_key')

    assert await connector._check_response_content_type('text/event-stream', MockAiohttpClientResponse('text/event-stream')) is None

@pytest.mark.asyncio
async def test_check_resolve_task_status_returns_correct_statuses():
    connector = SandboxConnector.windows('mock_api_key')

    assert await connector._resolve_task_status(-1) == 'FAILED'
    assert await connector._resolve_task_status(50) == 'RUNNING'
    assert await connector._resolve_task_status(100) == 'COMPLETED'
    assert await connector._resolve_task_status(21) == 'PREPARING'

@pytest.mark.asyncio
async def test_check_get_file_payload_returns_valid_payload_if_file_bytes_is_received():
    connector = SandboxConnector.windows('mock_api_key')

    payload, _ = await connector._get_file_payload(file_content=b'some text', filename='suspicious_file.txt')

    assert payload._value.decode() == 'some text'

@pytest.mark.asyncio
async def test_check_get_file_payload_returns_valid_payload_if_file_path_is_received():
    connector = SandboxConnector.windows('mock_api_key')

    payload, _ = await connector._get_file_payload(filepath='tests/suspicious_file.txt')

    assert payload._value.decode() == 'malware'

@pytest.mark.asyncio
async def test_check_get_file_payload_raises_exception_if_not_a_valid_file_path_is_received():
    connector = SandboxConnector.windows('mock_api_key')

    with pytest.raises(RunTimeException) as exception:
        await connector._get_file_payload(filepath='123')

    assert exception.value.description == 'Received not valid filepath: 123'

@pytest.mark.asyncio
async def test_set_task_object_type_returns_params_with_obj_type_rerun_if_rerun_task_id_is_specified():
    connector = SandboxConnector.windows('mock_api_key')

    params = await connector._set_task_object_type(
        {'task_rerun_uuid': 'some task uuid'},
        'url'
    )

    assert params.get('obj_type') == 'rerun'
    assert params.get('task_rerun_uuid') == 'some task uuid'

@pytest.mark.asyncio
async def test_set_task_object_type_returns_params_with_specified_obj_type_if_rerun_task_id_is_not_specified():
    connector = SandboxConnector.windows('mock_api_key')

    params = await connector._set_task_object_type(
        {'obj_url': 'https://any.run'},
        'url'
    )

    assert params.get('obj_type') == 'url'
    assert params.get('obj_url') == 'https://any.run'
