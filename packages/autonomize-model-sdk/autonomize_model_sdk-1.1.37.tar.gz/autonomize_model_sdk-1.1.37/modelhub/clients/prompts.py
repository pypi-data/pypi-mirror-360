from typing import List

import httpx
from pydantic import Tag

from modelhub.core import BaseClient, ModelHubAPIException
from modelhub.models.models import (
    Alias,
    SearchModelsCriteria,
    UpdatePromptVersionTagsRequest,
)
from modelhub.models.prompts import (
    EvaluationInput,
    PromptCreation,
    PromptRunTracesDto,
    UpdatePromptVersionRequest,
)

from ..utils import setup_logger

logger = setup_logger(__name__)


class PromptClient(BaseClient):
    """Client for interacting with prompts."""

    def create_prompt(self, prompt: PromptCreation):
        """
        Create a Prompt.
        Args:
            name: str
            template: List[Message]
            commit_message: Optional[str] = Field(default=None)
            version_metadata: Optional[Dict[str, str]] = Field(default=None)
            tags: Optional[Dict[str, str]] = Field(default=None)

        Returns:
            Registered Prompt.
        """
        try:
            endpoint = f"prompts/"
            response = self.post(endpoint, json=prompt)
            logger.debug("prompt created successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    async def acreate_prompt(self, prompt: PromptCreation):
        """
        Create a Prompt.
        Args:
            name: str
            template: List[Message]
            commit_message: Optional[str] = Field(default=None)
            version_metadata: Optional[Dict[str, str]] = Field(default=None)
            tags: Optional[Dict[str, str]] = Field(default=None)

        Returns:
            Registered Prompt.
        """
        try:
            endpoint = f"prompts/"
            response = await self.apost(endpoint, json=prompt)
            logger.debug("prompt created successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def get_prompts(
        self,
        criteria: SearchModelsCriteria,
    ):
        """
        Get all prompts.

        Args:
            criteria (SearchModelsCriteria): filtering criteria.

        Returns:
            List[Dict[str, Any]]: A list of all prompts.

        Raises:
            HTTPException: If an error occurs while fetching the prompts.
        """
        try:
            endpoint = f"prompts/search"
            response = self.post(endpoint, json=criteria)
            logger.debug("get prompts successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    async def aget_prompts(
        self,
        criteria: SearchModelsCriteria,
    ):
        """
        Get all prompts.

        Args:
            criteria (SearchModelsCriteria): filtering criteria.

        Returns:
            List[Dict[str, Any]]: A list of all prompts.

        Raises:
            HTTPException: If an error occurs while fetching the prompts.
        """
        try:
            endpoint = f"prompts/search"
            response = await self.apost(endpoint, json=criteria)
            logger.debug("get prompts successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def get_prompt_versions(self):
        """
        Get all prompt versions.

        Returns:
            List[Dict[str, Any]]: A list of all prompt versions.

        Raises:
            HTTPException: If an error occurs while fetching the prompt versions.
        """
        try:
            endpoint = f"prompts/versions/search"
            response = self.get(endpoint,)
            logger.debug("get prompt versions successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt versions: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def aget_prompt_versions(self):
        """
        Get all prompt versions.

        Returns:
            List[Dict[str, Any]]: A list of all prompt versions.

        Raises:
            HTTPException: If an error occurs while fetching the prompt versions.
        """
        try:
            endpoint = f"prompts/versions/search"
            response = await self.aget(endpoint)
            logger.debug("get prompt versions successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt versions: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def get_prompt_versions_with_name(
        self,
        prompt_name: str,
    ):
        """
        Get all prompt versions.

        Args:
          prompt_name (str):

        Returns:
            List[Dict[str, Any]]: A list of all prompt versions.

        Raises:
            HTTPException: If an error occurs while fetching the prompt versions.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/search"
            response = self.get(endpoint)
            logger.debug("get prompt versions successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt versions: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def aget_prompt_versions_with_name(
        self,
        prompt_name: str,
    ):
        """
        Get all prompt versions.

        Args:
          prompt_name (str):

        Returns:
            List[Dict[str, Any]]: A list of all prompt versions.

        Raises:
            HTTPException: If an error occurs while fetching the prompt versions.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/search"
            response = await self.aget(endpoint)
            logger.debug("get prompt versions successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt versions: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        


    def get_registered_prompt_by_name(self, name: str):
        """
        Get a registered prompt by name.

        Args:
            name (str): The name of the prompt.

        Returns:
            Dict[str, Any]: The registered prompt.

        Raises:
            HTTPException: If an error occurs while fetching the prompt.
        """
        try:
            endpoint = f"prompts/{name}"
            response = self.get(endpoint)
            logger.debug("get prompt successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def aget_registered_prompt_by_name(self, name: str):
        """
        Get a registered prompt by name.

        Args:
            name (str): The name of the prompt.

        Returns:
            Dict[str, Any]: The registered prompt.

        Raises:
            HTTPException: If an error occurs while fetching the prompt.
        """
        try:
            endpoint = f"prompts/{name}"
            response = await self.aget(endpoint)
            logger.debug("get prompt successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        

    def delete_prompt(self, prompt_name: str):
        """
        Delete an prompt by name.

        Args:
            prompt_name (str): The name of the prompt.

        Returns:
            Dict[str, str]: A message indicating the result of the deletion.

        Raises:
            HTTPException: If an error occurs while deleting the prompt.
        """
        try:
            endpoint = f"prompts/{prompt_name}"
            response = self.delete(endpoint)
            logger.debug("delete prompt successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    
    async def adelete_prompt(self, prompt_name: str):
        """
        Delete an prompt by name.

        Args:
            prompt_name (str): The name of the prompt.

        Returns:
            Dict[str, str]: A message indicating the result of the deletion.

        Raises:
            HTTPException: If an error occurs while deleting the prompt.
        """
        try:
            endpoint = f"prompts/{prompt_name}"
            response = await self.adelete(endpoint)
            logger.debug("delete prompt successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        

    def create_prompt_version(
        self,
        prompt_name: str,
        prompt: UpdatePromptVersionRequest,
    ):
        """
        Create a version of a prompt.

        Args:
            prompt_name (str): The name of the prompt.

        Returns:
            Dict[str, Any]: The created prompt version.

        Raises:
            HTTPException: If an error occurs during version creation.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions"
            response = self.post(endpoint, json=prompt)
            logger.debug("create prompt version successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt version: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    async def acreate_prompt_version(
        self,
        prompt_name: str,
        prompt: UpdatePromptVersionRequest,
    ):
        """
        Create a version of a prompt.

        Args:
            prompt_name (str): The name of the prompt.

        Returns:
            Dict[str, Any]: The created prompt version.

        Raises:
            HTTPException: If an error occurs during version creation.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions"
            response = await self.apost(endpoint, json=prompt)
            logger.debug("create prompt version successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt version: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def create_tag(
        self,
        prompt_name: str,
        tag: Tag,
    ):
        """
        Create a tag for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            tag (Tag): The tag to create.

        Returns:
            Dict[str, str]: A message confirming the creation.

        Raises:
            HTTPException: If an error occurs during tag creation.
        """
        try:
            endpoint = f"prompts/{prompt_name}/tags"
            response = self.post(endpoint, json=tag)
            logger.debug("create prompt tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    
    async def acreate_tag(
        self,
        prompt_name: str,
        tag: Tag,
    ):
        """
        Create a tag for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            tag (Tag): The tag to create.

        Returns:
            Dict[str, str]: A message confirming the creation.

        Raises:
            HTTPException: If an error occurs during tag creation.
        """
        try:
            endpoint = f"prompts/{prompt_name}/tags"
            response = await self.apost(endpoint, json=tag)
            logger.debug("create prompt tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def get_registered_prompt_version(self, name: str, version: int):
        """
        Get a registered prompt specific version.

        Args:
            name (str): The name of the prompt.
            version (int): The version of Prompt, if no version is specified it gives the latest version

        Returns:
            Dict[str, Any]: The registered prompt.

        Raises:
            HTTPException: If an error occurs while fetching the prompt.
        """
        try:
            endpoint = f"prompts/{name}/versions/{version}"
            response = self.get(endpoint)
            logger.debug("create prompt version successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt version: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def aget_registered_prompt_version(self, name: str, version: int):
        """
        Get a registered prompt specific version.

        Args:
            name (str): The name of the prompt.
            version (int): The version of Prompt, if no version is specified it gives the latest version

        Returns:
            Dict[str, Any]: The registered prompt.

        Raises:
            HTTPException: If an error occurs while fetching the prompt.
        """
        try:
            endpoint = f"prompts/{name}/versions/{version}"
            response = await self.aget(endpoint)
            logger.debug("create prompt version successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error getting prompt version: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def update_prompt_version_tag(
        self, prompt_name: str, version: str, version_metadata: List[Tag]
    ):
        """
        Update  tag for a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version.
            tag (Tag): The tag to update or add.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during tag deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}/tags"
            response = self.put(
                endpoint, json=version_metadata
            )
            logger.debug(" prompt version tag updated successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"error updating prompt version tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def aupdate_prompt_version_tag(
        self, prompt_name: str, version: str, version_metadata: List[Tag]
    ):
        """
        Update  tag for a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version.
            tag (Tag): The tag to update or add.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during tag deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}/tags"
            response = await self.aput(
                endpoint, json=version_metadata
            )
            logger.debug(" prompt version tag updated successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"error updating prompt version tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e


    def delete_prompt_version_tag(
        self, prompt_name: str, version: str, tag_key: str
    ):
        """
        Delete a tag for a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version.
            tag_key (str): The tag key to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during tag deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}/tags/{tag_key}"
            response = self.delete(endpoint)
            logger.debug("delete prompt version tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt version tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    async def adelete_prompt_version_tag(
        self, prompt_name: str, version: str, tag_key: str
    ):
        """
        Delete a tag for a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version.
            tag_key (str): The tag key to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during tag deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}/tags/{tag_key}"
            response = await self.adelete(endpoint)
            logger.debug("delete prompt version tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt version tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def delete_tag(self, prompt_name: str, tag_key: str):
        """
        Delete a tag for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            tag_key (str): The tag key to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during tag deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/tags/{tag_key}"
            response = self.delete(endpoint)
            logger.debug("delete prompt tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    async def adelete_tag(self, prompt_name: str, tag_key: str):
        """
        Delete a tag for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            tag_key (str): The tag key to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during tag deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/tags/{tag_key}"
            response = await self.adelete(endpoint)
            logger.debug("delete prompt tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def create_alias(
        self,
        prompt_name: str,
        alias: Alias,
    ):
        """
        Create an alias for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            alias (Alias): The alias data.

        Returns:
            Dict[str, str]: A message confirming the creation.

        Raises:
            HTTPException: If an error occurs during alias creation.
        """
        try:
            endpoint = f"prompts/{prompt_name}/aliases"
            response = self.post(endpoint, json=alias)
            logger.debug("create prompt alias successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt alias: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def acreate_alias(
        self,
        prompt_name: str,
        alias: Alias,
    ):
        """
        Create an alias for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            alias (Alias): The alias data.

        Returns:
            Dict[str, str]: A message confirming the creation.

        Raises:
            HTTPException: If an error occurs during alias creation.
        """
        try:
            endpoint = f"prompts/{prompt_name}/aliases"
            response = await self.apost(endpoint, json=alias)
            logger.debug("create prompt alias successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error creating prompt alias: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        


    def delete_alias(
        self,
        prompt_name: str,
        alias_name: str,
    ):
        """
        Delete an alias for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            alias_name (str): The alias to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during alias deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/aliases/{alias_name}"
            response = self.delete(endpoint)
            logger.debug("delete prompt tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def adelete_alias(
        self,
        prompt_name: str,
        alias_name: str,
    ):
        """
        Delete an alias for a prompt.

        Args:
            prompt_name (str): The name of the prompt.
            alias_name (str): The alias to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during alias deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/aliases/{alias_name}"
            response = await self.adelete(endpoint)
            logger.debug("delete prompt tag successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt tag: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def delete_prompt_version(self, prompt_name: str, version: int):
        """
        Delete a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during version deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}"
            response = self.delete(endpoint)
            logger.debug("delete prompt version successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt version: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    async def adelete_prompt_version(self, prompt_name: str, version: int):
        """
        Delete a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version to delete.

        Returns:
            Dict[str, str]: A message confirming the deletion.

        Raises:
            HTTPException: If an error occurs during version deletion.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}"
            response = await self.adelete(endpoint)
            logger.debug("delete prompt version successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error deleting prompt version: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    def update_prompt_version_tags(
        self,
        prompt_name: str,
        version: str,
        tags_request: UpdatePromptVersionTagsRequest,
    ):
        """
        Update tags for a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version to update.
            tags_request (UpdateTagsRequest): The tags to update.

        Returns:
            Dict[str, str]: A message confirming the update.

        Raises:
            HTTPException: If an error occurs during tag update.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}/tags"
            response = self.put(endpoint, json=tags_request)
            logger.debug("update prompt version tags successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error updating prompt version tags: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    async def aupdate_prompt_version_tags(
        self,
        prompt_name: str,
        version: str,
        tags_request: UpdatePromptVersionTagsRequest,
    ):
        """
        Update tags for a prompt version.

        Args:
            prompt_name (str): The name of the prompt.
            version (str): The version to update.
            tags_request (UpdateTagsRequest): The tags to update.

        Returns:
            Dict[str, str]: A message confirming the update.

        Raises:
            HTTPException: If an error occurs during tag update.
        """
        try:
            endpoint = f"prompts/{prompt_name}/versions/{version}/tags"
            response = await self.aput(endpoint, json=tags_request)
            logger.debug("update prompt version tags successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error updating prompt version tags: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def evaluate_prompt(self, data: EvaluationInput):
        """
        Evaluate a prompt version with given inputs and targets.

        Parameters:
        - inputs: List of input texts
        - targets: List of target summaries
        - prompt_version: Version number of the prompt to evaluate
        - model: Model to use for evaluation (default: gpt-3.5-turbo)
        - temperature: Temperature setting for model (default: 0.1)
        - experiment_name: Name of MLflow experiment (default: prompts-evaluation)

        Returns:
        - Evaluation metrics and a sample prediction
        """
        try:
            endpoint = f"prompts/evaluate-prompt"
            response = self.post(endpoint, json=data)
            logger.debug("prompt evaluation successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error evaluating prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
    
    async def aevaluate_prompt(self, data: EvaluationInput):
        """
        Evaluate a prompt version with given inputs and targets.

        Parameters:
        - inputs: List of input texts
        - targets: List of target summaries
        - prompt_version: Version number of the prompt to evaluate
        - model: Model to use for evaluation (default: gpt-3.5-turbo)
        - temperature: Temperature setting for model (default: 0.1)
        - experiment_name: Name of MLflow experiment (default: prompts-evaluation)

        Returns:
        - Evaluation metrics and a sample prediction
        """
        try:
            endpoint = f"prompts/evaluate-prompt"
            response = await self.apost(endpoint, json=data)
            logger.debug("prompt evaluation successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error evaluating prompt: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def get_traces(self, data: PromptRunTracesDto):
        """
        Endpoint to retrieve traces for a given prompt run traces.
        """
        try:
            endpoint = f"prompts/get-traces"
            response = self.post(endpoint, json=data)
            logger.debug("get traces successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error in getting traces: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        
    async def aget_traces(self, data: PromptRunTracesDto):
        """
        Endpoint to retrieve traces for a given prompt run traces.
        """
        try:
            endpoint = f"prompts/get-traces"
            response = await self.apost(endpoint, json=data)
            logger.debug("get traces successfull")
            return response
        except httpx.RequestError as e:
            error_msg = f"error in getting traces: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
