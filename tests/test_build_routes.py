import pytest
from starlette.responses import Response as StarletteResponse
from starlette.responses import StreamingResponse as StarletteStreamingResponse

from simpleindex.__main__ import _to_http_response
from simpleindex.routes import Response, StreamingResponse


def test_response_conversion():
    content = "{ value: 42 }"
    status_code = 401
    media_type = "application/json"
    header_key = "Header Key"
    header_value = "header value"
    headers = {header_key: header_value}

    response = Response(
        content=content, status_code=status_code, media_type=media_type, headers=headers
    )
    starlette_response = _to_http_response(response)

    assert isinstance(starlette_response, StarletteResponse)

    assert starlette_response.body.decode(starlette_response.charset) == content
    assert starlette_response.status_code == status_code
    assert starlette_response.media_type == media_type
    assert (
        header_key in starlette_response.headers
        and starlette_response.headers[header_key] == header_value
    )


@pytest.mark.asyncio
async def test_streaming_response_conversion():
    content_text = "{ value: 42 }"

    async def content():
        for c in content_text:
            yield c

    status_code = 401
    media_type = "application/json"
    header_key = "Header Key"
    header_value = "header value"
    headers = {header_key: header_value}

    response = StreamingResponse(
        content=content(),
        status_code=status_code,
        media_type=media_type,
        headers=headers,
    )
    starlette_response = _to_http_response(response)

    assert isinstance(starlette_response, StarletteStreamingResponse)

    assert "".join([v async for v in starlette_response.body_iterator]) == content_text
    assert starlette_response.status_code == status_code
    assert starlette_response.media_type == media_type
    assert (
        header_key in starlette_response.headers
        and starlette_response.headers[header_key] == header_value
    )
