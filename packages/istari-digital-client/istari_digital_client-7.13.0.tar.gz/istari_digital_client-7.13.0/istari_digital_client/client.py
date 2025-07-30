from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Union, TypeAlias, Optional, Iterable

from pydantic import StrictStr

from .api.client_api import ClientApi
from .api_client import ApiClient
from .configuration import Configuration, ConfigurationError
from .models.artifact import Artifact
from .models.comment import Comment
from .models.control_tag import ControlTag
from .models.control_tagging_object_type import ControlTaggingObjectType
from .models.file import File
from .models.function_auth_secret import FunctionAuthSecret
from .models.function_auth_type import FunctionAuthType
from .models.job import Job
from .models.model import Model
from .models.new_function_auth_secret import NewFunctionAuthSecret
from .models.new_source import NewSource
from .models.patch_op import PatchOp
from .models.resource_control_tagging import ResourceControlTagging
from .models.user import User
from .models.user_control_tagging import UserControlTagging
from .models.token import Token

logger = logging.getLogger("istari-digital-client.client")

PathLike = Union[str, os.PathLike, Path]
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class Client(ClientApi):
    """Create a new instance of the Istari client

    Args:
        config (Configuration | None): The configuration for the client
    """

    def __init__(
        self,
        config: Configuration | None = None,
    ) -> None:
        config = config or Configuration()

        if not config.registry_url:
            raise ConfigurationError(
                "Registry URL is not set! It must be specified either via an ISTART_REGISTRY_URL env variable or by "
                "explicitly setting the registry_url attribute in the (optional) config object on client initialization"
            )
        if not config.registry_auth_token:
            raise ConfigurationError(
                "Registry auth token is not set! It must be specified either via an ISTARI_REGISTRY_AUTH_TOKEN env "
                "variable or by explicitly setting the registry_auth_token attribute in the (optional) config object "
                "on client initialization"
            )

        self.configuration: Configuration = config

        self._api_client = ApiClient(config)

        super().__init__(self.configuration, self._api_client)

    def __del__(self):
        if (
            self.configuration.filesystem_cache_enabled
            and self.configuration.filesystem_cache_clean_on_exit
            and self.configuration.filesystem_cache_root.exists()
            and self.configuration.filesystem_cache_root.is_dir()
        ):
            logger.debug("Cleaning up cache contents for client exit")
            for child in self.configuration.filesystem_cache_root.iterdir():
                if child.is_dir():
                    logger.debug("deleting cache directory - %s", child)
                    shutil.rmtree(
                        self.configuration.filesystem_cache_root, ignore_errors=True
                    )
                elif child.is_file() and not child.is_symlink():
                    logger.debug("deleting cache file - %s", child)
                    child.unlink(missing_ok=True)
                else:
                    logger.debug(
                        "not deleting cache item (is neither a directory nor a regular file) -  %s",
                        child,
                    )

    def add_artifact(
        self,
        model_id: str,
        path: PathLike,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Artifact:
        """Add an artifact

        :param model_id: The model ID to get (required)
        :type model_id: str
        :param path: The path to the artifact (required)
        :type path: PathLike
        :param sources: The sources of the artifact (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the artifact (optional)
        :type description: str | None
        :param version_name: The version name of the artifact (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the artifact (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the artifact (optional)
        :type display_name: str | None

        """
        file_revision = self.create_revision(
            file_path=path,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return self._create_artifact(
            model_id=model_id,
            file_revision=file_revision,
        )

    def update_artifact(
        self,
        artifact_id: str,
        path: PathLike,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Artifact:
        salt = self.get_artifact(artifact_id=artifact_id).revision.content_token.salt

        file_revision = self.update_revision_content(
            file_path=path,
            salt=salt,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return self._update_artifact(
            artifact_id=artifact_id,
            file_revision=file_revision,
        )

    def add_comment(
        self,
        resource_id: str,
        path: PathLike,
        description: str | None = None,
    ) -> Comment:
        """Add a comment to a resource

        :param resource_id: The resource to add the comment to (required)
        :type resource_id: str
        :param path: The path to the comment (required)
        :type path: PathLike
        :param description: The description of the comment (optional)
        :type description: str | None

        """
        file_revision = self.create_revision(
            file_path=path,
            sources=None,
            display_name=None,
            description=description,
            version_name=None,
            external_identifier=None,
        )

        return self._create_comment(
            resource_id=resource_id,
            file_revision=file_revision,
        )

    def update_comment(
        self,
        comment_id: str,
        path: PathLike,
        description: str | None = None,
    ) -> Comment:
        """Update a comment

        :param comment_id: The comment to update (required)
        :type comment_id: str
        :param path: The path to the comment (required)
        :type path: PathLike
        :param description: The description of the comment (optional)
        :type description: str | None

        """

        salt = self.get_comment(comment_id=comment_id).revision.content_token.salt

        file_revision = self.update_revision_content(
            file_path=path,
            salt=salt,
            sources=None,
            display_name=None,
            description=description,
            version_name=None,
            external_identifier=None,
        )

        return self._update_comment(
            comment_id=comment_id,
            file_revision=file_revision,
        )

    def add_file(
        self,
        path: PathLike,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> File:
        """Add a file

        :param path: The path to the file (required)
        :type path:  PathLike
        :param sources: The sources of the file (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the file (optional)
        :type description: str | None
        :param version_name: The version name of the file (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the file (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the file (optional)
        :type display_name: str | None

        """
        file_revision = self.create_revision(
            file_path=path,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return self._create_file(
            file_revision=file_revision,
        )

    def update_file(
        self,
        file_id: str,
        path: PathLike | str,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> File:
        """Update a file

        :param file_id: The file to update (required)
        :type file_id: str
        :param path: The path to the file (required)
        :type path: PathLike | str
        :param sources: The sources of the file (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the file (optional)
        :type description: str | None
        :param version_name: The version name of the file (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the file (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the file (optional)
        :type display_name: str | None

        """
        salt = self.get_file(file_id=file_id).revision.content_token.salt

        file_revision = self.update_revision_content(
            file_path=path,
            salt=salt,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return self._update_file(
            file_id=file_id,
            file_revision=file_revision,
        )

    def update_file_properties(
        self,
        file: File,
        display_name: str | None = None,
        description: str | None = None,
        external_identifier: str | None = None,
        version_name: str | None = None,
    ) -> File:
        """Update file properties

        :param file: The file to update (required)
        :type file: File
        :param display_name: The display name of the file (optional)
        :type display_name: str | None
        :param description: The description of the file (optional)
        :type description: str | None

        """
        return self.update_revision_properties(
            file_revision=file.revision,
            display_name=display_name,
            description=description,
            external_identifier=external_identifier,
            version_name=version_name,
        )

    def add_job(
        self,
        model_id: str,
        function: str,
        *,
        parameters: JSON | None = None,
        parameters_file: PathLike | None = None,
        tool_name: str | None = None,
        tool_version: str | None = None,
        operating_system: str | None = None,
        assigned_agent_id: str | None = None,
        agent_identifier: str | None = None,
        sources: list[NewSource | str] | None = None,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
        **kwargs,
    ) -> "Job":
        """Add a job

        :param model_id: The model to add the job to (required)
        :type model_id:  str
        :param function: The function of the job (required)
        :type function: str
        :param parameters: The parameters of the job (optional)
        :type parameters: JSON | None
        :param parameters_file: The path to the parameters file (optional)
        :type parameters_file: PathLike | None
        :param tool_name: The name of the tool (optional)
        :type tool_name: str | None
        :param tool_version: The version of the tool (optional)
        :type tool_version: str | None
        :param operating_system: The operating system of the agent (optional)
        :type operating_system: str | None
        :param assigned_agent_id: The agent id for the agent assigned to execute the job (optional)
        :type assigned_agent_id: str | None
        :param agent_identifier: The agent identifier for the agent that created the job (optional)
        :type agent_identifier: str | None
        :param sources: The sources of the job (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the job (optional)
        :type description: str | None
        :param version_name: The version name of the job (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the job (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the job (optional)
        :type display_name: str | None

        """
        parameters_file_is_temp = False
        if parameters_file and (parameters or kwargs):
            raise ValueError(
                "Can't combine a parameters file with explicit parameters or parameter kwargs"
            )
        if not parameters_file:
            if parameters and kwargs:
                raise ValueError(
                    "Can't combine explicit parameters with parameters kwargs"
                )
            parameters = parameters or kwargs
            parameters_file = Path(
                tempfile.NamedTemporaryFile(
                    prefix="parameters", suffix=".json", delete=False
                ).name
            )
            parameters_file.write_text(json.dumps(parameters, indent=4))
            parameters_file_is_temp = True
        parameters_file = Path(parameters_file)
        try:
            file_revision = self.create_revision(
                file_path=str(parameters_file),
                sources=sources,
                display_name=display_name,
                description=description,
                version_name=version_name,
                external_identifier=external_identifier,
            )

            openapi_job = self._create_model_job(
                model_id=model_id,
                function_name=function,
                file_revision=file_revision,
                tool_name=tool_name,
                tool_version=tool_version,
                operating_system=operating_system,
                assigned_agent_id=assigned_agent_id,
                agent_identifier=agent_identifier,
            )
        finally:
            if parameters_file_is_temp:
                if parameters_file.exists():
                    parameters_file.unlink(missing_ok=True)

        return openapi_job

    def update_job(
        self,
        job_id: str,
        path: PathLike,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Job:
        """Update a job

        :param job_id: The job to update (required)
        :type job_id: str
        :param path: The path to the job (required)
        :type path: PathLike
        :param sources: The sources of the job (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the job (optional)
        :type description: str | None
        :param version_name: The version name of the job (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the job (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the job (optional)
        :type display_name: str | None

        """
        salt = self.get_job(job_id=job_id).revision.content_token.salt

        file_revision = self.update_revision_content(
            file_path=path,
            salt=salt,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return self._update_job(
            job_id=job_id,
            file_revision=file_revision,
        )

    def add_model(
        self,
        path: PathLike,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Model:
        """Add a model

        :param path: The path to the model (required)
        :type path: PathLike
        :param sources: The sources of the model (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the model (optional)
        :type description: str | None
        :param version_name: The version name of the model (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the model (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the model (optional)
        :type display_name: str | None

        """
        file_revision = self.create_revision(
            file_path=path,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )
        return self._create_model(
            file_revision=file_revision,
        )

    def update_model(
        self,
        model_id: str,
        path: PathLike,
        sources: list[NewSource | str] | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Model:
        """Update a model

        :param model_id: The model to update (required)
        :type model_id: str
        :param path: The path to the model (required)
        :type path: PathLike
        :param sources: The sources of the model (optional)
        :type sources: List[NewSource | str] | None
        :param description: The description of the model (optional)
        :type description: str | None
        :param version_name: The version name of the model (optional)
        :type version_name: str | None
        :param external_identifier: The external identifier of the model (optional)
        :type external_identifier: str | None
        :param display_name: The display name of the model (optional)
        :type display_name: str | None

        """
        salt = self.get_model(model_id=model_id).revision.content_token.salt

        file_revision = self.update_revision_content(
            file_path=path,
            salt=salt,
            sources=sources,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return self._update_model(
            model_id=model_id,
            file_revision=file_revision,
        )

    def add_function_auth_secret(
        self,
        auth_provider_name: str,
        function_auth_type: FunctionAuthType,
        path: PathLike,
        expiration: Optional[datetime] = None,
    ) -> FunctionAuthSecret:
        """This method creates a new function auth secret from a file.

        :param auth_provider_name: The name of the auth provider (required)
        :type auth_provider_name: str
        :param function_auth_type: The type of the function auth secret (required)
        :type function_auth_type: FunctionAuthType
        :param path: The path to the file containing the secret (required)
        :type path: PathLike
        :param expiration: The expiration date of the secret (optional)
        :type expiration: Optional[datetime]

        """

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        file_revision = self.create_secret_revision(
            file_path=path,
        )

        # Generate content token for the secret
        # This is a different process than the file revision
        # because the secret is encrypted and we need to
        # generate a token for the plain secret content
        with open(path, "rb") as f:
            secret_content = f.read()
            token: Token = Token.from_bytes(secret_content)

        secret = NewFunctionAuthSecret(
            auth_provider_name=auth_provider_name,
            revision=file_revision,
            function_auth_type=function_auth_type,
            expiration=expiration,
            sha=token.sha,
            salt=token.salt,
        )

        return self._create_function_auth_secret(secret)

    def add_user_control_taggings(
        self,
        user_id: StrictStr,
        control_tag_ids: Iterable[StrictStr],
        reason: Optional[StrictStr] = None,
    ) -> list[UserControlTagging]:
        """Assign one or more control tags to a model. The list resource control taggings returned may be more than the number of control tags assigned,
        as when a tag is applied to a model, the tagging is applied to each of its child artifacts as well. The calling user must be a customer admin on the
        tenant the target user is a member of or the operation will fail with a permission denied error.

        :param user_id: The id of the user to assign control tag access to.
        :type user_id: str
        :param control_tag_ids:  The ids of the control tags to assign access to.
        :type control_tag_ids: Iterable[str]
        :param reason: The reason for the assignment (optional)
        :type reason: Optional[str]

        """

        return self.patch_user_control_taggings(
            user_id, list(control_tag_ids), patch_op=PatchOp.SET, reason=reason
        )

    def remove_user_control_taggings(
        self,
        user_id: StrictStr,
        control_tag_ids: Iterable[StrictStr],
        reason: Optional[StrictStr] = None,
    ) -> list[UserControlTagging]:
        """Remove (archive) one or more control tag access assignments from a user. The calling user must be a customer
        admin on the tenant the target user is a member of or the operation will fail with a permission denied error.

        :param user_id: The id of the user to remove control tag access from.
        :type user_id: str
        :param control_tag_ids:  The ids of the control tags to remove access assignments from.
        :type control_tag_ids: Iterable[str]
        :param reason: The reason for the assignment (optional)
        :type reason: Optional[str]

        """

        return self.patch_user_control_taggings(
            user_id, list(control_tag_ids), patch_op=PatchOp.DELETE, reason=reason
        )

    def add_model_control_taggings(
        self,
        model_id: StrictStr,
        control_tag_ids: Iterable[StrictStr],
        reason: Optional[StrictStr] = None,
    ) -> list[ResourceControlTagging]:
        """Assign one or more control tags to a model. The list resource control taggings returned may be more than the number of control tags assigned,
        as when a tag is applied to a model, the tagging is applied to each of its child artifacts as well. Owner or administrator access to the model
        is required to modify control tag assignments.

        :param model_id: The id of the model to assign the control tag to.
        :type model_id: str
        :param control_tag_ids:  The ids of the control tags to assign.
        :type control_tag_ids: Iterable[str]
        :param reason: The reason for the assignment (optional)
        :type reason: Optional[str]

        """

        return self.patch_model_control_taggings(
            model_id, list(control_tag_ids), patch_op=PatchOp.SET, reason=reason
        )

    def remove_model_control_taggings(
        self,
        model_id: StrictStr,
        control_tag_ids: Iterable[StrictStr],
        reason: Optional[StrictStr] = None,
    ) -> list[ResourceControlTagging]:
        """Remove (archive) one or more control tag assignments from a model. Owner or administrator access to the model its parent model is required to modify control tag
        assignments.

        :param model_id: The id of the model to remove the control tag assignment from (required)
        :type model_id: str
        :param control_tag_ids:  The ids of the control tags to assign (required)
        :type control_tag_ids: Iterable[str]
        :param reason: The reason for the assignment (optional)

        """

        return self.patch_model_control_taggings(
            model_id, list(control_tag_ids), patch_op=PatchOp.DELETE, reason=reason
        )

    def add_artifact_control_taggings(
        self,
        artifact_id: StrictStr,
        control_tag_ids: Iterable[StrictStr],
        reason: Optional[StrictStr] = None,
    ) -> list[ResourceControlTagging]:
        """Assign one or more control tags to an artifact. Owner or administrator access to the artifacts parent model is required to modify control tag
        assignments.

        :param artifact_id: The id of the artifact to assign the control tag to (required)
        :type artifact_id: str
        :param control_tag_ids:  The ids of the control tags to assign (required)
        :type control_tag_ids: Iterable[str]
        :param reason: The reason for the assignment (optional)
        :type reason: Optional[str]

        """

        return self.patch_artifact_control_taggings(
            artifact_id, list(control_tag_ids), patch_op=PatchOp.SET, reason=reason
        )

    def remove_artifact_control_taggings(
        self,
        artifact_id: StrictStr,
        control_tag_ids: Iterable[StrictStr],
        reason: Optional[StrictStr] = None,
    ) -> list[ResourceControlTagging]:
        """Archive one or more control taggings on a model. Owner or administrator access to the artifacts parent model is required to modify control tag
        assignments.

        :param artifact_id: The id of the artifact to remove the control tag assignment from (required)
        :type artifact_id: str
        :param control_tag_ids:  The ids of the control tags to assign (required)
        :type control_tag_ids: Iterable[str]
        :param reason: The reason for the assignment (optional)
        :type reason: Optional[str]

        """

        return self.patch_artifact_control_taggings(
            artifact_id, list(control_tag_ids), patch_op=PatchOp.DELETE, reason=reason
        )

    def get_model_control_tags(self, model_id: StrictStr) -> list[ControlTag]:
        """Get list of control tags for the active control taggings on a model.

        :param model_id: The id of the model to get the assigned control tags for (required)
        :type model_id: str

        """

        return self.get_object_control_tags(ControlTaggingObjectType.MODEL, model_id)

    def get_artifact_control_tags(self, artifact_id: StrictStr) -> list[ControlTag]:
        """Get list of control tags for the active control taggings on a model.

        :param artifact_id: The id of the artifact to get the assigned control tags for (required)
        :type artifact_id: str

        """

        return self.get_object_control_tags(
            ControlTaggingObjectType.ARTIFACT, artifact_id
        )

    def get_user_control_tags(self, user_id: StrictStr) -> list[ControlTag]:
        """Get list of control tags a user has been assigned access to.

        :param user_id: The id of the user to get the assigned control tags for (required)
        :type user_id: str

        """

        return self.get_object_control_tags(ControlTaggingObjectType.USER, user_id)

    def get_user(self, user_id: StrictStr) -> User:
        """Get a user from the registry. This method simply a convenience wrapper for "get_user_by_id" added for
        "get" method naming convention consistency (get_model, get_artifact, etc...)

        :param user_id: The id of the user to get (required)
        :type user_id: str

        """

        return self.get_user_by_id(user_id)
