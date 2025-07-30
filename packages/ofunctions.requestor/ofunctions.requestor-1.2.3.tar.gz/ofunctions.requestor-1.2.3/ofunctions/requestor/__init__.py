#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions

__intname__ = "ofunctions.requestor"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2025 Orsiris de Jong"
__description__ = "Requests abstractor class for JSON oriented REST APIs"
__license__ = "BSD-3-Clause"
__version__ = "1.2.3"
__build__ = "2025070801"
__compat__ = "python3.6+"


from typing import List, Optional, Any, Union
from logging import getLogger
import json
import requests
import warnings


logger = getLogger(__intname__)


class Requestor:
    """
    A class that handles JSON APIs elegantly, with server fallback, ACLS and error control

    data_model: high level json api function
    requestor: standard requests
    get_raw: low level binary download
    """

    def __init__(
        self,
        servers: List[str],
        username: str = None,
        password: str = None,
        cert_verify: bool = True,
        use_json: bool = True,
    ):
        self.api_session = None
        self.username = username
        self.password = password
        self.cert_verify = cert_verify
        self._endpoint = None
        self._use_json = use_json

        self._app_name = "ofunctions-requestor-app"
        self._user_agent = "ofunctions-requestor-ua"

        self._ignore_errors = False

        self._action_list = ["create", "read", "update", "delete", "exists"]
        self._allowed_models = []
        self._acls = {}
        """
        ACLS would look like a dict giving each allowed action for each model, eg:
        {
            'users': 'create', 'read', 'update', 'delete', 'exists',
            'items': 'read', 'exists'
        }
        """
        self._action_requests_equiv = {
            "create": "post",
            "read": "get",
            "update": "put",
            "delete": "delete",
            "exists": "get",
        }

        # Headers need to be set to Accept: application/json or else Laravel will send HTML as return
        # Do not set Content-Type or else uploads will fail
        self._headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate, gzip",
            "User-Agent": self._user_agent,
            "Referer": self._app_name,
        }

        self._proxy_dict = {}

        self.servers = []
        # servers can be multiple servers for failover
        if isinstance(servers, list):
            self.servers = servers
        elif servers is not None:
            for server in servers.split(","):
                # Remove trailing & ending spaces
                # Make sure server ends with '/'
                self.servers.append(server.strip().rstrip("/") + "/")
        self.connected_server = None

    def write_logs(self, logstr: str, level: str = "info"):
        """
        Write logs to logger
        """
        if level == "info":
            logger.info(logstr)
        elif level == "debug":
            logger.debug(logstr)
        elif level == "error":
            if self.ignore_errors:
                logger.info(logstr)
            else:
                logger.error(logstr)
        elif level == "warning":
            if self.ignore_errors:
                logger.info(logstr)
            else:
                logger.warning(logstr)
        elif level == "critical":
            if self.ignore_errors:
                logger.info(logstr)
            else:
                logger.critical(logstr)
        else:
            logger.info(logstr)

    @property
    def app_name(self):
        return self._app_name

    @app_name.setter
    def app_name(self, value: str):
        if isinstance(value, str):
            self._app_name = value.strip()
            self.headers["Referer"] = self.app_name
        else:
            raise ValueError("Bogus app name")

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str):
        if isinstance(value, str):
            self._user_agent = value.strip()
            self.headers["User-Agent"] = self.user_agent
        else:
            raise ValueError("Bogus user agent")

    @property
    def ignore_errors(self):
        return self._ignore_errors

    @ignore_errors.setter
    def ignore_errors(self, value: bool):
        if isinstance(value, bool):
            self._ignore_errors = value
        else:
            raise ValueError("Bogus ignore_errors value")

    @property
    def headers(self):
        return self._headers

    @property
    def header(self):
        pass

    @header.setter
    def header(self, value: dict):
        if isinstance(value, dict):
            self._headers = {**self._headers, **value}
            if self.api_session:
                self.api_session.headers = self._headers
        else:
            raise ValueError("Bogus header given")

    @headers.setter
    def headers(self, value: dict):
        if isinstance(value, dict):
            self._headers = value
            if self.api_session:
                self.api_session.headers = self._headers
        else:
            raise ValueError("Bogus header given")

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str):
        if isinstance(value, str):
            self._endpoint = value.strip().lstrip("/")

    @property
    def allowed_models(self):
        return self._allowed_models

    @allowed_models.setter
    def allowed_models(self, value: List[str]):
        if isinstance(value, list):
            self._allowed_models = value
        else:
            raise ValueError("Bogus allowed models given")

    @property
    def acls(self):
        return self._acls

    @acls.setter
    def acls(self, value: dict):
        if isinstance(value, list):
            for key, val in value:
                if key not in self.allowed_models:
                    raise ValueError("ACL for non existent model given")
                if val not in self._action_list:
                    raise ValueError("Not a valid action")

            self._acls = value
        else:
            raise ValueError("Bogus acls given")

    @property
    def action_list(self) -> List[str]:
        return self._action_list

    @property
    def proxy(self) -> dict:
        return self._proxy_dict

    @proxy.setter
    def proxy(self, value: str):
        if isinstance(value, str) and (
            value.startswith("http://") or value.startswith("https://")
        ):
            if value.startswith("http"):
                self._proxy_dict = {"http": value.strip("http://")}
            elif value.startswith("https"):
                self._proxy_dict = {"https": value.strip("https://")}
        else:
            raise ValueError("Bogus proxy given")

    def _create_session(self, uri: str = "", authenticated: bool = False) -> bool:
        """Needed for api calls that don't require api authentication"""
        try:
            api_session = requests.Session()
            # Remove accept: application/json from headers since it will fail on non API calls
            headers = self.headers
            headers["Accept"] = ""
            if authenticated:
                api_session.auth = (self.username, self.password)

            if not self.cert_verify:
                warnings.filterwarnings("ignore", category=Warning)
            result = api_session.get(uri, verify=self.cert_verify, headers=headers)
            try:
                status_code = result.status_code
            except AttributeError:
                self.write_logs("Server did not return a status code", level="error")
                status_code = None

            try:
                text = result.text
            except AttributeError:
                self.write_logs("Server did not return any data", level="error")
                text = None
            if status_code == 200:
                self.api_session = api_session
                if authenticated:
                    # This has to be changed depending on the API
                    if text.lower().startswith("token"):
                        token = text.replace("Token", "").strip()
                        self.header = {"Authorization": f"Bearer {token}"}
                return True

            self.write_logs("Cannot establish a session to server.", level="error")
            self.write_logs(f"Server return code: {status_code}", level="warning")
            try:
                logger.debug(
                    "Error:\n{}".format(text.encode("utf-8", errors="backslashreplace"))
                )
            except:
                pass
        except requests.exceptions.SSLError:
            self.write_logs(
                "Cannot establish a session: SSL/TLS error. Are your server & client certificates valid ?",
                level="error",
            )
            logger.debug("Trace:", exc_info=True)
        except requests.exceptions.ConnectionError:
            self.write_logs(
                "Cannot establish a session. Looks like we cannot reach the server.",
                level="error",
            )
            logger.debug("Trace:", exc_info=True)
        except Exception as exc:  # pylint: disable=W0703,broad-except
            self.write_logs(
                f"Cannot establish a session, unknown reason: {exc}", level="error"
            )
            logger.debug("Trace:", exc_info=True)
        return False

    def create_session(self, endpoint: str = None, authenticated: bool = False) -> bool:
        """
        Tries every server in server list until one can be reached, and sets server_api
        :return:
        """
        auth_endpoint = None
        for server in self.servers:
            if endpoint:
                auth_endpoint = server.rstrip("/") + "/" + endpoint.strip().strip("/")
            elif self._endpoint:
                auth_endpoint = (
                    server.rstrip("/") + "/" + +self._endpoint.strip().strip("/")
                )
            else:
                auth_endpoint = server.rstrip("/")
            if (
                not self._create_session(auth_endpoint, authenticated)
                and len(self.servers) > 1
            ):
                logger.info("Contacting auth server failed. Trying fallback server.")
            else:
                self.connected_server = server
                return True
        return False

    def _base_requestor(
        self, endpoint: str = None, action: str = "read", data: Any = None
    ) -> requests.Request:
        """
        simple request function that does handle all exceptions and will return a requeusts.Request object or False
        """
        if not self.api_session:
            self.write_logs("Cannot operate without proper session.", level="error")
            return None

        if not self.connected_server:
            self.write_logs(
                "Currently not connected to any server. Do we have an open session ?",
                level="error",
            )
            return False

        if endpoint:
            url = self.connected_server.rstrip("/") + "/" + endpoint.strip().strip("/")
        elif self._endpoint:
            url = self.connected_server.rstrip("/") + "/" + self._endpoint
        else:
            url = self.connected_server.rstrip("/")

        try:
            if not self.cert_verify:
                warnings.filterwarnings("ignore", category=Warning)
            if action in ["update", "create"]:
                if self._use_json:
                    result = getattr(
                        self.api_session, self._action_requests_equiv[action]
                    )(
                        url,
                        headers=self.headers,
                        json=data,
                        proxies=self._proxy_dict,
                        verify=self.cert_verify,
                    )
                else:
                    result = getattr(
                        self.api_session, self._action_requests_equiv[action]
                    )(
                        url,
                        headers=self.headers,
                        data=data,
                        proxies=self._proxy_dict,
                        verify=self.cert_verify,
                    )
            else:
                result = getattr(self.api_session, self._action_requests_equiv[action])(
                    url,
                    headers=self.headers,
                    proxies=self._proxy_dict,
                    verify=self.cert_verify,
                )
            status_code = result.status_code
            if status_code in [200, 201, 202]:
                if status_code == 200:
                    logger.debug(f"Successful operation {action}:{endpoint}")
                elif status_code == 201:
                    logger.debug(f"Created operation {action}:{endpoint}")
                elif status_code == 202:
                    logger.debug(f"Accepted operation {action}:{endpoint}")
                if action == "exists":
                    return True
                return result
            else:
                if (status_code in [400, 404]) and action == "exists":
                    logger.debug(
                        f"Exists with url {url} operation{action}:{endpoint}: No."
                    )
                elif status_code == 401:
                    self.write_logs(
                        f"Server with url {url} denied operation for {action}:{endpoint}",
                        level="error",
                    )
                elif status_code == 404:
                    logger.debug(
                        f"Server with url {url} did not find {action}:{endpoint}"
                    )
                else:
                    self.write_logs(
                        f"Failed with url {url} operation {action}:{endpoint}",
                        level="error",
                    )
                    self.write_logs(
                        f"Server with url {url} return code: {status_code}.",
                        level="error",
                    )
                    try:
                        self.write_logs(
                            f'Error:\n{result.text.encode("utf-8", errors="backslashreplace")}',
                            level="error",
                        )
                    except Exception:  # pylint: disable=W0703,broad-except
                        self.write_logs("No other info given by server.", level="error")
            return False
        except requests.exceptions.SSLError:
            self.write_logs(
                "Cannot establish a session: SSL/TLS error. Are your server & client certificates valid ?",
                level="error",
            )
            logger.debug("Trace:", exc_info=True)
        except requests.exceptions.ConnectionError as exc:
            self.write_logs(
                f"Cannot establish a session. Looks like we cannot reach the server: {exc}.",
                level="error",
            )
            logger.debug("Trace:", exc_info=True)
        except Exception as exc:  # pylint: disable=W0703,broad-except
            self.write_logs(
                f"Cannot establish a session, unknown reason: {exc}", level="error"
            )
            logger.debug("Trace:", exc_info=True)
        return False

    def requestor(
        self,
        endpoint: str = None,
        action: str = "read",
        data: Any = None,
        raw: bool = False,
    ) -> Union[dict, bytes, bool, str]:
        """
        simple request function that does handle all exceptions and will return content or False
        """
        if action not in self.action_list:
            logger.error("Unknown action %s", action)

        result = self._base_requestor(endpoint, action, data)
        if not result:
            return False
        if self._use_json and not raw:
            try:
                return json.loads(result.text)
            except json.JSONDecodeError as exc:
                logger.error(f"Cannot decode json output: {exc}")
                logger.debug("Trace:", exc_info=True)
                return None
        if raw:
            return result.content
        return result.text

    def get_raw(self, endpoint: str) -> Union[bytes, bool]:
        """
        Shorthand essentially used to download binary files
        """
        result = self._base_requestor(endpoint, action="read")
        if result:
            return result.content
        return result

    def data_model(
        self,
        model: str = None,
        id_record: Optional[Union[int, str]] = None,
        action: str = "read",
        data: Any = None,
        json_output: bool = True,
    ) -> Optional[Union[bool, str, dict]]:
        """
        CRUD(E) model handler for APIs

        Example: update users in /users
        payload = {
            'username': 'Hello',
            'password': 'somepass'
        }
        res = requestor.handle_data_model(model='users', action='update', id=34, data=payload)
        This will call a PUT <server_uri>/users/34
        """
        if self.allowed_models and model not in self.allowed_models:
            logger.error("Model %s is not allowed", model)

        if action not in self.action_list:
            logger.error("Unknown action %s", action)

        if self.allowed_models and self.acls:
            if action not in self.acls[model]:
                logger.error("ACLS don't allow action %s for model %s", action, model)

        # Sanitize model and id_record
        if model:
            model = model.strip().strip("/")

        if id_record:
            id_record = id_record.strip().strip("/")

        if isinstance(id_record, str) and id_record.startswith("#"):
            raise ValueError(
                "id may not start with [#] sign since it is reserved for pagination."
            )
        if id_record:
            # Action is read, exists, update or delete
            model_endpoint = f"{model}/{id_record}"
        else:
            model_endpoint = model

        if json_output:
            if data and isinstance(data, dict):
                data = json.dumps(data)
            self._use_json = True
        result = self.requestor(model_endpoint, action, data)
        return result
