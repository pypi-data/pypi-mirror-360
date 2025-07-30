import logging
from typing import Dict, Any, List, Optional

import urllib3
from atlassian import Confluence
from atlassian.errors import ApiError
from atlassian.rest_client import AtlassianRestAPI
from requests import HTTPError

from confluence_cli.cli.comala_api import ComalaAPI
from confluence_cli.cli.types import Page
from confluence_cli.cli.utils import (
    type_wrap_decorator,
    type_wrap,
    requests_error_handling,
    base_methods_decorator,
)

# * logger definition
logger = logging.getLogger("confluence_log")
# * Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


@base_methods_decorator(
    deco=type_wrap_decorator, regex=r"_response_handler", base_class=AtlassianRestAPI
)
@base_methods_decorator(
    deco=requests_error_handling,
    regex=r"(post|put|delete)",
    base_class=AtlassianRestAPI,
)
class ConfluenceWrapper(Confluence):
    """Atlassian Confluence api cliente wrapper for extension and control purpouses.

    Admisible params:

    params = {
        "baseURL": "http://confluence:8090",
        "user": "myuser",
        "password": "mypass",
        "token": ""  # Personal access token as an alternative to user/pass
        "proxies": {
            "http": "",
            "https": ""
        },
        "verify_ssl": False
    }

    confluence_api = ConfluenceWrapper(params)
    """

    ## Borg pattern
    _shared_state: dict = {}

    def __init__(self, params: Dict[str, Any], **kwargs):
        self.__dict__ = ConfluenceWrapper._shared_state
        if not self.__dict__ or params:
            username = params.get("username")
            password = params.get("password")
            token = params.get("token")
            if token and username and password:
                logger.warning(
                    "token param was provided along with user/password data. Token takes precedence"
                )
            if token:
                username = password = None

            super().__init__(
                url=params["baseURL"],
                username=username,
                password=password,
                token=token,
                proxies=params.get("proxies"),
                verify_ssl=params.get("verify_ssl"),
                **kwargs
            )

            logger.info("Confluence python client initialized")

    def get_comala_api(self, token: str = None) -> ComalaAPI:
        return ComalaAPI(
            url=self.__dict__["url"],
            username=self.__dict__["username"],
            password=self.__dict__["password"],
            token=token,
            proxies=self.__dict__["proxies"],
            verify_ssl=self.__dict__["verify_ssl"],
        )

    @requests_error_handling
    def get(
            self,
            path,
            data=None,
            flags=None,
            params=None,
            headers=None,
            not_json_response=None,
            trailing=None,
            absolute=False,
            advanced_mode=False,
    ):
        """Overriden GET operations to ensure custom type return."""
        logger.debug(f"{path} , params: {params}")
        result = super().get(
            path,
            data,
            flags,
            params,
            headers,
            not_json_response,
            trailing,
            absolute,
            advanced_mode,
        )
        if not_json_response or advanced_mode:
            return result
        if path == "rest/api/search" and not params.get("cursor"):  # ? cql() search
            return result
        if path == "rest/api/search" and params.get("cursor"):  # ? get of next cursor in search
            content_list = self._get_content_from_cql_result(result)
            if self.cloud:  # Cloud pagination returning dict instead of list of content
                return {
                    "results": content_list,
                    "totalSize": result["totalSize"],
                    "_links": result.get("_links"),
                }
            else:
                return content_list

        if result.get("results"):
            return {"results": [type_wrap(content) for content in result.get("results")]}
        elif result.get("id"):
            return type_wrap(result)
        else:
            return result

    @staticmethod
    def _get_content_from_cql_result(cql_result: dict):
        if not cql_result:
            return []
        content_list = list()
        results: Optional[list] = cql_result.get("results")
        if not results:
            return
        for result in results:
            content = result.get("content")
            if content:  # Non pages (blogs, comments) results do not have "content"
                content["lastModified"] = result["lastModified"]
                content["totalSize"] = cql_result["totalSize"]
                content_list.append(type_wrap(content))
            else:
                logger.warning(
                    f"Result with no content: firt key {list(result.keys())[0]}"
                )
        return content_list

    def cql(
            self,
            cql,
            start=0,
            limit=None,
            expand=None,
            include_archived_spaces=None,
            excerpt=None,
    ):

        cql_result = super().cql(cql, start, limit, expand, include_archived_spaces, excerpt)
        if cql_result:
            content_list = self._get_content_from_cql_result(cql_result)
        if self.cloud:  # Cloud pagination returning dict instead of list of content
            return {
                "results": content_list,
                "totalSize": cql_result["totalSize"],
                "_links": cql_result.get("_links"),
            }

        return content_list

    @requests_error_handling
    def add_space_permissions_rpc(
            self, space_key: str, permissions: List[str], entity_name: str
    ) -> bool:
        """Adds space permissions to entity ('user'|'group') via JSON-RPC API.

        Args:
            space_key (str):
            permissions (List[str]): List of permissions:
                https://developer.atlassian.com/server/confluence/remote-confluence-methods/
            entity_name (str): Name of the user or group.

        Returns:
            bool: True if space permissions added succesfully
        """
        url = "rpc/json-rpc/confluenceservice-v2"
        data = {
            "jsonrpc": "2.0",
            "method": "addPermissionsToSpace",
            "id": 7,
            "params": [permissions, entity_name, space_key],
        }
        logger.debug(f"params: {data['params']}")
        json = self.post(url, data=data)
        logger.debug(json)
        return json.get("result")

    @requests_error_handling
    def remove_space_permission(
            self, space_key: str, permission: str, entity_name: str
    ) -> bool:
        """Remove specific space permission from entity with name entity_name

        Args:
            space_key (str): space key.
            permission (str): https://developer.atlassian.com/server/confluence/remote-confluence-methods/
            entity_name (str): Name of the user or group.

        Returns:
            bool: True on success False otherwise.
        """
        url = "rpc/json-rpc/confluenceservice-v2"
        data = {
            "jsonrpc": "2.0",
            "method": "removePermissionFromSpace",
            "id": 7,
            "params": [permission, entity_name, space_key],
        }
        logger.debug(f"params: {data['params']}")
        json = self.post(url, data=data)
        logger.debug(json)
        return json.get("result")

    @requests_error_handling
    def add_content_restrictions(
            self, content_id: str, operations: List[str], entity_name: str, entity_type: str

    ) -> dict:
        """add read or update restrictions to content_id.

        Args:
            content_id (str): Content id
            operations (List[str]): List with "read" and "update" tokens. Ex: ["read"], ["read", "update"] ...
            entity_name (str): Name of the user or group
            entity_type (str): "user"|"group"

        Returns:
            dict: [description]
        """ """"""

        url = f"rest/experimental/content/{content_id}/restriction"
        restriction_type = entity_type if entity_type == "group" else "known"
        identifier_label = "username" if entity_type == "user" else "name"
        data_list: List[dict] = []
        for operation in operations:
            data_oper: dict = {
                "operation": operation,
                "restrictions": {
                    entity_type: [{"type": restriction_type, identifier_label: entity_name}]

                },
            }

            data_list.append(data_oper)
        json = self.put(url, data=data_list)
        return json

    @requests_error_handling
    def delete_content_restrictions(
            self, content_id: str, operations: List[str], entity_name: str, entity_type: str

    ) -> dict:
        """delete read or update restrictions to content_id.

        Args:
            content_id (str): Content id
            operations (List[str]): List with "read" and "update" tokens. Ex: ["read"], ["read", "update"] ...
            entity_name (str): Name of the user or group
            entity_type (str): "user"|"group"

        Returns:
            dict: [description]
        """ """"""

        url = f"rest/experimental/content/{content_id}/restriction"
        restriction_type = entity_type if entity_type == "group" else "known"
        identifier_label = "username" if entity_type == "user" else "name"
        data_list: List[dict] = []
        for operation in operations:
            data_oper: dict = {
                "operation": operation,
                "restrictions": {
                    entity_type: [{"type": restriction_type, identifier_label: entity_name}]

                },
            }
            data_list.append(data_oper)
        json = self.delete(url, data=data_list)
        return json

    def delete_content_restriction(
            self, content_id: str, operation: str, entity_name: str, entity_type: str
    ):
        """Deletes content restriction for a operation on a content for a entity.

        Args:
            content_id (str): content id
            operation (str): "read" | "update"
            entity_name (str): User or group name
            entity_type (str): "user" | "group"
        """
        url = f"rest/experimental/content/{content_id}/restriction/byOperation/{operation}/{entity_type}/{entity_name}"
        self.delete(url)

    def get_pages_detail_lines(self, cql: str, space_key: str, page_size, page_index: int):
        url: str = "rest/masterdetail/1.0/detailssummary/lines"
        params: Dict[str, str] = {
            "cql": cql,
            "spaceKey": space_key,
            "pageSize": str(page_size),  # ! Critical value!!
            "pageIndex": str(page_index),
        }
        return self.get(url, params=params)

    def get_page_properties(self, page_id, limit: int = 100):
        """
        Get the page (content) properties
        :param page_id: content_id format
        :return: get properties
        """
        params = {
            "limit": limit
        }
        url = "rest/api/content/{page_id}/property".format(page_id=page_id)

        try:
            response = self.get(path=url, params=params)
        except HTTPError as e:
            if e.response.status_code == 404:
                # Raise ApiError as the documented reason is ambiguous
                raise ApiError(
                    "There is no content with the given id, "
                    "or the calling user does not have permission to view the content",
                    reason=e,
                )

            raise

        return response

    def set_page_labels(self, page_id: str, labels: List[str]):
        url = f"rest/api/content/{page_id}/label"
        data: List[Dict[str, str]] = []
        for label in labels:
            data.append({"prefix": "global", "name": label})
        try:
            response = self.post(path=url, data=data)
        except HTTPError as e:
            if e.response.status_code == 404:
                # Raise ApiError as the documented reason is ambiguous
                raise ApiError(
                    "There is no content with the given id, "
                    "or the calling user does not have permission to view the content",
                    reason=e,
                )
            raise
        return response

    def create_page_from_template(
            self,
            space: str,
            title: str,
            template_pageid: str,
            parent_id=None,
            type="page",
            editor=None,
    ):
        """
        Creates a page using another page as template.

        Note: At this moment REST API doesn't support create from template natively so this method is needed
        """
        template_page: Page = self.get_page_by_id(
            page_id=template_pageid,
            expand="body.storage"
        )

        response_page: Page = self.create_page(
            space=space,
            title=title,
            body=template_page.body_storage,
            type="page",
            parent_id=parent_id,
            representation="storage"
        )

        return response_page
