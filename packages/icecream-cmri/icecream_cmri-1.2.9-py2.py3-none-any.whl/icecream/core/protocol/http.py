"""
@author:cmcc
@file: http.py
@time: 2024/7/21 22:28
"""

import copy
import requests
import json
import datetime
import uuid
import six
import logging
from requests.models import Request
from icecream.utils.common import Utils
from icecream.core.exceptions import AttrException

try:
    import netaddr
except ImportError:
    netaddr = None
import traceback
import urllib3
urllib3.disable_warnings()


logger = logging.getLogger(__name__)


class _JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return six.text_type(o)
        if netaddr and isinstance(o, netaddr.IPAddress):
            return six.text_type(o)

        return super(_JSONEncoder, self).default(o)


class Session(object):

    def __init__(self, session=None):
        self.session = session or requests.sessions.Session()
        self._request = None
        self._response = None

    def __del__(self):
        """Clean up resources on delete."""
        if self.session:
            # If we created a requests.Session, try to close it out correctly
            try:
                self.session.close()
            except Exception:
                pass
            finally:
                self.session = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def head(self, url, **kwargs):
        """Perform a HEAD request.

        This calls :py:meth:`.request()` with ``method`` set to ``HEAD``.

        """
        return self.request(url, 'HEAD', **kwargs)

    def get(self, url, **kwargs):
        """Perform a GET request.

        This calls :py:meth:`.request()` with ``method`` set to ``GET``.

        """
        return self.request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request.

        This calls :py:meth:`.request()` with ``method`` set to ``POST``.

        """
        return self.request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request.

        This calls :py:meth:`.request()` with ``method`` set to ``PUT``.

        """
        return self.request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request.

        This calls :py:meth:`.request()` with ``method`` set to ``DELETE``.

        """
        return self.request(url, 'DELETE', **kwargs)

    def patch(self, url, **kwargs):
        """Perform a PATCH request.

        This calls :py:meth:`.request()` with ``method`` set to ``PATCH``.

        """
        return self.request(url, 'PATCH', **kwargs)

    def request(self, url, method,
            params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json_data=None):
        content_type = Utils.ignore_case_get(headers, "content-type")
        if content_type:
            if "application/json" in content_type:
                if data is not None:
                    json_data = copy.deepcopy(data)
                    data = None
        if headers:
            if Utils.ignore_case_get(headers, "user-agent") is None:
                headers.update({
                    "User-Agent": "icecream"
                })
        else:
            headers = {"User-Agent": "icecream"}
        # Create the Request.
        req = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json_data,
            params=params or {},
            auth=auth,
            cookies=cookies,
            hooks=hooks,
        )
        prep = self.session.prepare_request(req)

        proxies = proxies or {}

        settings = self.session.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )

        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(settings)
        self._request = {'req': req, 'prep': prep, 'send_kwargs': send_kwargs}
        return self

    def send(self, http_result=None):
        try:
            req = self._request['req']
            logger.debug(f'method: {req.method} url: {req.url} headers: {req.headers} params {req.params}'
                         f' data: { req.data or req.json}')
            if http_result:
                http_result.request.update(
                    {
                        "headers": dict(req.headers),
                        "cookie": req.cookies
                    }
                )
            res = self.session.send(self._request['prep'], **self._request['send_kwargs'])
            content_length = res.headers.get("Content-Length", 0)
            if content_length == 0:
                logger.debug(f"status_code: {res.status_code} content: {res.text}")
            else:
                logger.debug(f"status_code: {res.status_code}")
            resp = Response(res)
            if http_result:
                http_result.response = resp.to_json()
            self._response = res
            return resp
        except Exception:
            msg = traceback.format_exc(3)
            logger.error(msg)
            if http_result:
                http_result.response["text"] = str(msg)

    def _format_size(self, size):
        if size > 1024:
            return str(round(size/1024, 2)) + "KB"
        else:
            return str(size) + "B"


class Response(object):
    def __init__(self, response):
        self.raw_resp = response
        self.status_code = response.status_code
        self.resp_time = response.elapsed.total_seconds() * 1000
        self.headers = response.headers
        self.encoding = response.encoding
        self.history = response.history
        self.reason = response.reason
        self.cookies = response.cookies
        self.content = response.content
        self.text = response.text
        self.request = response.request
        self.json = response.json
        if hasattr(response, "next"):
            self.next = response.next
        else:
            self.next = None

    def _is_larger_attachment(self):
        """
        判断大附件，大内容
        :return:
        """
        size = int(self.headers.get("Content-Length", 0))
        content_type = self.headers.get("Content-Type", "")
        content_disposition = self.headers.get("Content-Disposition", None)
        if content_disposition and "attachment;" in content_disposition:
            if not content_disposition.endswith((".png", ".jpg", ".bmp")):
                return True
            if size > 200 * 1024:  #200KB
                return True
        if "application/octet-stream" in content_type:
            if size > 200 * 1024:  #200KB
                return True

    def __getattr__(self, attr):
        response_attr = object.__getattribute__(self.raw_resp, attr)
        if response_attr:
            return response_attr
        if response_attr != "next":
            raise AttrException(f"not attr: {response_attr}")

    def _format_size(self, size):
        if size > 1024 * 1024:
            return str(round(size/1024/1024, 2)) + "MB"
        if size > 1024:
            return str(round(size/1024, 2)) + "KB"
        return str(size) + "B"

    def _format_res_time(self, duration=None):
        if duration is None:
            return "0ms"
        if duration > 60 * 1000:
            return str(round(duration/1000/60, 2)) + "m"
        if duration > 1000:
            return str(round(duration/1000, 2)) + "s"
        return str(round(duration, 2)) + "ms"

    def to_json(self):
        size = int(self.headers.get("Content-Length", 0))
        content_type = self.headers.get("Content-Type", None)
        text = self.text
        if self._is_larger_attachment():
            text = "响应内容为大附件，需要人工下载(断言里写处理逻辑)"
        else:
            if content_type and "application/json" in content_type:
                try:
                    text = json.dumps(self.json(), ensure_ascii=False)
                except Exception as e:
                    logger.error(f"json transform failure {e}")
            else:
                text = self.text
                try:
                    text = self.content.decode("utf-8")
                except Exception as e:
                    logger.error(f"content decode failure {e}")
        return {
            "status_code": self.status_code,
            # "headers": {**self.headers, "cookies": self.cookies},
            "headers": dict(self.headers),
            "resp_time": {"total": self._format_res_time(self.resp_time)},
            "text": text,
            "size": {"body": self._format_size(len(self.raw_resp.content) if size == 0 else size)},
        }


class IceRequest(object):
    def __init__(self, ice=None):
        self.ice = ice
        self._header = {}

    def get(self, url, **kwargs):
        return self.send(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self.send(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self.send(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self.send(url, 'DELETE', **kwargs)

    def head(self, url, **kwargs):
        return self.send(url, 'HEAD', **kwargs)

    def patch(self, url, **kwargs):
        return self.send(url, 'PATCH', **kwargs)

    def set_headers(self, headers):
        self._header.update(headers)

    def send(self, url, method, params=None, data=None, headers=None, verify=False, **kwargs) -> Response:
        session = Session()
        http_result = kwargs.pop("http_result", None)
        response = session.request(url, method, params, data, headers, verify=verify, **kwargs).send(http_result)
        self.ice._response = response
        return response



