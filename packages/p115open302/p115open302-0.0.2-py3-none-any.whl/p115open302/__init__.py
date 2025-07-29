#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__version__ = (0, 0, 2)
__license__ = "GPLv3 <https://www.gnu.org/licenses/gpl-3.0.txt>"

import logging

from collections.abc import Buffer, Mapping
from errno import ENOENT, ENOTDIR
from hashlib import sha1 as calc_sha1
from http import HTTPStatus
from re import compile as re_compile
from string import digits, hexdigits
from time import time
from typing import Final
from urllib.parse import parse_qsl, quote, unquote, urlsplit, urlunsplit

from blacksheep import json, text, Application, Request, Response, Router
from blacksheep.contents import Content
from blacksheep.server.remotes.forwarding import ForwardedHeadersMiddleware
from cachedict import LRUDict, TLRUDict, TTLDict
from orjson import dumps, OPT_INDENT_2, OPT_SORT_KEYS
from p115client import check_response, P115Client, P115URL
from rich.box import ROUNDED
from rich.console import Console
from rich.highlighter import JSONHighlighter
from rich.panel import Panel
from rich.text import Text
from uvicorn.config import LOGGING_CONFIG


CRE_name_search: Final = re_compile("[^&=]+(?=&|$)").match

LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[\x1b[1m%(asctime)s\x1b[0m] %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = '[\x1b[1m%(asctime)s\x1b[0m] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'


class ColoredLevelNameFormatter(logging.Formatter):

    def format(self, record):
        match record.levelno:
            case logging.DEBUG:
                # blue
                record.levelname = f"\x1b[34m{record.levelname}\x1b[0m:".ljust(18)
            case logging.INFO:
                # green
                record.levelname = f"\x1b[32m{record.levelname}\x1b[0m:".ljust(18)
            case logging.WARNING:
                # yellow
                record.levelname = f"\x1b[33m{record.levelname}\x1b[0m:".ljust(18)
            case logging.ERROR:
                # red
                record.levelname = f"\x1b[31m{record.levelname}\x1b[0m:".ljust(18)
            case logging.CRITICAL:
                # magenta
                record.levelname = f"\x1b[35m{record.levelname}\x1b[0m:".ljust(18)
            case _:
                # dark grey
                record.levelname = f"\x1b[2m{record.levelname}\x1b[0m: ".ljust(18)
        return super().format(record)


def default(obj, /):
    if isinstance(obj, Buffer):
        return str(obj, "utf-8")
    raise TypeError


def highlight_json(val, /, default=default, highlighter=JSONHighlighter()) -> Text:
    if isinstance(val, Buffer):
        val = str(val, "utf-8")
    if not isinstance(val, str):
        val = dumps(val, default=default, option=OPT_INDENT_2 | OPT_SORT_KEYS).decode("utf-8")
    return highlighter(val)


def get_first(m: Mapping, *keys, default=None):
    for k in keys:
        if k in m:
            return m[k]
    return default


def make_application(
    client: P115Client, 
    debug: bool = False, 
    token: str = "", 
    cache_url: bool = False, 
    cache_size: int = 65536, 
) -> Application:
    ID_TO_PICKCODE: LRUDict[int, str] = LRUDict(cache_size)
    SHA1_TO_PICKCODE: LRUDict[str | tuple[str, int], str] = LRUDict(cache_size)
    NAME_TO_PICKCODE: LRUDict[str | tuple[str, int], str] = LRUDict(cache_size)
    PATH_TO_PICKCODE: TTLDict[str, str] = TTLDict(cache_size, ttl=3600)
    if cache_url:
        DOWNLOAD_URL_CACHE: TLRUDict[tuple[str, str], P115URL] = TLRUDict(cache_size)
    DOWNLOAD_URL_CACHE1: TLRUDict[str, P115URL] = TLRUDict(cache_size)
    DOWNLOAD_URL_CACHE2: TLRUDict[tuple[str, str], P115URL] = TLRUDict(1024)

    app = Application(router=Router(), show_error_details=debug)
    logger = getattr(app, "logger")
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredLevelNameFormatter("[\x1b[1m%(asctime)s\x1b[0m] %(levelname)s %(message)s"))
    logger.addHandler(handler)

    async def redirect_exception_response(
        self, 
        request: Request, 
        exc: Exception, 
    ):
        if isinstance(exc, ValueError):
            return text(str(exc), 400)
        elif isinstance(exc, FileNotFoundError):
            return text(str(exc), 404)
        elif isinstance(exc, OSError):
            return text(str(exc), 503)
        else:
            return text(str(exc), 500)

    if debug:
        logger.level = logging.DEBUG

    @app.on_middlewares_configuration
    def configure_forwarded_headers(app: Application):
        app.middlewares.insert(0, ForwardedHeadersMiddleware(accept_only_proxied_requests=False))

    @app.middlewares.append
    async def access_log(request: Request, handler) -> Response:
        start_t = time()
        def get_message(response: Response, /) -> str:
            remote_attr = request.scope["client"]
            status = response.status
            if status < 300:
                status_color = 32
            elif status < 400:
                status_color = 33
            else:
                status_color = 31
            message = f'\x1b[5;35m{remote_attr[0]}:{remote_attr[1]}\x1b[0m - "\x1b[1;36m{request.method}\x1b[0m \x1b[1;4;34m{request.url}\x1b[0m \x1b[1mHTTP/{request.scope["http_version"]}\x1b[0m" - \x1b[{status_color}m{status} {HTTPStatus(status).phrase}\x1b[0m - \x1b[32m{(time() - start_t) * 1000:.3f}\x1b[0m \x1b[3mms\x1b[0m'
            if debug:
                console = Console()
                with console.capture() as capture:
                    urlp = urlsplit(str(request.url))
                    url = urlunsplit(urlp._replace(path=unquote(urlp.path), scheme=request.scheme, netloc=request.host))
                    console.print(
                        Panel.fit(
                            f"[b cyan]{request.method}[/] [u blue]{url}[/] [b]HTTP/[red]{request.scope["http_version"]}",
                            box=ROUNDED,
                            title="[b red]URL", 
                            border_style="cyan", 
                        ), 
                    )
                    headers = {str(k, 'latin-1'): str(v, 'latin-1') for k, v in request.headers}
                    console.print(
                        Panel.fit(
                            highlight_json(headers), 
                            box=ROUNDED, 
                            title="[b red]HEADERS", 
                            border_style="cyan", 
                        )
                    )
                    scope = {k: v for k, v in request.scope.items() if k != "headers"}
                    console.print(
                        Panel.fit(
                            highlight_json(scope), 
                            box=ROUNDED, 
                            title="[b red]SCOPE", 
                            border_style="cyan", 
                        )
                    )
                message += "\n" + capture.get()
            return message
        try:
            response = await handler(request)
            logger.info(get_message(response))
        except Exception as e:
            response = await redirect_exception_response(app, request, e)
            logger.error(get_message(response))
            if debug:
                raise
        return response

    async def get_pickcode_to_id(id: int) -> str:
        if pickcode := ID_TO_PICKCODE.get(id, ""):
            return pickcode
        resp = await client.fs_info_open(id, timeout=5, async_=True)
        check_response(resp)
        data = resp["data"]
        if not data:
            raise FileNotFoundError(ENOENT, id)
        elif not data["sha1"]:
            raise NotADirectoryError(ENOTDIR, id)
        pickcode = ID_TO_PICKCODE[id] = data["pick_code"]
        return pickcode

    async def get_pickcode_for_sha1(
        sha1: str, 
        size: int = -1, 
    ) -> str:
        if size < 0:
            if pickcode := SHA1_TO_PICKCODE.get(sha1, ""):
                return pickcode
        elif pickcode := SHA1_TO_PICKCODE.get((sha1, size), ""):
            return pickcode
        resp = await client.fs_search_open(
            {"search_value": sha1, "fc": 2, "limit": 16}, 
            async_=True, 
        )
        check_response(resp)
        for info in resp["data"]:
            if info["sha1"] == sha1:
                if size >= 0 and int(info["file_size"]) != size:
                    continue
                if size < 0:
                    pickcode = SHA1_TO_PICKCODE[sha1] = info["pick_code"]
                else:
                    pickcode = SHA1_TO_PICKCODE[(sha1, size)] = info["pick_code"]
                return pickcode
        raise FileNotFoundError(ENOENT, pickcode)

    async def get_pickcode_for_name(
        name: str, 
        size: int = -1, 
        refresh: bool = False, 
    ) -> str:
        if not refresh:
            if size < 0:
                if pickcode := NAME_TO_PICKCODE.get(name, ""):
                    return pickcode
            elif pickcode := NAME_TO_PICKCODE.get((name, size), ""):
                return pickcode
        payload = {"search_value": name, "fc": 2, "limit": 16}
        suffix = name.rpartition(".")[-1]
        if len(suffix) < 5 and suffix.isalnum() and suffix[0].isalpha():
            payload["suffix"] = suffix
        resp = await client.fs_search_open(payload, async_=True)
        check_response(resp)
        for info in resp["data"]:
            if info["name"] == name:
                if size >= 0 and int(info["file_size"]) != size:
                    continue
                if size < 0:
                    pickcode = NAME_TO_PICKCODE[name] = info["pick_code"]
                else:
                    pickcode = NAME_TO_PICKCODE[(name, size)] = info["pick_code"]
                return pickcode
        raise FileNotFoundError(ENOENT, name)

    async def get_pickcode_for_path(
        path: str, 
        refresh: bool = False, 
    ) -> str:
        path = "/" + path.replace(">", "/").strip("/")
        if not refresh:
            if pickcode := PATH_TO_PICKCODE.get(path, ""):
                return pickcode
        resp = await client.fs_info_open(path, timeout=5, async_=True)
        check_response(resp)
        data = resp["data"]
        if not data:
            raise FileNotFoundError(ENOENT, path)
        elif not data["sha1"]:
            raise NotADirectoryError(ENOTDIR, path)
        pickcode = PATH_TO_PICKCODE[path] = data["pick_code"]
        return pickcode

    async def get_downurl(
        pickcode: str, 
        user_agent: str = "", 
    ) -> P115URL:
        if (cache_url and (r := DOWNLOAD_URL_CACHE.get((pickcode, user_agent)))
            or (r := DOWNLOAD_URL_CACHE1.get(pickcode))
            or (r := DOWNLOAD_URL_CACHE2.get((pickcode, user_agent)))
        ):
            return r[1]
        url = await client.download_url_open(
            pickcode, 
            headers={"User-Agent": user_agent}, 
            async_=True, 
        )
        expire_ts = int(next(v for k, v in parse_qsl(urlsplit(url).query) if k == "t")) - 60 * 5
        if "&c=0&f=&" in url:
            DOWNLOAD_URL_CACHE1[pickcode] = (expire_ts, url)
        elif "&c=0&f=1&" in url:
            DOWNLOAD_URL_CACHE2[(pickcode, user_agent)] = (expire_ts, url)
        elif cache_url:
            DOWNLOAD_URL_CACHE[(pickcode, user_agent)] = (expire_ts, url)
        return url

    @app.router.route("/", methods=["GET", "HEAD", "POST"])
    @app.router.route("/<path:name2>", methods=["GET", "HEAD", "POST"])
    async def index(
        request: Request, 
        pickcode: str = "", 
        id: int = 0, 
        sha1: str = "", 
        path: str = "", 
        name: str = "", 
        name2: str = "", 
        size: int = -1, 
        refresh: bool = False, 
        sign: str = "", 
        t: int = 0, 
    ):
        def check_sign(value, /):
            if not token:
                return None
            if sign != calc_sha1(bytes(f"302@115-{token}-{t}-{value}", "utf-8")).hexdigest():
                return json({"state": False, "message": "invalid sign"}, 403)
            elif t > 0 and t <= time():
                return json({"state": False, "message": "url was expired"}, 401)
        if pickcode:
            if resp := check_sign(pickcode):
                return resp
            if not (len(pickcode) == 17 and pickcode.isalnum()):
                raise ValueError(f"bad pickcode: {pickcode!r}")
        elif id:
            if resp := check_sign(id):
                return resp
            pickcode = await get_pickcode_to_id(id)
        elif sha1:
            if resp := check_sign(sha1):
                return resp
            if len(sha1) != 40 or sha1.strip(hexdigits):
                raise ValueError(f"bad sha1: {sha1!r}")
            pickcode = await get_pickcode_for_sha1(sha1.upper(), size)
        elif name:
            if resp := check_sign(name):
                return resp
            pickcode = await get_pickcode_for_name(name, size, refresh=refresh)
        elif path:
            if resp := check_sign(path):
                return resp
            pickcode = await get_pickcode_for_path(path, refresh=refresh)
        else:
            remains = ""
            if match := CRE_name_search(unquote(request.url.query or b"")):
                name = match[0]
            elif (idx := name2.find("/")) > 0:
                name, remains = name2[:idx], name2[idx:]
            if name:
                fullname = name + remains
                if resp := check_sign(fullname):
                    return resp
                if len(name) == 17 and name.isalnum():
                    pickcode = name.lower()
                elif not name.strip(digits):
                    pickcode = await get_pickcode_to_id(int(name))
                elif len(name) == 40 and not name.strip(hexdigits):
                    pickcode = await get_pickcode_for_sha1(name.upper(), size)
            else:
                fullname = name2
            if not pickcode:
                if ">" in fullname or "/" in fullname:
                    pickcode = await get_pickcode_for_path(fullname, refresh=refresh)
                else:
                    pickcode = await get_pickcode_for_name(fullname, size, refresh=refresh)
        if not pickcode:
            raise FileNotFoundError(ENOENT, f"not found: {str(request.url)!r}")
        user_agent = (request.get_first_header(b"User-agent") or b"").decode("latin-1")
        url = await get_downurl(pickcode.lower(), user_agent)
        return Response(302, [
            (b"Location", bytes(url, "utf-8")), 
            (b"Content-Disposition", b'attachment; filename="%s"' % bytes(quote(url["name"], safe=""), "latin-1")), 
        ], Content(b"application/json; charset=utf-8", dumps(url.__dict__)))

    return app


if __name__ == "__main__":
    from pathlib import Path
    from uvicorn import run

    client = P115Client(Path("115-cookies.txt"), ensure_cookies=True, check_for_relogin=True)
    client.login_another_open(replace=True)
    run(
        make_application(client, debug=True), 
        host="0.0.0.0", 
        port=8000, 
        proxy_headers=True, 
        server_header=False, 
        forwarded_allow_ips="*", 
        timeout_graceful_shutdown=1, 
        access_log=False, 
    )

