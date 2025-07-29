import logging
from http import HTTPStatus
from json import dumps, loads
from typing import List, Optional

import requests

import coder

logger = logging.getLogger(__name__)


def get_api_domain():
    return coder.api_domain


def get_access_header():

    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Coder-Session-Token": coder.token,
    }


class User:
    @classmethod
    def list(cls) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + "users"
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get(
        cls,
        user: str,
    ) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + f"users/{user}"
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def create(
        cls,
        email: str,
        name: str,
        username: str,
        disable_login: bool = True,
        login_type: Optional[str] = None,  # choices: 'oidc', 'password'
        avatar_url: Optional[str] = None,
        organization_ids: List[str] = [],
        roles: List[str] = [],
        status: Optional[str] = "active",
        theme_preference: Optional[str] = "",
    ) -> requests.Response:
        logger.debug("user create")
        headers = get_access_header()
        body = {
            "avatar_url": avatar_url,
            "email": email,
            "name": name,
            "username": username,
            "disable_login": disable_login,
            "login_type": login_type,
            "organization_ids": organization_ids,
            "roles": roles,
            "status": status,
            "theme_preference": theme_preference,
        }
        url = get_api_domain() + "users"

        response = requests.request(method="POST", url=url, headers=headers, data=dumps(body))

        return response

    @classmethod
    def get_or_create(
        cls,
        email: str,
        name: str,
        username: str,
        disable_login: bool = True,
        login_type: Optional[str] = None,  # choices: 'oidc', 'password'
        avatar_url: Optional[str] = None,
        organization_ids: List[str] = [],
        roles: List[str] = [],
        status: Optional[str] = "active",
        theme_preference: Optional[str] = "",
    ) -> requests.Response:
        response_create = cls.create(
            email=email,
            name=name,
            username=username,
            disable_login=disable_login,
            login_type=login_type,
            avatar_url=avatar_url,
            organization_ids=organization_ids,
            roles=roles,
            status=status,
            theme_preference=theme_preference,
        )
        if response_create.status_code == HTTPStatus.CREATED:
            return response_create

        response_get = cls.get(user=username)
        if response_get.status_code == HTTPStatus.OK:
            return response_get

        response = requests.Response()
        response.status_code = 422
        response._content = dumps(
            {
                "info": "Can't get or create user.",
                "create status": response_create.status_code,
                "create message": response_create.text,
                "get status": response_get.status_code,
                "get message": response_get.text,
            }
        )
        return response

    @classmethod
    def delete(cls, user: str) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + f"users/{user}"
        response = requests.request(method="DELETE", url=url, headers=headers)
        return response

    @classmethod
    def activate(
        cls,
        user: str,
    ) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + f"users/{user}/status/activate"
        response = requests.request(method="PUT", url=url, headers=headers)
        return response

    @classmethod
    def suspend(
        cls,
        user: str,
    ) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + f"users/{user}/status/suspend"
        response = requests.request(method="PUT", url=url, headers=headers)
        return response

    @classmethod
    def auth_methods(cls) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + "users/authmethods"
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def ssh_key(
        cls,
        user: str,
    ) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + f"users/{user}/gitsshkey"
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def create_session_key(
        cls,
        user: str,
    ) -> requests.Response:
        headers = get_access_header()
        url = get_api_domain() + f"users/{user}/keys"
        response = requests.request(method="POST", url=url, headers=headers)
        return response

    @classmethod
    def get_organizations(
        cls,
        user: str,
    ) -> requests.Response:
        url = get_api_domain() + f"users/{user}/organizations"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get_tokens(
        cls,
        user: str,
    ) -> requests.Response:
        url = get_api_domain() + f"users/{user}/keys/tokens"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def create_token(
        cls,
        user: str,
        token_name: Optional[str] = None,
        lifetime_seconds: Optional[int] = None,
        scope: Optional[str] = None,
    ) -> requests.Response:
        url = get_api_domain() + f"users/{user}/keys/tokens"
        headers = get_access_header()
        body = {
            "lifetime_seconds": lifetime_seconds,
            "scope": scope,
            "token_name": token_name,
        }
        response = requests.request(method="POST", url=url, headers=headers, data=dumps(body))
        return response

    @classmethod
    def get_token(
        cls,
        user: str,
        key_name: Optional[str] = None,
        token_id: Optional[str] = None,
    ) -> requests.Response:
        if key_name and token_id:
            raise ValueError("'key_name' and 'token_id' params shouldn't be used together.")
        elif key_name:
            url = get_api_domain() + f"users/{user}/keys/tokens/{key_name}"
        elif token_id:
            url = get_api_domain() + f"users/{user}/keys/{token_id}"
        else:
            raise ValueError("One of 'key_name' and 'token_id' params are required.")

        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def delete_token(cls, user: str, token_id: str) -> requests.Response:
        url = get_api_domain() + f"users/{user}/keys/{token_id}"
        headers = get_access_header()
        response = requests.request(method="DELETE", url=url, headers=headers)
        return response


class Workspace:
    @classmethod
    def list(
        cls,
    ) -> requests.Response:
        url = get_api_domain() + "workspaces"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        print(response.text)
        return response

    @classmethod
    def get(
        cls,
        workspace_id,
    ):
        url = get_api_domain() + f"workspaces/{workspace_id}"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        print(response.text)
        return response

    @classmethod
    def get_user_workspace(
        cls,
        user,
        workspace_name,
    ):
        url = get_api_domain() + f"users/{user}/workspace/{workspace_name}"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def status(
        cls,
        workspace_id,
    ):
        response = cls.get(workspace_id=workspace_id)

        # response = requests.Response()
        if response.status_code == HTTPStatus.OK:
            response._content = dumps({"status": loads(response.text).get("latest_build", {}).get("status")}).encode()
        return response

    @classmethod
    def get_listening_ports(
        cls,
        workspace_agent_id,
    ):
        url = get_api_domain() + f"workspaceagents/{workspace_agent_id}/listening-ports"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def create(
        cls,
        user: str,
        name: str,
        template_version_id: str,
        organization_id: Optional[str] = None,
        rich_parameter_values: List[str] = [],
        template_id: Optional[str] = None,
        automatic_updates: str = "always",
        autostart_schedule: Optional[str] = None,
        ttl_ms: Optional[int] = None,
        # max_deadline # TODO: testar isso,
    ) -> requests.Response:
        # if not(template_version_id ^ template_id):
        #     raise ValueError("'template_version_id' and 'template_id' params shouldn't be used together.")

        if organization_id:
            url = get_api_domain() + f"organizations/{organization_id}/members/{user}/workspaces"
        else:
            url = get_api_domain() + f"users/{user}/workspaces"
        headers = get_access_header()
        body = {
            "name": name,
            "template_version_id": template_version_id,
            "rich_parameter_values": rich_parameter_values,
            "template_id": template_id,
            "automatic_updates": automatic_updates,
            "autostart_schedule": autostart_schedule,  # https://crontab.cronhub.io/
            "ttl_ms": ttl_ms,
            # "max_deadline": str(datetime.now().astimezone() + timedelta(hours=3, minutes=1)),
            # "deadline": str(datetime.now().astimezone() + timedelta(hours=3, minutes=1)),
        }
        print("body: ", body)
        response = requests.request(method="POST", url=url, headers=headers, data=dumps(body))
        return response

    @classmethod
    def start(cls, workspace):
        url = get_api_domain() + f"workspaces/{workspace}/builds"
        headers = get_access_header()
        body = {"transition": "start"}
        response = requests.request(method="POST", url=url, headers=headers, data=dumps(body))
        return response

    @classmethod
    def delete(cls, workspace):
        url = get_api_domain() + f"workspaces/{workspace}/builds"
        headers = get_access_header()
        body = {"orphan": False, "transition": "delete"}
        response = requests.request(method="POST", url=url, headers=headers, data=dumps(body))
        return response

    # @classmethod
    # def apps(cls, workspace):
    #     url = get_api_domain() + f"workspaces/{workspace}/"
    #     headers = get_access_header()
    #     response = requests.request(method="GET", url=url, headers=headers)
    #     return response

    @classmethod
    def agents(cls, workspaceagent_id):
        url = get_api_domain() + f"workspaceagents/{workspaceagent_id}"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response


class Organization:
    @classmethod
    def list(cls) -> requests.Response:
        url = get_api_domain() + "organizations"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get(
        cls,
        organization_id: str,
    ) -> requests.Response:
        url = get_api_domain() + f"organizations/{organization_id}"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def create(
        cls,
        name: str,
        display_name: Optional[str] = "",
        description: Optional[str] = "",
        icon: Optional[str] = "",
    ) -> requests.Response:
        url = get_api_domain() + "organizations"
        headers = get_access_header()
        body = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "icon": icon,
        }
        response = requests.request(method="POST", url=url, headers=headers, data=dumps(body))
        return response

    @classmethod
    def delete(cls, organization_id: str) -> requests.Response:
        url = get_api_domain() + f"organizations/{organization_id}"
        headers = get_access_header()
        response = requests.request(method="DELETE", url=url, headers=headers)
        return response


class Template:
    @classmethod
    def list(
        cls,
        organization_id: Optional[str] = None,
    ) -> requests.Response:
        if organization_id:
            url = get_api_domain() + f"organizations/{organization_id}/templates"
        else:
            url = get_api_domain() + "templates"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get(
        cls,
        template_id: str,
    ) -> requests.Response:
        url = get_api_domain() + f"templates/{template_id}"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get_versions(
        cls,
        template_id: str,
    ) -> requests.Response:
        url = get_api_domain() + f"templates/{template_id}/versions/"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get_version(
        cls,
        template_id: str,
        template_version_name: str,
    ) -> requests.Response:
        url = get_api_domain() + f"templates/{template_id}/versions/{template_version_name}"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def list_examples(
        cls,
        organization_id: str,
    ) -> requests.Response:
        url = get_api_domain() + f"organizations/{organization_id}/templates/examples"
        # if organization_id:
        #     url = get_api_domain() + f"organizations/{organization_id}/templates/examples"
        # else:
        #     url = get_api_domain() + "templates/examples"  # API does not respond to this endpoint
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def get_parameters(
        cls,
        template_version_id: str,
    ) -> requests.Response:
        url = get_api_domain() + f"templateversions/{template_version_id}/rich-parameters"
        headers = get_access_header()
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    @classmethod
    def create_version(
        cls,
        organization_id: str,
        name: str,
        file_id: str,
        storage_method: str = "file",
        provisioner: str = "terraform",
        **kwargs,
    ) -> requests.Response:
        url = get_api_domain() + f"organizations/{organization_id}/templateversions"
        headers = get_access_header()

        body = {
            "name": name,
            "file_id": file_id,
            "storage_method": storage_method,
            "provisioner": provisioner,
            **kwargs,
        }

        return requests.request(method="POST", url=url, headers=headers, data=dumps(body))

    @classmethod
    def create(cls, organization_id: str, name: str, template_version_id: str, **kwargs) -> requests.Response:
        url = get_api_domain() + f"organizations/{organization_id}/templates"
        headers = get_access_header()

        body = {"name": name, "template_version_id": template_version_id, **kwargs}

        return requests.request(method="POST", url=url, headers=headers, data=dumps(body))


class File:
    @staticmethod
    def upload(zip_file_path: str) -> str:

        url = get_api_domain() + "files"
        headers = {**get_access_header(), "Content-Type": "application/x-tar"}
        with open(zip_file_path, "rb") as f:
            resp = requests.request(method="POST", url=url, headers=headers, data=f)
        resp.raise_for_status()
        return resp.json()["hash"]

    @staticmethod
    def download(file_id: str, output_path: str) -> None:

        url = get_api_domain() + f"files/{file_id}?download=true"
        headers = get_access_header()
        resp = requests.request(method="GET", url=url, headers=headers, stream=True)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
