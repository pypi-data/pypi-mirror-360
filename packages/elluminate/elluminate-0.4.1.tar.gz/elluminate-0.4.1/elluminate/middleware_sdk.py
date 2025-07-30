import asyncio
import inspect
import re
import time
from datetime import datetime
from typing import Any

import openai
from loguru import logger

from elluminate.client import Client
from elluminate.schemas import GenerationMetadata, LLMConfig


class ElluminateOpenAIMiddleware:
    _instance: "ElluminateOpenAIMiddleware | None" = None

    def __new__(cls, _client: Client) -> "ElluminateOpenAIMiddleware":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._patch_openai()
        return cls._instance

    def __init__(self, client: Client) -> None:
        self.client = client

    @classmethod
    def initialize(
        cls,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        api_key_env: str | None = None,
    ) -> None:
        """Initialize the ElluminateOpenAIMiddleware.

        Args:
            base_url (str | None): The base URL of the Elluminate API.
            api_key (str | None): The API key to use for the Elluminate API.
            api_key_env (str | None): The environment variable to use for the API key.

        """
        if cls._instance is None:
            optional_kwargs = {}
            if base_url is not None:
                optional_kwargs["base_url"] = base_url
            if api_key is not None:
                optional_kwargs["api_key"] = api_key
            if api_key_env is not None:
                optional_kwargs["api_key_env"] = api_key_env

            client = Client(**optional_kwargs)
            cls(client)

    def _patch_openai(self) -> None:
        original_create = openai.resources.chat.Completions.create

        def intercepted_create(_self: openai.resources.chat.Completions, **kwargs: Any) -> Any:
            # Call the original method first
            response = original_create(_self, **kwargs)

            try:
                annotation = self._extract_annotation()
            except Exception as e:
                logger.warning(f"Error in Elluminate middleware processing: {str(e)}", exc_info=True)
                annotation = None
            if annotation is None:
                # Create a timestamp-based annotation if none provided
                annotation = "middleware-" + datetime.now().strftime("%y%m%d")

            # Start middleware processing in background
            messages = kwargs.get("messages", [])
            self._create_background_task(self._process_middleware(response, messages, _self, kwargs, annotation))

            return response

        # Replace the original method with our intercepted version
        openai.resources.chat.Completions.create = intercepted_create  # type: ignore[reportAttributeAccessIssue]

    def _create_background_task(self, coro: Any) -> None:
        """Helper to create and track background tasks"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            loop.create_task(coro)
        else:
            loop.run_until_complete(coro)

    async def _process_middleware(
        self,
        response: Any,
        messages: list,
        completions: openai.resources.chat.Completions,
        kwargs: dict,
        annotation: str,
    ) -> None:
        """Async function to handle middleware processing"""
        try:
            # Extract the prompt
            prompt = messages[-1]["content"] if messages else ""

            collection, _ = await self.client.collections.aget_or_create(
                name="openai-" + annotation,
                description="Auto-generated collection for OpenAI middleware",
            )
            prompt_template, _ = await self.client.prompt_templates.aget_or_create(
                "{{text}}",
                name=annotation + "-default",
                default_collection=collection,
            )

            ai_response = response.choices[0].message.content
            if ai_response is None:
                return

            # Create an `LLMConfig` for this inference
            llm_config = LLMConfig(
                # Important: Do not include the `api_key` here since this model
                # will be saved into the `GenerationMetadata`
                api_version=getattr(completions._client, "_api_version", None),
                llm_base_url=str(completions._client._base_url),
                llm_model_name=response.model if response.model else f"{kwargs['model']}",
                max_tokens=kwargs.get("max_tokens"),
                top_p=kwargs.get("top_p"),
                temperature=kwargs.get("temperature", 0.7),
                best_of=kwargs.get("best_of"),
                logprobs=kwargs.get("logprobs"),
                top_logprobs=kwargs.get("top_logprobs"),
                reasoning_effort=kwargs.get("reasoning_effort"),
            )

            # Use the `llm_model_name` for this middleware `LLMConfig`
            await self.client.llm_configs.aget_or_create(
                name=f"{llm_config.llm_model_name} - middleware",
                api_key=completions._client.api_key,
                **llm_config.model_dump(exclude_unset=True),
            )

            duration_seconds = getattr(response, "created", None)
            if duration_seconds is not None:
                duration_seconds = int(int(time.time()) - response.created)

            # Create generation metadata
            generation_metadata = GenerationMetadata(
                llm_model_config=llm_config,
                duration_seconds=duration_seconds,
                input_tokens=getattr(response.usage, "prompt_tokens", None) if hasattr(response, "usage") else None,
                output_tokens=getattr(response.usage, "completion_tokens", None)
                if hasattr(response, "usage")
                else None,
            )

            template_variables = await self.client.template_variables.aadd_to_collection(
                {"text": prompt}, collection
            )

            # Record the response in Elluminate
            await self.client.responses.aadd(
                prompt_template=prompt_template,
                response=ai_response,
                template_variables=template_variables,
                metadata=generation_metadata,
            )

        except Exception as e:
            logger.warning(f"Error in Elluminate middleware processing: {str(e)}", exc_info=True)
            raise e

    def _extract_annotation(self) -> str | None:
        annotation: str | None = None
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            try:
                # Get the first source line of the calling code
                calling_line = inspect.getframeinfo(frame.f_back.f_back).code_context[0].strip()
                # Check if there's an Elluminate annotation using regex
                match = re.search(r"#\s*elluminate:\s*(.*?)(?:\s*#|$)", calling_line)
                if match:
                    annotation = match.group(1).strip()
                    if not annotation:
                        logger.warning("Empty prompt name annotation")
                        annotation = None
            except Exception:
                logger.warning("Error processing Elluminate annotation", exc_info=True)
            finally:
                del frame
        return annotation
