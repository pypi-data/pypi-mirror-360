from typing import Annotated, List, Optional

from fastmcp import Context as ServerContext
from pydantic import Field, StringConstraints

from devopness.models import (
    LanguageRuntime,
    SourceTypePlain,
)

from ..auth import get_credentials
from ..devopness_api import devopness, ensure_authenticated
from ..models import ActionSummary, ApplicationSummary, VariableSummary
from ..response import MCPResponse
from ..types import MAX_RESOURCES_PER_PAGE, ExtraData, TypeListServerID
from ..utils import (
    get_instructions_choose_resource,
    get_instructions_format_list,
    get_instructions_format_resource_table,
    get_instructions_format_table,
    get_instructions_how_to_monitor_action,
    get_instructions_next_action_suggestion,
    get_web_link_to_environment_resource,
)


class ApplicationService:
    @staticmethod
    async def tool_get_available_language_runtimes(
        ctx: ServerContext,
    ) -> MCPResponse[List[LanguageRuntime]]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.static.get_static_application_options()

        runtimes = response.data.language_runtimes

        return MCPResponse.ok(
            runtimes,
            [
                get_instructions_format_list(
                    "#N. {runtime.name_human_readable}",
                    [
                        "Versions:",
                        "- {version for item in runtime.engine_versions}",
                        "Frameworks:",
                        "- {name_human_readable for item in runtime.frameworks}",
                    ],
                )
            ],
        )

    @staticmethod
    async def tool_list_applications(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        page: int = Field(
            default=1,
            gt=0,
        ),
    ) -> MCPResponse[List[ApplicationSummary]]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.applications.list_environment_applications(
            environment_id,
            page,
            per_page=MAX_RESOURCES_PER_PAGE,
        )

        applications = [
            ApplicationSummary.from_sdk_model(
                application,
                ExtraData(
                    url_web_permalink=get_web_link_to_environment_resource(
                        project_id,
                        environment_id,
                        "application",
                        application.id,
                    ),
                ),
            )
            for application in response.data
        ]

        return MCPResponse.ok(
            applications,
            [
                get_instructions_format_table(
                    [
                        (
                            "ID",
                            "{application.id}",
                        ),
                        (
                            "Name",
                            "[{application.name}]({application.url_web_permalink})",
                        ),
                        (
                            "Repository",
                            "{application.repository}",
                        ),
                        (
                            "Root directory",
                            "{application.root_directory}",
                        ),
                        (
                            "Stack (Language, Version, Framework)",
                            "{application.programming_language} "
                            #
                            "[IF {application.programming_language_version} == 'none'"
                            " THEN `` ELSE {application.programming_language_version}]"
                            #
                            "[IF {application.programming_language_framework} == 'none'"
                            " THEN `` ELSE ({application.programming_language_framework})]",  # noqa: E501
                        ),
                        (
                            "Build command",
                            "{application.build_command} or `-`",
                        ),
                        (
                            "Install dependencies command",
                            "{application.install_dependencies_command} or `-`",
                        ),
                    ]
                ),
                get_instructions_choose_resource("application"),
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_create_application(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        source_credential_id: int,
        name: Annotated[
            str,
            StringConstraints(
                max_length=60,
                pattern=r"^[a-z0-9\.\-\_]+$",
            ),
        ],
        repository: Annotated[
            str,
            StringConstraints(
                max_length=100,
                pattern=r"^[\w.-]+[\/][\w.-]+$",
            ),
            Field(description="Expecting a repository in the format 'owner/repo'."),
        ],
        programming_language: str,
        programming_language_version: str,
        programming_language_framework: str,
        root_directory: Annotated[
            str,
            Field(
                examples=[
                    "`/` for the root directory of the repository.",
                    "`/some/path` for a subdirectory of the repository.",
                ]
            ),
            StringConstraints(
                # Required to start with a slash
                pattern=r"^/.*$",
            ),
        ],
        build_command: Optional[str],
        install_dependencies_command: Optional[str],
        default_branch: str,
        deployments_keep: int = 4,
    ) -> MCPResponse[ApplicationSummary]:
        """
        Rules:
        - The source_credential_id must be of the source provider where the repository
           is hosted. You MUST ensure the user has selected the correct credential
           if user provided the link to the repository. Eg: https://github.com/devopness/devopness
           should use a GitHub credential.
        - If the environment selected by the user does not have a credential of the
           source provider where the repository is hosted, you MUST inform the user
           that they need to create a credential for that source provider in the
           selected environment.
           Please guide the user to access the url
           https://app.devopness.com/projects/<project_id>/environments/<environment_id>/credentials/add
        - Use the `devopness_get_available_language_runtimes` tool help the user to
           select the programming language, version and framework for the new
           application.
        - If the user does not provide an engine version, assume the latest version
           available for the programming language.
        """
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.applications.add_environment_application(
            environment_id,
            {
                "credential_id": source_credential_id,
                "name": name,
                "repository": repository,
                "programming_language": programming_language,
                "engine_version": programming_language_version,
                "framework": programming_language_framework,
                "root_directory": root_directory,
                "build_command": build_command,
                "install_dependencies_command": install_dependencies_command,
                "default_branch": default_branch,
                "deployments_keep": deployments_keep,
            },
        )

        application = ApplicationSummary.from_sdk_model(response.data)

        return MCPResponse.ok(
            application,
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{application.id}",
                        ),
                        (
                            "Name",
                            "[{application.name}]({application.url_web_permalink})",
                        ),
                        (
                            "Repository",
                            "{application.repository}",
                        ),
                        (
                            "Root directory",
                            "{application.root_directory}",
                        ),
                        (
                            "Stack (Language, Version, Framework)",
                            "{application.programming_language} "
                            #
                            "[IF {application.programming_language_version} == 'none'"
                            " THEN `` ELSE {application.programming_language_version}]"
                            #
                            "[IF {application.programming_language_framework} == 'none'"
                            " THEN `` ELSE ({application.programming_language_framework})]",  # noqa: E501
                        ),
                        (
                            "Build command",
                            "{application.build_command} or `-`",
                        ),
                        (
                            "Install dependencies command",
                            "{application.install_dependencies_command} or `-`",
                        ),
                    ]
                ),
                "See more details at: "
                + get_web_link_to_environment_resource(
                    project_id,
                    environment_id,
                    "application",
                    response.data.id,
                ),
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_edit_application(
        ctx: ServerContext,
        application_id: int,
        repository: Annotated[
            Optional[str],
            Field(
                examples=[
                    "`None` to not change the current repository.",
                ],
            ),
        ],
        source_credential_id: Annotated[
            Optional[int],
            Field(
                examples=[
                    "`None` to not change the current used credential.",
                ],
            ),
        ],
        programming_language_version: Annotated[
            Optional[str],
            Field(
                examples=[
                    "`None` to not change the current programming language version.",
                ],
            ),
        ],
        root_directory: Annotated[
            Optional[str],
            Field(
                examples=[
                    "`None` to not change the current root directory."
                    "`/` for the root directory of the repository."
                    "`/some/path` for a subdirectory of the repository.",
                ],
            ),
            StringConstraints(
                # Required to start with a slash
                pattern=r"^/.*$",
            ),
        ],
        build_command: Annotated[
            Optional[str],
            Field(
                examples=[
                    "`None` to not change the current build command.",
                    "`Empty String` to remove the current build command.",
                ],
            ),
        ],
        install_dependencies_command: Annotated[
            Optional[str],
            Field(
                examples=[
                    "`None` to not change the current install dependencies command.",
                    "`Empty String` to remove the current install dependencies command",
                ],
            ),
        ],
    ) -> MCPResponse[ApplicationSummary]:
        await ensure_authenticated(get_credentials(ctx))

        application = (
            await devopness.applications.get_application(application_id)
        ).data

        await devopness.applications.update_application(
            application.id,
            {
                "repository": (
                    application.repository
                    if repository is None  #
                    else repository
                ),
                "credential_id": (
                    application.credential.id  # type: ignore
                    if source_credential_id is None
                    else source_credential_id
                ),
                "engine_version": (
                    application.engine_version
                    if programming_language_version is None
                    else programming_language_version
                ),
                "root_directory": (
                    application.root_directory
                    if root_directory is None
                    else root_directory
                ),
                "build_command": (
                    application.build_command
                    if build_command is None
                    else build_command
                ),
                "install_dependencies_command": (
                    application.install_dependencies_command
                    if install_dependencies_command is None
                    else install_dependencies_command
                ),
                # Application `const` fields
                "id": application.id,
                "name": application.name,
                "programming_language": application.programming_language,
                "framework": application.framework,
                "default_branch": application.default_branch,
                "deployments_keep": application.deployments_keep,
            },
        )

        updated_application = (
            await devopness.applications.get_application(application_id)
        ).data

        return MCPResponse.ok(
            ApplicationSummary.from_sdk_model(updated_application),
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{application.id}",
                        ),
                        (
                            "Name",
                            "[{application.name}]({application.url_web_permalink})",
                        ),
                        (
                            "Repository",
                            "{application.repository}",
                        ),
                        (
                            "Root directory",
                            "{application.root_directory}",
                        ),
                        (
                            "Stack (Language, Version, Framework)",
                            "{application.programming_language} "
                            #
                            "[IF {application.programming_language_version} == 'none'"
                            " THEN `` ELSE {application.programming_language_version}]"
                            #
                            "[IF {application.programming_language_framework} == 'none'"
                            " THEN `` ELSE ({application.programming_language_framework})]",  # noqa: E501
                        ),
                        (
                            "Build command",
                            "{application.build_command} or `-`",
                        ),
                        (
                            "Install dependencies command",
                            "{application.install_dependencies_command} or `-`",
                        ),
                    ]
                ),
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_deploy_application(
        ctx: ServerContext,
        pipeline_id: int,
        source_type: SourceTypePlain,
        source_value: str,
        server_ids: TypeListServerID,
    ) -> MCPResponse[ActionSummary]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.actions.add_pipeline_action(
            pipeline_id,
            {
                "source_type": source_type,
                "source_ref": source_value,
                "servers": server_ids,
            },
        )

        action = ActionSummary.from_sdk_model(response.data)

        return MCPResponse.ok(
            action,
            [
                get_instructions_how_to_monitor_action(action.url_web_permalink),
            ],
        )

    @staticmethod
    async def tool_list_application_variables(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        page: int = Field(
            default=1,
            gt=0,
        ),
    ) -> MCPResponse[List[VariableSummary]]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.variables.list_variables_by_resource_type(
            application_id,
            "application",
            page,
            include_virtual_variables=True,
            variable_target="os-env-var",
        )

        variables = [
            VariableSummary.from_sdk_model(
                variable,
                ExtraData(
                    url_web_permalink=get_web_link_to_environment_resource(
                        project_id,
                        environment_id,
                        "application",
                        application_id,
                    )
                    + f"variables/{variable.id}",
                ),
            )
            for variable in response.data
        ]

        return MCPResponse.ok(
            variables,
            [
                get_instructions_format_table(
                    [
                        (
                            "ID",
                            "IF {variable.id} == 0 THEN `-`ELSE {variable.id}",
                        ),
                        (
                            "Key/Name",
                            "IF {variable.id} == 0"
                            " THEN {variable.key}"
                            " ELSE [{variable.key}]({variable.url_web_permalink})",
                        ),
                        (
                            "Value",
                            "IF {variable.id} == 0 THEN `-`"
                            "ELSE IF {variable.hidden} THEN `🔒 Secret`"
                            "ELSE **{variable.value}**",
                        ),
                        (
                            "Description",
                            "{variable.description} OR `-`",
                        ),
                    ]
                ),
                get_instructions_choose_resource("variable"),  # type: ignore
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_create_application_variable(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        variable_name: Annotated[
            str,
            StringConstraints(
                # Define a POSIX-compliant pattern for environment variable names.
                # See: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap08.html
                pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            ),
        ],
        variable_value: str,
        variable_is_secret: bool = False,
        variable_description: Optional[str] = None,
    ) -> MCPResponse[VariableSummary]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.variables.add_variable(
            application_id,
            "application",
            {
                "key": variable_name,
                "value": variable_value,
                "type": "variable",
                "target": "os-env-var",
                "hidden": variable_is_secret,
                "description": variable_description,
            },
        )

        variable = VariableSummary.from_sdk_model(
            response.data,
            ExtraData(
                url_web_permalink=get_web_link_to_environment_resource(
                    project_id,
                    environment_id,
                    "application",
                    application_id,
                )
                + f"variables/{response.data.id}",
            ),
        )

        return MCPResponse.ok(
            variable,
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{variable.id}",
                        ),
                        (
                            "Key/Name",
                            "[{variable.key}]({variable.url_web_permalink})",
                        ),
                        (
                            "Value",
                            "IF {variable.hidden}"
                            " THEN `🔒 Secret`"
                            " ELSE **{variable.value}**",
                        ),
                        (
                            "Description",
                            "{variable.description} OR `-`",
                        ),
                    ]
                ),
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_edit_application_variable(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        variable_id: int,
        variable_name: Annotated[
            str,
            StringConstraints(
                # Define a POSIX-compliant pattern for environment variable names.
                # See: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap08.html
                pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            ),
        ],
        variable_value: str,
        variable_is_secret: bool = False,
        variable_description: Optional[str] = None,
    ) -> MCPResponse[VariableSummary]:
        await ensure_authenticated(get_credentials(ctx))

        await devopness.variables.update_variable(
            variable_id,
            {
                "id": variable_id,
                "key": variable_name,
                "value": variable_value,
                "type": "variable",
                "target": "os-env-var",
                "hidden": variable_is_secret,
                "description": variable_description,
            },
        )

        response = await devopness.variables.get_variable(variable_id)

        variable = VariableSummary.from_sdk_model(
            response.data,
            ExtraData(
                url_web_permalink=get_web_link_to_environment_resource(
                    project_id,
                    environment_id,
                    "application",
                    application_id,
                )
                + f"variables/{response.data.id}",
            ),
        )

        return MCPResponse.ok(
            variable,
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{variable.id}",
                        ),
                        (
                            "Key/Name",
                            "[{variable.key}]({variable.url_web_permalink})",
                        ),
                        (
                            "Value",
                            "IF {variable.hidden}"
                            " THEN `🔒 Secret`"
                            " ELSE **{variable.value}**",
                        ),
                        (
                            "Description",
                            "{variable.description} OR `-`",
                        ),
                    ]
                ),
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_list_application_config_files(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        page: int = Field(
            default=1,
            gt=0,
        ),
    ) -> MCPResponse[List[VariableSummary]]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.variables.list_variables_by_resource_type(
            application_id,
            "application",
            page,
            include_virtual_variables=False,
            variable_target="resource-config-file",
        )

        config_files = [
            VariableSummary.from_sdk_model(
                config_file,
                ExtraData(
                    application_hide_config_file_content=True,
                    url_web_permalink=get_web_link_to_environment_resource(
                        project_id,
                        environment_id,
                        "application",
                        application_id,
                    )
                    + f"files/{config_file.id}",
                ),
            )  #
            for config_file in response.data
        ]

        return MCPResponse.ok(
            config_files,
            [
                get_instructions_format_table(
                    [
                        (
                            "ID",
                            "{config_file.id}",
                        ),
                        (
                            "Path",
                            "[{config_file.key}]({config_file.url_web_permalink})",
                        ),
                        (
                            "Description",
                            "`{config_file.description}` OR `-`",
                        ),
                    ]
                ),
                get_instructions_choose_resource("config-file"),  # type: ignore
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_get_application_config_file(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        config_file_id: int,
    ) -> MCPResponse[VariableSummary]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.variables.get_variable(config_file_id)

        config_file = VariableSummary.from_sdk_model(
            response.data,
            ExtraData(
                url_web_permalink=get_web_link_to_environment_resource(
                    project_id,
                    environment_id,
                    "application",
                    application_id,
                )
                + f"files/{config_file_id}",
            ),
        )

        return MCPResponse.ok(
            config_file,
            [
                "You MUST present config file details in the below format:",
                "ID: **{config_file.id}**",
                "Path: [{config_file.key}]({config_file.url_web_permalink})",
                "Content:",
                "{config_file.value}",
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_create_application_config_file(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        file_path: Annotated[
            str,
            Field(
                description="The path to the configuration file,"
                "relative to the application directory.",
                examples=[
                    ".env",
                    "config.json",
                    "config/database.yml",
                ],
            ),
        ],
        file_content: str,
        file_description: Optional[str] = None,
    ) -> MCPResponse[VariableSummary]:
        await ensure_authenticated(get_credentials(ctx))

        response = await devopness.variables.add_variable(
            application_id,
            "application",
            {
                "key": file_path,
                "value": file_content,
                "type": "file",
                "target": "resource-config-file",
                "hidden": False,
                "description": file_description,
            },
        )

        config_file = VariableSummary.from_sdk_model(
            response.data,
            ExtraData(
                url_web_permalink=get_web_link_to_environment_resource(
                    project_id,
                    environment_id,
                    "application",
                    application_id,
                )
                + f"files/{response.data.id}",
            ),
        )

        return MCPResponse.ok(
            config_file,
            [
                "You MUST present config file details in the below format:",
                "ID: **{config_file.id}**",
                "Path: [{config_file.key}]({config_file.url_web_permalink})",
                "Content:",
                "{config_file.value}",
                get_instructions_next_action_suggestion("deploy", "application"),
            ],
        )

    @staticmethod
    async def tool_edit_application_config_file(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        application_id: int,
        file_id: int,
        file_path: Annotated[
            str,
            Field(
                description="The path to the configuration file,"
                "relative to the application directory.",
                examples=[
                    ".env",
                    "config.json",
                    "config/database.yml",
                ],
            ),
        ],
        file_content: str,
        file_description: Optional[str] = None,
    ) -> MCPResponse[VariableSummary]:
        await ensure_authenticated(get_credentials(ctx))

        await devopness.variables.update_variable(
            file_id,
            {
                "id": file_id,
                "key": file_path,
                "value": file_content,
                "type": "file",
                "target": "resource-config-file",
                "hidden": False,
                "description": file_description,
            },
        )

        return await ApplicationService.tool_get_application_config_file(
            ctx,
            project_id,
            environment_id,
            application_id,
            file_id,
        )
