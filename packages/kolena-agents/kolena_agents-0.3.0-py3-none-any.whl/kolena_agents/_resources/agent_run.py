from typing import Any
from typing import List
from typing import Optional

import kolena_agents.types.agent_run as agent_run_types
from kolena_agents._generated.openapi_client import ApiClient  # type: ignore
from kolena_agents._generated.openapi_client.api import ClientApi  # type: ignore


class AgentRun:
    def __init__(self, client: ApiClient) -> None:
        """Initialize the AgentRun resource.

        Args:
            client: The configured API client instance.
        """
        self._api = ClientApi(client)

    def get(self, agent_id: int, run_id: int) -> agent_run_types.AgentRun:
        """Get details of a specific agent run.

        Args:
            agent_id: The ID of the agent
            run_id: The ID of the run to retrieve
        """
        return self._api.get_agent_run_api_v1_client_agents_agent_id_runs_run_id_get(
            agent_id=agent_id, run_id=run_id
        )

    def add(
        self, agent_id: int, files: List[Any], user_defined_id: Optional[str] = None
    ) -> agent_run_types.AgentRun:
        """Add a new agent run.

        Args:
            agent_id: The ID of the agent
            files: List of files to upload with the run
            user_defined_id: Optional user-defined identifier for the run
        """
        return self._api.add_agent_run_api_v1_client_agents_agent_id_runs_post(
            agent_id=agent_id,
            files=files,
            user_defined_id=user_defined_id,
        )

    def list(
        self,
        agent_id: int,
        page_number: int = 0,
        page_size: int = 50,
        run_ids: Optional[List[int]] = None,
    ) -> agent_run_types.ListAgentRunsResponse:
        """Get a paginated list of agent runs.

        Args:
            agent_id: The ID of the agent
            page_number: Page number for pagination (default: 0)
            page_size: Number of items per page (default: 50, max: 1000)
            run_ids: Optional list of run_id to get.
        """
        return self._api.list_agent_runs_api_v1_client_agents_agent_id_runs_get(
            agent_id=agent_id,
            page_number=page_number,
            page_size=page_size,
            run_ids=run_ids,
        )

    def delete(self, agent_id: int, run_id: int) -> None:
        """Delete a specific agent run.

        Args:
            agent_id: The ID of the agent
            run_id: The ID of the run to delete
        """
        self._api.delete_agent_run_api_v1_client_agents_agent_id_runs_run_id_delete(
            agent_id=agent_id, run_id=run_id
        )
