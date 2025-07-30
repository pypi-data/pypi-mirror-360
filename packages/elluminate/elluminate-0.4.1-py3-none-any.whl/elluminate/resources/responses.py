from typing import List, overload

from loguru import logger
from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionMessageParam

from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    BatchCreatePromptResponseRequest,
    BatchCreatePromptResponseStatus,
    CreatePromptResponseRequest,
    Experiment,
    GenerationMetadata,
    LLMConfig,
    PromptResponse,
    PromptResponseFilter,
    PromptTemplate,
    ResponsesSample,
    ResponsesSampleFilter,
    ResponsesSampleSortBy,
    ResponsesStats,
    TemplateVariables,
)
from elluminate.schemas.template_variables_collection import TemplateVariablesCollection
from elluminate.utils import retry_request, run_async


class ResponsesResource(BaseResource):
    async def alist(
        self,
        prompt_template: PromptTemplate | None = None,
        template_variables: TemplateVariables | None = None,
        experiment: Experiment | None = None,
        collection: TemplateVariablesCollection | None = None,
        filters: PromptResponseFilter | None = None,
    ) -> list[PromptResponse]:
        """Async version of list."""
        filters = filters or PromptResponseFilter()
        if prompt_template:
            filters.prompt_template_id = prompt_template.id
        if template_variables:
            filters.template_variables_id = template_variables.id
        if experiment:
            filters.experiment_id = experiment.id
        if collection:
            filters.collection_id = collection.id
        params = filters.model_dump(exclude_none=True)

        return await self._paginate(
            path="responses",
            model=PromptResponse,
            params=params,
            resource_name="Responses",
        )

    def list(
        self,
        prompt_template: PromptTemplate | None = None,
        template_variables: TemplateVariables | None = None,
        experiment: Experiment | None = None,
        collection: TemplateVariablesCollection | None = None,
        filters: PromptResponseFilter | None = None,
    ) -> list[PromptResponse]:
        """Returns the responses belonging to a prompt template, a template variables, or both.

        Args:
            prompt_template (PromptTemplate | None): The prompt template to get responses for.
            template_variables (TemplateVariables | None): The template variables to get responses for.
            experiment (Experiment | None): The experiment to get responses for.
            collection (TemplateVariablesCollection | None): The collection to get responses for.
            filters (PromptResponseFilter | None): The filters to apply to the responses.

        Returns:
            list[PromptResponse]: The list of prompt responses.

        """
        return run_async(self.alist)(
            prompt_template=prompt_template,
            template_variables=template_variables,
            experiment=experiment,
            collection=collection,
            filters=filters,
        )

    async def alist_samples(
        self,
        experiment: Experiment,
        exclude_perfect_responses: bool = False,
        filters: ResponsesSampleFilter | None = None,
        sort_by: ResponsesSampleSortBy | None = None,
    ) -> List[ResponsesSample]:
        """Async version of list_samples."""
        filters = filters or ResponsesSampleFilter(
            experiment_id=experiment.id,
        )
        params = filters.model_dump(exclude_none=True)

        if exclude_perfect_responses:
            params["exclude_perfect_responses"] = True

        if sort_by:
            params["sort_by"] = sort_by.value

        response = await self._aget("responses/samples", params=params)
        return [ResponsesSample.model_validate(item) for item in response.json()]

    def list_samples(
        self,
        experiment: Experiment,
        exclude_perfect_responses: bool = False,
        filters: ResponsesSampleFilter | None = None,
        sort_by: ResponsesSampleSortBy | None = None,
    ) -> List[ResponsesSample]:
        """List samples for an experiment.

        Args:
            experiment (Experiment): The experiment to get samples for.
            exclude_perfect_responses (bool): Whether to exclude perfect responses.
            filters (ResponsesSampleFilter | None): The filters to apply to the samples.
            sort_by (ResponsesSampleSortBy | None): The sort order for the samples.

        Returns:
            List[ResponsesSample]: The list of samples.

        """
        filters = filters or ResponsesSampleFilter(
            experiment_id=experiment.id,
        )

        return run_async(self.alist_samples)(
            experiment=experiment,
            exclude_perfect_responses=exclude_perfect_responses,
            filters=filters,
            sort_by=sort_by,
        )

    async def aget_stats(
        self,
        llm_config: LLMConfig | None = None,
        days: int = 30,
    ) -> ResponsesStats:
        """Async version of get_stats."""
        if days < 1 or days > 90:
            raise ValueError("Days must be between 1 and 90.")

        params = {
            "days": days,
        }
        if llm_config:
            params["llm_config_id"] = llm_config.id

        response = await self._aget("responses/stats", params=params)
        return ResponsesStats.model_validate(response.json())

    def get_stats(
        self,
        llm_config: LLMConfig | None = None,
        days: int = 30,
    ) -> ResponsesStats:
        """Get usage statistics for responses in a project with optional LLM config filtering.

        Args:
            llm_config (LLMConfig | None): The LLM config to get stats of. If not provided, the project's default LLM config will be used.
            days (int): The number of days to get stats for. Defaults to 30. Must be between 1 and 90.

        Returns:
            ResponsesStats: The stats of the LLM config.

        """
        return run_async(self.aget_stats)(llm_config=llm_config, days=days)

    @retry_request
    async def aadd(
        self,
        response: str | List[ChatCompletionMessageParam],
        prompt_template: PromptTemplate,
        template_variables: TemplateVariables,
        metadata: LLMConfig | GenerationMetadata | None = None,
    ) -> PromptResponse:
        """Async version of add."""
        async with self._semaphore:
            if isinstance(metadata, LLMConfig):
                metadata = GenerationMetadata(llm_model_config=metadata)

            if isinstance(response, str):
                messages = [ChatCompletionAssistantMessageParam(role="assistant", content=response, tool_calls=[])]
            else:
                messages = response

            prompt_response = CreatePromptResponseRequest(
                prompt_template_id=prompt_template.id,
                messages=messages,
                template_variables_id=template_variables.id,
                metadata=metadata,
            )

            server_response = await self._apost(
                "responses",
                json=prompt_response.model_dump(),
            )
            return PromptResponse.model_validate(server_response.json())

    def add(
        self,
        response: str | List[ChatCompletionMessageParam],
        prompt_template: PromptTemplate,
        template_variables: TemplateVariables,
        metadata: LLMConfig | GenerationMetadata | None = None,
    ) -> PromptResponse:
        """Add a response to a prompt template.

        Args:
            response (str | ChatCompletionMessageParam): The response to add.
            prompt_template (PromptTemplate): The prompt template to add the response to.
            template_variables (TemplateVariables | None): The template variables to use for the response.
            metadata (LLMConfig | GenerationMetadata | None): Optional metadata to associate with the response.

        Returns:
            PromptResponse: The newly created prompt response object.

        """
        return run_async(self.aadd)(
            response=response,
            prompt_template=prompt_template,
            template_variables=template_variables,
            metadata=metadata,
        )

    @retry_request
    async def agenerate(
        self,
        prompt_template: PromptTemplate,
        template_variables: TemplateVariables,
        llm_config: LLMConfig | None = None,
    ) -> PromptResponse:
        """Async version of generate."""
        async with self._semaphore:
            if llm_config is not None and llm_config.id is None:
                logger.warning("The LLM config id is None. Default LLM config will be used.")

            prompt_response = CreatePromptResponseRequest(
                prompt_template_id=prompt_template.id,
                template_variables_id=template_variables.id,
                llm_config_id=llm_config.id if llm_config else None,
            )

            server_response = await self._apost(
                "responses",
                json=prompt_response.model_dump(),
            )
            return PromptResponse.model_validate(server_response.json())

    def generate(
        self,
        prompt_template: PromptTemplate,
        template_variables: TemplateVariables,
        llm_config: LLMConfig | None = None,
    ) -> PromptResponse:
        """Generate a response for a prompt template using an LLM.

        This method sends the prompt to an LLM for generation. If no LLM config is provided,
        the project's default LLM config will be used.

        Args:
            prompt_template (PromptTemplate): The prompt template to generate a response for.
            llm_config (LLMConfig | None): Optional LLM configuration to use for generation.
                If not provided, the project's default config will be used.
            template_variables (TemplateVariables | None): The template variables to use for the response.

        Returns:
            PromptResponse: The generated response object

        Raises:
            ValueError: If no template variables source is provided (either template_variables or template_variables_id)

        """
        return run_async(self.agenerate)(
            prompt_template=prompt_template,
            template_variables=template_variables,
            llm_config=llm_config,
        )

    @retry_request
    async def aadd_many(
        self,
        responses: List[str | List[ChatCompletionMessageParam]],
        prompt_template: PromptTemplate,
        template_variables: List[TemplateVariables],
        metadata: List[LLMConfig | GenerationMetadata | None] | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]:
        """Async version of add_many."""
        async with self._semaphore:
            len_responses = len(responses)
            len_template_variables = len(template_variables)
            _metadata = metadata if metadata is not None else [None] * len_responses

            len_metadata = len(_metadata)
            if not (len_template_variables == len_responses == len_metadata):
                raise ValueError(
                    f"All input lists must have the same length. Got {len_template_variables} for template_variables, "
                    f"{len_responses} for responses, and {len_metadata} for metadata."
                )
            prompt_response_ins = []
            for resp, tmp_var, md in zip(responses, template_variables, _metadata):
                if isinstance(md, LLMConfig):
                    md = GenerationMetadata(llm_model_config=md)

                if isinstance(resp, str):
                    messages = [ChatCompletionAssistantMessageParam(role="assistant", content=resp, tool_calls=[])]
                else:
                    messages = resp

                prompt_response_ins.append(
                    CreatePromptResponseRequest(
                        prompt_template_id=prompt_template.id,
                        messages=messages,
                        template_variables_id=tmp_var.id,
                        metadata=md,
                    )
                )

            batch_request = BatchCreatePromptResponseRequest(
                prompt_response_ins=prompt_response_ins,
            )

            return await self._abatch_create(
                path="responses/batches",
                batch_request=batch_request,
                batch_response_type=BatchCreatePromptResponseStatus,
                timeout=timeout,
            )

    def add_many(
        self,
        responses: List[str | ChatCompletionMessageParam],
        prompt_template: PromptTemplate,
        template_variables: List[TemplateVariables],
        metadata: List[LLMConfig | GenerationMetadata | None] | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]:
        """Add multiple responses to a prompt template in bulk.

        Use this method when you have a list of responses to add, instead of adding them one by one with the add() method.

        Args:
            responses (list[str | ChatCompletionMessageParam]): List of responses to add.
            prompt_template (PromptTemplate): The prompt template to add responses to.
            template_variables (list[TemplateVariables]): List of template variables for each response.
            metadata (list[LLMConfig | GenerationMetadata | None] | None): Optional list of metadata for each response.
            timeout (float | None): Timeout in seconds for API requests. Defaults to no timeout.

        Returns:
            list[PromptResponse]: List of newly created prompt response objects.

        """
        return run_async(self.aadd_many)(
            responses=responses,
            prompt_template=prompt_template,
            template_variables=template_variables,
            metadata=metadata,
            timeout=timeout,
        )

    # This function is necessary because we use overloads for the agenerate_many method and reference it in the generate_many method.
    # The TypeChecker would complain if we reference the "base" async version in the generate_many method, as there is no overloaded option for
    # the parameters used.
    async def _agenerate_many_impl(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: List[TemplateVariables] | None = None,
        collection: TemplateVariablesCollection | None = None,
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]:
        assert any([template_variables, collection]), "Either template_variables or collection must be provided."
        assert not all([template_variables, collection]), "Cannot provide both template_variables and collection."

        if collection is not None:
            template_variables = await self._client.template_variables.alist(collection=collection)

        # This is just for the linter, the checks above should ensure this
        assert template_variables

        len_template_variables = len(template_variables)
        llm_configs = [llm_config] * len_template_variables

        prompt_response_ins = []
        for tmp_var, llm_conf in zip(template_variables, llm_configs):
            prompt_response_ins.append(
                CreatePromptResponseRequest(
                    prompt_template_id=prompt_template.id,
                    template_variables_id=tmp_var.id,
                    llm_config_id=llm_conf.id if llm_conf else None,
                )
            )

        batch_request = BatchCreatePromptResponseRequest(
            prompt_response_ins=prompt_response_ins,
        )

        return await self._abatch_create(
            path="responses/batches",
            batch_request=batch_request,
            batch_response_type=BatchCreatePromptResponseStatus,
            timeout=timeout,
        )

    @overload
    async def agenerate_many(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: List[TemplateVariables],
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]: ...

    @overload
    async def agenerate_many(
        self,
        prompt_template: PromptTemplate,
        *,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]: ...

    @retry_request
    async def agenerate_many(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: List[TemplateVariables] | None = None,
        collection: TemplateVariablesCollection | None = None,
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]:
        """Async version of generate_many."""
        return await self._agenerate_many_impl(
            prompt_template=prompt_template,
            template_variables=template_variables,
            collection=collection,
            llm_config=llm_config,
            timeout=timeout,
        )

    @overload
    def generate_many(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: List[TemplateVariables],
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]: ...

    @overload
    def generate_many(
        self,
        prompt_template: PromptTemplate,
        *,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]: ...

    def generate_many(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: List[TemplateVariables] | None = None,
        collection: TemplateVariablesCollection | None = None,
        llm_config: LLMConfig | None = None,
        timeout: float | None = None,
    ) -> List[PromptResponse]:
        """Generate multiple responses for a prompt template.

        Use this method when you have a list of responses to generate, instead of generating them one by one with the generate() method.

        Either `template_variables` or `collection` can be provided:
        - If `template_variables` is given, it will use the provided list of template variables for each response.
        - If `collection` is given, it will use the template variables from the specified collection.

        Args:
            prompt_template (PromptTemplate): The prompt template to use for generation.
            template_variables (list[TemplateVariables] | None): List of template variables for each response.
            collection (TemplateVariablesCollection | None): The collection to use for the template variables.
            llm_config (LLMConfig | None): Optional LLMConfig to use for generation.
            timeout (float): Timeout in seconds for API requests. Defaults to no timeout.

        Returns:
            list[PromptResponse]: List of newly created prompt response objects.

        """
        return run_async(self._agenerate_many_impl)(
            prompt_template=prompt_template,
            template_variables=template_variables,
            collection=collection,
            llm_config=llm_config,
            timeout=timeout,
        )

    async def adelete(self, prompt_response: PromptResponse) -> None:
        """Async version of delete."""
        await self._adelete(f"responses/{prompt_response.id}")

    def delete(self, prompt_response: PromptResponse) -> None:
        """Delete a prompt response.

        Args:
            prompt_response (PromptResponse): The prompt response to delete.

        """
        return run_async(self.adelete)(prompt_response)
