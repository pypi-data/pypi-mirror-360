from typing import Any, Type, Dict
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response


__all__ = (
    "return_response",
    "return_json_response",
)


def return_response(
    data: Any,
    status_code: int,
    response_class: Type[Response],
    return_json_directly: bool = False,
    headers: Dict[int, Dict] = None,
    no_cache: bool = True,
) -> Response:
    if headers is None:
        headers = {}

    final_headers = headers.get(status_code) or {}

    if no_cache:
        final_headers.update(
            {
                "Cache-Control": "private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )

    if response_class != JSONResponse:
        return_json_directly = True

    if return_json_directly:
        content = data
    else:
        if status_code < 300:
            content = {"success": True, "data": jsonable_encoder(data)}
        else:
            content = {"success": False, "message": data}

    return response_class(
        status_code=status_code, content=content, headers=final_headers
    )


def return_json_response(
    data: Any,
    status_code: int,
    return_json_directly: bool = False,
    headers: Dict[int, Dict] = None,
    no_cache: bool = True,
) -> JSONResponse:
    return return_response(
        data=data,
        status_code=status_code,
        return_json_directly=return_json_directly,
        headers=headers,
        no_cache=no_cache,
        response_class=JSONResponse,
    )
