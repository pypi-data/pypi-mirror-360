from typing import List

from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    BatchCreateRatingRequest,
    BatchCreateRatingResponseStatus,
    CreateRatingRequest,
    Experiment,
    PromptResponse,
    Rating,
    RatingMode,
)
from elluminate.utils import retry_request, run_async


class RatingsResource(BaseResource):
    async def alist(
        self,
        prompt_response: PromptResponse,
    ) -> List[Rating]:
        """Async version of list."""
        params = {
            "prompt_response_id": prompt_response.id,
        }
        return await self._paginate(
            path="ratings",
            model=Rating,
            params=params,
            resource_name="Ratings",
        )

    def list(
        self,
        prompt_response: PromptResponse,
    ) -> List[Rating]:
        """Gets the ratings for a prompt response.

        Args:
            prompt_response (PromptResponse): The prompt response to get ratings for.

        Returns:
            list[Rating]: List of rating objects for the prompt response.

        Raises:
            httpx.HTTPStatusError: If the prompt response doesn't exist or belongs to a different project.

        """
        return run_async(self.alist)(prompt_response)

    @retry_request
    async def arate(
        self,
        prompt_response: PromptResponse,
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.DETAILED,
    ) -> List[Rating]:
        """Async version of create."""
        async with self._semaphore:
            response = await self._apost(
                "ratings",
                json=CreateRatingRequest(
                    prompt_response_id=prompt_response.id,
                    experiment_id=experiment.id if experiment else None,
                    rating_mode=rating_mode,
                ).model_dump(),
            )

        return [Rating.model_validate(rating) for rating in response.json()]

    def rate(
        self,
        prompt_response: PromptResponse,
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.DETAILED,
    ) -> List[Rating]:
        """Rates a response against its prompt template's criteria using an LLM.

        This method evaluates a prompt response against all applicable criteria associated with its prompt template.
        If template variables were used for the response, it will consider both general criteria and criteria specific
        to those variables.

        Args:
            prompt_response (PromptResponse): The response to rate.
            experiment (Experiment | None): Optional experiment to associate ratings with. If provided,
                the method will verify that the response matches the experiment's prompt template,
                collection, and LLM configuration before rating.
            rating_mode (RatingMode): Mode for rating generation:
                - FAST: Quick evaluation without detailed reasoning
                - DETAILED: Includes explanations for each rating

        Returns:
            list[Rating]: List of rating objects, one per criterion.

        Raises:
            httpx.HTTPStatusError: If no criteria exist for the prompt template

        """
        return run_async(self.arate)(
            prompt_response,
            experiment=experiment,
            rating_mode=rating_mode,
        )

    @retry_request
    async def arate_many(
        self,
        prompt_responses: List[PromptResponse],
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.DETAILED,
        timeout: float | None = None,
    ) -> List[List[Rating]]:
        """Async version of rate_many."""
        async with self._semaphore:
            response = await self._abatch_create(
                path="ratings/batches",
                batch_request=BatchCreateRatingRequest(
                    prompt_response_ids=[pr.id for pr in prompt_responses],
                    rating_mode=rating_mode,
                    experiment_id=experiment.id if experiment else None,
                ),
                batch_response_type=BatchCreateRatingResponseStatus,
                timeout=timeout,
            )

        return response

    def rate_many(
        self,
        prompt_responses: List[PromptResponse],
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.DETAILED,
        timeout: float | None = None,
    ) -> List[List[Rating]]:
        """Batch version of rate.

        Args:
            prompt_responses (list[PromptResponse]): List of prompt responses to rate.
            experiment (Experiment | None): Optional experiment to associate ratings with.
            rating_mode (RatingMode): Mode for rating generation (FAST or DETAILED). If DETAILED a reasoning is added to the rating.
            timeout (float): Timeout in seconds for API requests. Defaults to no timeout.

        Returns:
            List[List[Rating]]: List of lists of rating objects, one per criterion for each prompt response.

        """
        return run_async(self.arate_many)(
            prompt_responses,
            experiment=experiment,
            rating_mode=rating_mode,
            timeout=timeout,
        )

    async def adelete(self, rating: Rating) -> None:
        """Async version of delete."""
        await self._adelete(f"/{rating.id}")

    def delete(self, rating: Rating) -> None:
        """Deletes a rating.

        Args:
            rating (Rating): The rating to delete.

        """
        return run_async(self.adelete)(rating)

    async def adelete_all(self, prompt_response: PromptResponse) -> None:
        """Async version of delete_all."""
        params = {"prompt_response_id": prompt_response.id}
        await self._adelete("ratings", params=params)

    def delete_all(self, prompt_response: PromptResponse) -> None:
        """Deletes all ratings for a prompt response.

        Args:
            prompt_response (PromptResponse): The prompt response to delete ratings for.

        Raises:
            httpx.HTTPStatusError: If the prompt response doesn't exist or belongs to a different project.

        """
        return run_async(self.adelete_all)(prompt_response)
