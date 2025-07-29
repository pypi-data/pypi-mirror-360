import json
import logging
import os
import pandas as pd

from nemo_library.features.migman_database import MigManDatabaseLoad
from nemo_library.model.migman import MigMan
from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import (
    get_migman_fields,
    get_migman_mandatory_fields,
    get_migman_postfixes,
    get_migman_project_list,
    getProjectName,
    is_migman_project_existing,
)

__all__ = ["MigManPrecheckFiles"]


def MigManPrecheckFiles(config: Config) -> dict[str, str]:
    """
    Perform pre-checks on MigMan project files.

    This function validates the existence and structure of project files
    based on the configuration and database definitions. It checks if the
    projects exist in the database, verifies the file structure, and ensures
    mandatory fields are present.

    Args:
        config (Config): Configuration object containing MigMan settings.

    Returns:
        dict[str, str]: A dictionary with project names as keys and their
        status ("ok" or error message) as values.
    """
    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    multi_projects = config.get_migman_multi_projects()
    projects = get_migman_project_list(config)

    database = MigManDatabaseLoad()
    status = {}
    for project in projects:

        try:

            # check for project in database
            if not is_migman_project_existing(database, project):
                raise ValueError(f"project '{project}' not found in database")

            # get list of postfixes
            postfixes = get_migman_postfixes(database, project)

            # init project
            multi_projects_list = (
                (multi_projects[project] if project in multi_projects else None)
                if multi_projects
                else None
            )
            if multi_projects_list:
                for addon in multi_projects_list:
                    for postfix in postfixes:
                        _check_data(
                            config,
                            database,
                            local_project_directory,
                            project,
                            addon,
                            postfix,
                        )
            else:
                for postfix in postfixes:
                    _check_data(
                        config,
                        database,
                        local_project_directory,
                        project,
                        None,
                        postfix,
                    )

            status[project] = "ok"

        except Exception as e:
            status[project] = str(e)  # traceback.format_exc()
            continue

    for project in projects:
        logging.info(
            f"status of project {project}: {json.dumps(status[project],indent=4)}"
        )
    return status


def _check_data(
    config: Config,
    database: list[MigMan],
    local_project_directory: str,
    project: str,
    addon: str,
    postfix: str,
) -> None:
    """
    Validate the data file for a specific project, addon, and postfix.

    This function checks if the data file exists, verifies that all columns
    in the file are defined in the MigMan template, and ensures that all
    mandatory fields are present.

    Args:
        config (Config): Configuration object containing MigMan settings.
        database (list[MigMan]): List of MigMan objects loaded from the database.
        local_project_directory (str): Path to the local project directory.
        project (str): Name of the project.
        addon (str): Addon name for the project (if any).
        postfix (str): Postfix for the project.

    Raises:
        ValueError: If the file contains undefined columns or is missing
        mandatory fields.
    """
    # check for file first
    project_name = getProjectName(project, addon, postfix)
    file_name = os.path.join(
        local_project_directory,
        "srcdata",
        f"{project_name}.csv",
    )

    if os.path.exists(file_name):

        # read the file now and check the fields that are filled in that file
        datadf = pd.read_csv(
            file_name,
            sep=";",
            dtype=str,
        )

        # drop all columns that are totally empty
        columns_to_drop = datadf.columns[datadf.isna().all()]
        datadf_cleaned = datadf.drop(columns=columns_to_drop)

        # check if all columns are defined in MigMan
        columns_migman = get_migman_fields(database, project, postfix)
        for col in datadf_cleaned.columns:
            if not col in columns_migman:
                raise ValueError(
                    f"file {file_name} contains column '{col}' that is not defined in MigMan Template"
                )

        # check mandatory fields
        mandatoryfields = get_migman_mandatory_fields(database, project, postfix)
        for field in mandatoryfields:
            if not field in datadf_cleaned.columns:
                raise ValueError(
                    f"file {file_name} is missing mandatory field '{field}'"
                )
    else:
        raise FileNotFoundError(
            f"Warning! file {file_name} does not exist"
        )
