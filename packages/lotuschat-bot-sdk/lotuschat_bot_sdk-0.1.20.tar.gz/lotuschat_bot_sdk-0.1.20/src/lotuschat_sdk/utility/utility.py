import asyncio
import time

from aiohttp import FormData


def response_success(code: int):
    return {
        "code": code,
        "message": "",
        "time": time.time()
    }


def response_error(code: int, message: str):
    return {
        "code": code,
        "message": message,
        "time": time.time()
    }


def error_message(method: str, message: str):
    return {
        "method": method,
        "message": message,
        "time": time.time()
    }


def is_not_empty(s: str) -> bool:
    return bool(s and s.strip())


def extract_last_url(url: str) -> str:
    if url:
        return url.rstrip("/").split("/")[-1]
    return url


def run_async(coro):
    asyncio.run(coro)


def print_form_data(form: FormData) -> str:
    fields = getattr(form, "_fields", None)
    if fields is None:
        return f"{form}"
    else:
        return ", ".join(f"{f[0]["name"]}={f[2]!r}" for f in fields)
