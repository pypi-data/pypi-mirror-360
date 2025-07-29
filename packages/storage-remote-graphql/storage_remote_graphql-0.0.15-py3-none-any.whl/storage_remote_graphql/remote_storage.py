from logger_local.LoggerLocal import Logger

# TODO Is it a good idea to replace requests with httpx / axios?
import requests
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from python_sdk_remote.utilities import our_get_env
from url_remote.component_name_enum import ComponentName
from url_remote.entity_name_enum import EntityName
from url_remote.our_url import OurUrl
from logger_local.MetaLogger import MetaLogger

# TODO Please replace all strings and Magic Numbers such as "graphql" to const enum  # noqa: E501
version = 1
action = "graphql"
BRAND_NAME = our_get_env('BRAND_NAME')
ENVIRONMENT_NAME = our_get_env('ENVIRONMENT_NAME')

# TODO storage_code_logger_object
storage_logger_object = {
    'component_id': 176,
    'component_name': "storage-remote-graphql-python-package",
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": "gabriel.d@circ.zone"
}
logger = Logger.create_logger(object=storage_logger_object)


class RemoteStorage(metaclass=MetaLogger, object=storage_logger_object):
    def __init__(self) -> None:
        self.url = OurUrl.endpoint_url(
            brand_name=BRAND_NAME, environment_name=ENVIRONMENT_NAME,
            component_name=ComponentName.GROUP_PROFILE.value,
            # TODO version=GROUP_PROFILE_API_VERSION[ENVIRONMENT_NAME] while GROUP_PROFILE_API_VERSION defined in url-remote, see examples in other packages  # noqa: E501
            entity_name=EntityName.GROUP_PROFILE.value, version=version,
            action_name=action)

    def put(self, *, filename: str, local_path: str, created_user_id: int, entity_type_id: int, profile_id: int) -> str:
        """
        Uploads a file to the remote storage and returns the file's remote path.

        :param filename: The name of the file.
        :param local_path: The local path to the file on your system.
        :param created_user_id: The ID of the user who created the file.
        :param entity_type_id: The ID of the entity type associated with the file.
        :param profile_id: The ID of the profile associated with the file.
        :return: The remote path of the uploaded file.
        """
        put_query = f"""
        mutation {{
          put(
            filename: "{filename}",
            local_path: "{local_path}",
            created_user_id: "{created_user_id}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}"
          )
        }}"""
        response = requests.post(self.url, json={"query": put_query})

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            logger.exception(f"Error uploading file: {response_data['errors'][0]['message']}")
        elif "put" not in response_data:
            logger.exception("Unknown error while uploading file", response_data)
        else:
            return response_data["put"]

    def download(self, *, filename: str, local_path: str, entity_type_id: int, profile_id: int) -> str:
        """
        Downloads a file from the remote storage and returns the file's contents.

        :param filename: The name of the file to download.
        :param entity_type_id: The ID of the entity type associated with the file.
        :param profile_id: The ID of the profile associated with the file.
        :param local_path: The local path where the downloaded file should be saved.
        :return: The contents of the downloaded file.
        """
        download_query = f"""
        mutation {{
          download(
            filename: "{filename}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}",
            local_path: "{local_path}"
          )
        }}
        """
        response = requests.post(self.url, json={"query": download_query})

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            logger.exception(f"Error downloading file: {response_data['errors'][0]['message']}")

        return response_data["download"]
