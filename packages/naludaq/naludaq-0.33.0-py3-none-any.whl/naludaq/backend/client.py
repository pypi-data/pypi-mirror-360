import http

import requests

from .exceptions import BackendError, HttpError


class HttpClient:
    def __init__(self, addr: tuple[str, int]) -> None:
        """Simple wrapper for sending HTTP requests to the backend.

        Args:
            addr (tuple[str, int]): address of the client.
        """
        host, port = addr
        self._address = addr
        self._prefix = f"http://{host}:{port}"
        self._session = requests.Session()
        self._timeout_sec = 2

    @property
    def address(self) -> tuple[str, int]:
        """Get the server address as (ip, port)"""
        return self._address

    @property
    def host(self) -> str:
        """Get the host IP of the server"""
        return self._address[0]

    @property
    def port(self) -> int:
        """Get the port number of the server"""
        return self._address[1]

    @property
    def url(self) -> str:
        """Get the URL used to reach the server"""
        return f"http://{self.host}:{self.port}/"

    def reachable(self) -> bool:
        """Checks if the server can be reached."""
        try:
            self.get("/connection/info")
            return True
        except BackendError:
            return False

    def put(self, route: str, *, params=None, json=None) -> requests.Response:
        """Send a PUT request to the server."""
        return self._request("put", route, params=params, json=json)

    def put_binary(self, route: str, *, data: bytes, params=None) -> requests.Response:
        """Send a PUT request with binary content to the server."""
        return self._request(
            "put",
            route,
            params=params,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
        )

    def post(self, route: str, *, params=None, json=None) -> requests.Response:
        """Send a POST request to the server."""
        return self._request("post", route, params=params, json=json)

    def post_binary(self, route: str, *, data: bytes, params=None) -> requests.Response:
        """Send a POST request with binary content to the server."""
        return self._request(
            "post",
            route,
            params=params,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
        )

    def delete(self, route: str, *, params=None, json=None) -> requests.Response:
        """Send a DELETE request to the server."""
        return self._request("delete", route, params=params, json=json)

    def get(self, route: str, *, params=None, json=None) -> requests.Response:
        """Send a GET request to the server."""
        return self._request("get", route, params=params, json=json)

    def get_json(self, route: str, *, params=None, json=None) -> dict:
        """Send a GET request to the server and parse the response from JSON."""
        return self.get(route, params=params, json=json).json()

    def get_binary(self, route: str, *, params=None, json=None) -> bytes:
        """Send a GET request to the server and return the raw binary response content"""
        return self.get(route, params=params, json=json).content

    def _request(
        self,
        method: str,
        route: str,
        **kwargs,
    ) -> requests.Response:
        """Sends a generic request to the backend.

        Args:
            method (str): HTTP method as a string (e.g. "post")
            route (str): route for the request
            **kwargs: any arguments accepted by `requests.request`

        Raises:
            HttpError: a generic HTTP error if the status code is not OK.

        Returns:
            requests.Response: the response from the backend.
        """
        extra_args = {"timeout": self._timeout_sec}
        kwargs |= extra_args
        url = self._format_route(route)
        response = self._session.request(method, url=url, **kwargs)
        status = http.HTTPStatus(response.status_code)
        if status == http.HTTPStatus.OK:
            return response
        try:
            error = HttpError(status, response.json())
        except Exception as e:
            raise BackendError("The server sent a malformed response") from e
        error.raise_typed()

    def _format_route(self, route: str) -> str:
        """Get the full URL for a route."""
        if route.startswith("/"):
            route = route[1:]
        return self.url + route
