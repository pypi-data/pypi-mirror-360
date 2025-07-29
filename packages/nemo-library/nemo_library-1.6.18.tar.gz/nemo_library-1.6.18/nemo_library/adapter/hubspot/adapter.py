from nemo_library.adapter.base import BaseAdapter
from nemo_library.utils.config import Config


class HubspotAdapter(BaseAdapter):
    """
    Adapter for Hubspot API.
    """

    def __init__(
        self,
        config_file: str = "config.ini",
        environment: str = None,
        tenant: str = None,
        userid: str = None,
        password: str = None,
        hubspot_api_token: str = None,
        migman_local_project_directory: str = None,
        migman_proALPHA_project_status_file: str = None,
        migman_projects: list[str] = None,
        migman_mapping_fields: list[str] = None,
        migman_additional_fields: dict[str, list[str]] = None,
        migman_multi_projects: dict[str, list[str]] = None,
        metadata: str = None,
    ):
        """
        Initializes the adapter instance with configuration settings.

        Args:
            config_file (str): Path to the configuration file. Defaults to "config.ini".
            environment (str, optional): Environment name (e.g., "dev", "prod"). Defaults to None.
            tenant (str, optional): Tenant name. Defaults to None.
            userid (str, optional): User ID for authentication. Defaults to None.
            password (str, optional): Password for authentication. Defaults to None.
            hubspot_api_token (str, optional): API token for HubSpot integration. Defaults to None.
            migman_local_project_directory (str, optional): Directory for local project files. Defaults to None.
            migman_proALPHA_project_status_file (str, optional): Path to the project status file. Defaults to None.
            migman_projects (list[str], optional): List of project names. Defaults to None.
            migman_mapping_fields (list[str], optional): List of mapping fields. Defaults to None.
            migman_additional_fields (dict[str, list[str]], optional): Additional fields for mapping. Defaults to None.
            migman_multi_projects (dict[str, list[str]], optional): Multi-project configurations. Defaults to None.
            metadata (str, optional): Metadata configuration. Defaults to None.
        """

        self.config = Config(
            config_file=config_file,
            environment=environment,
            tenant=tenant,
            userid=userid,
            password=password,
            hubspot_api_token=hubspot_api_token,
            migman_local_project_directory=migman_local_project_directory,
            migman_proALPHA_project_status_file=migman_proALPHA_project_status_file,
            migman_projects=migman_projects,
            migman_mapping_fields=migman_mapping_fields,
            migman_additional_fields=migman_additional_fields,
            migman_multi_projects=migman_multi_projects,
            metadata=metadata,
        )

        super().__init__()

    def extract(self):
        pass

    def transform(self, data):
        pass

    def load(self, data):
        pass
