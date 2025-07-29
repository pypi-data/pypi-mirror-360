import logging
import os
import sys
import unittest
from json import loads

from dotenv import load_dotenv

import coder

# from time import sleep

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestCoderAPI(unittest.TestCase):
    def get_user_data_dict(self):
        return {
            "email": "user123@test.com",
            "name": "user teste123",
            "username": "testuser123",
            "disable_login": True,
            "login_type": "",
            "avatar_url": "",
            "organization_ids": [],
            "roles": [],
            "status": "",
            "theme_preference": "",
        }

    def get_token_data_dict(self, user):
        return {
            "user": user,
            # "lifetime_seconds": 1,
            # "scope": "all",
            "token_name": "test token123",
        }

    @classmethod
    def setUpClass(cls):
        load_dotenv()

        coder.token = os.getenv("CODER_TOKEN")
        if not coder.token:
            raise ValueError("The CODER_TOKEN is not defined in the .env file")

        coder.api_domain = os.getenv("API_DOMAIN")
        if not coder.api_domain:
            raise ValueError("The API_DOMAIN is not defined in the .env file")

    def test_list_user(self):
        logger.debug("test_list_user")
        response = coder.User.list()
        logger.debug(f"{response.status_code} {response.text}")
        assert response.status_code == 200

    def test_get_user(self):
        logger.debug("test_get_user")
        response_create = coder.User.create(**self.get_user_data_dict())
        logger.debug(f"create: {response_create.status_code} {response_create.text}")
        user = loads(response_create.text).get("id")

        response = coder.User.get(user=user)
        logger.debug(f"{response.status_code} {response.text}")

        response_delete = coder.User.delete(user=user)
        logger.debug(f"delete: {response_delete.status_code} {response_delete.text}")

        assert response.status_code == 200

    def test_create_delete_user(self):
        logger.debug("test_create_delete_user")
        response_create = coder.User.create(**self.get_user_data_dict())
        logger.debug(f"create: {response_create.status_code} {response_create.text}")
        user = loads(response_create.text).get("id")
        response_delete = coder.User.delete(user=user)
        logger.debug(f"delete: {response_delete.status_code} {response_delete.text}")
        assert response_create.status_code == 201 and response_delete.status_code == 200

    def test_activate_user(self):
        logger.debug("test_activate_user")
        response_create = coder.User.create(**self.get_user_data_dict())
        logger.debug(f"create: {response_create.status_code} {response_create.text}")
        user = loads(response_create.text).get("id")
        # sleep(10)
        response = coder.User.activate(user=user)
        logger.debug(f"{response.status_code} {response.text}")
        # sleep(10)
        response_delete = coder.User.delete(user=user)
        logger.debug(f"delete: {response_delete.status_code} {response_delete.text}")

        assert response.status_code == 200

    def test_suspend_user(self):
        logger.debug("test_suspend_user")
        response_create = coder.User.create(**self.get_user_data_dict())
        logger.debug(f"create: {response_create.status_code} {response_create.text}")
        user = loads(response_create.text).get("id")
        response = coder.User.suspend(user=user)
        logger.debug(f"{response.status_code} {response.text}")
        response_delete = coder.User.delete(user=user)
        logger.debug(f"delete: {response_delete.status_code} {response_delete.text}")

        assert response.status_code == 200

    def test_user_auth_methods(self):
        logger.debug("test_user_auth_methods")
        response = coder.User.auth_methods()
        logger.debug(f"{response.status_code} {response.text}")

        assert response.status_code == 200

    def test_get_user_ssh_key(self):
        logger.debug("test_get_user_ssh_key")
        response_create = coder.User.create(**self.get_user_data_dict())
        logger.debug(f"create: {response_create.status_code} {response_create.text}")
        user = loads(response_create.text).get("id")
        response = coder.User.ssh_key(user=user)
        logger.debug(f"{response.status_code} {response.text}")
        response_delete = coder.User.delete(user=user)
        logger.debug(f"delete: {response_delete.status_code} {response_delete.text}")

        assert response.status_code == 200

    def test_user_create_session_key(self):
        logger.debug("test_user_create_sesion_key")
        response_create = coder.User.create(**self.get_user_data_dict())
        logger.debug(f"create: {response_create.status_code} {response_create.text}")
        user = loads(response_create.text).get("id")
        response = coder.User.create_session_key(user=user)
        logger.debug(f"{response.status_code} {response.text}")
        response_delete = coder.User.delete(user=user)
        logger.debug(f"delete: {response_delete.status_code} {response_delete.text}")

        assert response.status_code == 201

    def test_get_user_organizations(self):
        logger.debug("test_get_user_organizations")

        response = coder.User.create(**self.get_user_data_dict())
        user = loads(response.text).get("id")

        response = coder.User.get_organizations(
            user=user,
        )
        coder.User.delete(user=user)
        logger.debug(f"{response.status_code} {response.text}")
        assert response.status_code == 200

    def test_list_organizations(self):
        logger.debug("test_list_organizations")
        response = coder.Organization.list()
        logger.debug(f"response: {response.url} {response.status_code} {response.text}")
        assert response.status_code == 200

    def test_get_organization(self):
        logger.debug("test_get_organization")

        response_list = coder.Organization.list()
        logger.debug(f"response: {response_list.status_code} {response_list.text}")
        org_id = loads(response_list.text)[0].get("id")

        response_get = coder.Organization.get(organization_id=org_id)
        logger.debug(f"response: {response_get.status_code} {response_get.text}")
        assert response_get.status_code == 200

    # def test_create_delete_organization(self):
    #     logger.debug("test_create_delete_organization")

    #     response_create = coder.Organization.create(
    #         name="organization-test123",
    #         display_name="org123",
    #         description="org test",
    #     )
    #     logger.debug(f"{response_create.status_code} {response_create.text}")
    #     org_id = loads(response_create.text).get("id")

    #     response_delete = coder.Organization.delete(organization_id=org_id)
    #     logger.debug(f"{response_delete.status_code} {response_delete.text}")
    #     assert response_create.status_code == 201 and response_delete.status_code == 200

    def test_get_workspaces(self):
        logger.debug("test_get_workspaces")
        response = coder.Workspace.list()
        logger.debug(f"response: {response.status_code} {response.text}")
        assert response.status_code == 200

    # def test_create_user_workspace(self):
    #     logger.debug("test_create_workspace")

    #     try:
    #         response_create_user = coder.User.create(**self.get_user_data_dict())
    #         logger.debug(f"response_create_user: {response_create_user.status_code} {response_create_user.text}")
    #         user = loads(response_create_user.text).get("id")
    #     except Exception as e: logger.exception(e)

    #     try:
    #         response_templates = coder.Template.list()
    #         templates = loads(response_templates.text)
    #         # template_version_id = next(t for t in templates if t.get("name") == "scratch").get("active_version_id")
    #         if len(templates) < 1:
    #             logger.debug("There is no template available")
    #             return
    #         template_version_id = templates[0].get("active_version_id")
    #         response_parameters = coder.Template.get_parameters(template_version_id=template_version_id)
    #         logger.debug(f"param: {loads(response_parameters.text)[1].get("options")}")
    #         parameters_opt = loads(response_parameters.text)[1].get("options")
    #         kwargs1 = {
    #             "automatic_updates": "always",
    #             "autostart_schedule": "*/5 * * * *",
    #             "name": "testuser123",
    #             "rich_parameter_values": [
    #                 {
    #                     "name": parameters_opt[1].get("name"),
    #                     "value": parameters_opt[1].get("value"),
    #                 }
    #             ],
    #             "template_version_id": template_version_id,
    #             "ttl_ms": 0
    #         }
    #         logger.debug(f"kwargs1: {kwargs1}")

    #         response_create_workspace = coder.Workspace.create(
    #             user=user,
    #             **kwargs1,
    #         )
    #         logger.debug(
    #             f"response_create_workspace: {response_create_workspace.status_code} \
    #             {response_create_workspace.text}"
    #         )

    #         # kwargs2 = kwargs1.copy()
    #         # kwargs2["name"] = "test789"
    #         # kwargs2["rich_parameter_values"] = [
    #         #     {
    #         #         "name": parameters_opt[2].get("name"),
    #         #         "value": parameters_opt[2].get("value"),
    #         #     }
    #         # ]
    #         # logger.debug(f"kwargs2: {kwargs2}")
    #         # org_id = loads(coder.Organization.list().text)[0].get("id")
    #         # logger.debug(f"org_id: {org_id}")
    #         # response_create_workspace_org = coder.Workspace.create(
    #         #     user=user,
    #         #     organization_id=org_id,
    #         #     **kwargs2,
    #         # )
    #         # logger.debug(
    #         #     f"response_create_workspace_org: {response_create_workspace_org.status_code} \
    #         #     {response_create_workspace_org.text}"
    #         # )
    #         worksapce_id = loads(response_create_workspace.text).get("id")
    #         response_get_workspace = coder.Workspace.get(workspace_id=worksapce_id)
    #         logger.debug(
    #             f"response_get_workspace: {response_get_workspace.status_code} {response_get_workspace.text}"
    #         )

    #         response_workspace_status = coder.Workspace.status(workspace_id=worksapce_id)
    #         logger.debug(
    #             f"response_workspace_status: {response_workspace_status.status_code} {response_workspace_status.text}"
    #         )

    #         sleep(20)
    #         response_delete_workspace = coder.Workspace.delete(workspace=worksapce_id)
    #         logger.debug(
    #             f"response_delete_workspace: {response_delete_workspace.status_code} {response_delete_workspace.text}"
    #         )
    #         sleep(10)
    #     except Exception as e: logger.exception(e)

    #     try:
    #         response_delete_user = coder.User.delete(user=user)
    #         logger.debug(f"response_delete_user: {response_delete_user.status_code} {response_delete_user.text}")
    #     except Exception as e: logger.exception(e)

    #     assert (
    #         response_create_workspace.status_code == 201
    #         and response_get_workspace.status_code == 200
    #         and response_workspace_status.status_code == 200
    #         and response_delete_workspace.status_code == 201
    #         # and response_create_workspace_org.status_code == 201
    #     )

    # def test_delete_workspace(self):
    #     logger.debug("test_delete_workspace")
    #     response_delete_workspace = coder.Workspace.delete(workspace="5fa0166d-5ed9-4dd4-b6fe-0124d6799778")
    #     logger.debug(
    #         f"response_delete_workspace: {response_delete_workspace.status_code} {response_delete_workspace.text}"
    #     )

    #     assert response_delete_workspace == 200

    def test_user_tokens(self):
        logger.debug("test_get_user_tokens")

        try:
            response_create_user = coder.User.create(**self.get_user_data_dict())
            logger.debug(f"response_create_user: {response_create_user.status_code} {response_create_user.text}")
            user = loads(response_create_user.text).get("id")
        except Exception as e:
            logger.exception(e)

        try:
            response_create_token = coder.User.create_token(**self.get_token_data_dict(user=user))
            # response_create_token = coder.User.create_token(user=user)
            logger.debug(f"response_create_token: {response_create_token.status_code} {response_create_token.text}")

            response_get_tokens = coder.User.get_tokens(user=user)
            logger.debug(f"response_get_tokens: {response_get_tokens.status_code} {response_get_tokens.text}")

            response_get_token_by_name = coder.User.get_token(
                user=user, key_name=self.get_token_data_dict(user=user).get("token_name")
            )
            logger.debug(
                f"response_get_token_by_name: {response_get_token_by_name.status_code} \
                {response_get_token_by_name.text}"
            )
            token_id = loads(response_get_token_by_name.text).get("id")

            response_get_token_by_id = coder.User.get_token(user=user, token_id=token_id)
            logger.debug(
                f"response_get_token_by_id: {response_get_token_by_id.status_code} {response_get_token_by_id.text}"
            )

            response_delete_token = coder.User.delete_token(user=user, token_id=token_id)
            logger.debug(f"response_delete_token: {response_delete_token.status_code} {response_delete_token.text}")
        except Exception as e:
            logger.exception(e)

        try:
            response_delete_user = coder.User.delete(user=user)
            logger.debug(f"response_delete_user: {response_delete_user.status_code} {response_delete_user.text}")
        except Exception as e:
            logger.exception(e)

        assert (
            response_create_token.status_code == 201
            and response_get_tokens.status_code == 200
            and response_get_token_by_name.status_code == 200
            and response_get_token_by_id.status_code == 200
            and response_delete_token.status_code == 204
        )

    def test_list_templates(self):
        logger.debug("test_list_templates")
        response = coder.Template.list()
        logger.debug(f"response: {response.status_code} {response.text}")

        response_org = coder.Organization.list()
        logger.debug(f"response org: {response_org.status_code} {response_org.text}")
        org_id = loads(response_org.text)[0].get("id")

        response_org_templates = coder.Template.list(organization_id=org_id)
        logger.debug(f"response_org_templates: {response_org_templates.status_code} {response_org_templates.text}")
        assert response.status_code == 200 and response_org_templates.status_code == 200

    def test_list_template_examples(self):
        logger.debug("test_list_template_examples")
        # response = coder.Template.list_examples()
        # logger.debug(f"response: {response.url} {response.status_code} {response.text}")

        response_org = coder.Organization.list()
        logger.debug(f"response org: {response_org.status_code} {response_org.text}")
        org_id = loads(response_org.text)[0].get("id")

        response_org_templates = coder.Template.list_examples(organization_id=org_id)
        logger.debug(f"response_org_templates: {response_org_templates.status_code} {response_org_templates.text}")
        assert response_org_templates.status_code == 200
        # assert response.status_code == 200 and response_org_templates.status_code == 200

    def test_get_template(self):
        logger.debug("test_get_template")

        response_list = coder.Template.list()
        logger.debug(f"response: {response_list.status_code} {response_list.text}")
        template_id = loads(response_list.text)[0].get("id")

        response_get = coder.Template.get(template_id=template_id)
        logger.debug(f"response: {response_get.url} {response_get.status_code} {response_get.text}")
        assert response_get.status_code == 200

    # def test_create_template(self):
    #     logger.debug("test_create_template")
    #     response = coder.Template.create(
    #         organization_id="17690503-7359-47b7-b78f-f74461045e5d",
    #         **{
    #             "activity_bump_ms": 0,
    #             "allow_user_autostart": True,
    #             "allow_user_autostop": True,
    #             "allow_user_cancel_workspace_jobs": True,
    #             "autostart_requirement": {
    #                 "days_of_week": ["monday"],
    #             },
    #             "autostop_requirement": {
    #                 "days_of_week": ["monday"],
    #                 "weeks": 0,
    #             },
    #             "default_ttl_ms": 0,
    #             "delete_ttl_ms": 0,
    #             "description": "string",
    #             "disable_everyone_group_access": True,
    #             "display_name": "string",
    #             "dormant_ttl_ms": 0,
    #             "failure_ttl_ms": 0,
    #             "icon": "string",
    #             "name": "string",
    #             "require_active_version": True,
    #             "template_version_id": "7931bd81-df00-4b1a-8bc1-10c6f15db53c",
    #         }
    #     )
    #     logger.debug(f"response: {response.url} {response.status_code} {response.text}")
    #     assert response.status_code == 200

    def test_template_version(self):
        logger.debug("test_get_template_versions")
        response_get_template = coder.Template.list()
        logger.debug(f"response_get_template: {response_get_template.status_code} {response_get_template.text}")
        template_id = loads(response_get_template.text)[0].get("id")

        response_template_versions = coder.Template.get_versions(template_id=template_id)
        logger.debug(
            f"response_template_versions: {response_template_versions.status_code} {response_template_versions.text}"
        )
        version_name = loads(response_template_versions.text)[0].get("name")

        response_template_version = coder.Template.get_version(
            template_id=template_id, template_version_name=version_name
        )
        logger.debug(
            f"response_template_version: {response_template_version.status_code} {response_template_version.text}"
        )

        assert response_template_versions.status_code == 200 and response_template_version.status_code == 200

    def test_get_template_parameters(self):
        logger.debug("test_get_template_parameters")
        response_templates = coder.Template.list()
        logger.debug(f"response_templates: {response_templates.status_code} {response_templates.text}")
        templates = loads(response_templates.text)
        # template_version_id = next(t for t in templates if t.get("name") == "scratch").get("active_version_id")
        if len(templates) < 1:
            logger.debug("There is no template available")
            return
        template_version_id = templates[0].get("active_version_id")
        logger.debug(f"template_version_id, {template_version_id}")
        response_parameters = coder.Template.get_parameters(template_version_id=template_version_id)
        logger.debug(f"response_parameters: {response_parameters.status_code} {response_parameters.text}")
        assert response_parameters.status_code == 200

    # def test_delete_users(self):
    #     logger.debug("test_delete_users")
    #     users = loads(coder.User.list().text).get("users")
    #     for user in users:
    #         print(user.get("name"), user)
    #         input()
    #         if user.get('name') == "admin":
    #             continue
    #         r = coder.User.delete(user=user.get('username'))
    #         print("response: ", r.status_code, r.text)


if __name__ == "__main__":
    logger.debug("MAIN_______________________")
    unittest.main()
