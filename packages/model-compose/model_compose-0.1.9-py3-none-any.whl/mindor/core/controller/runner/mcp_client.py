from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from mindor.dsl.schema.controller import ControllerConfig
from mindor.core.utils.mcp_client import McpClient
from .runner import ControllerClient

class McpControllerClient(ControllerClient):
    def __init__(self, config: ControllerConfig):
        super().__init__(config)

    async def run_workflow(self, workflow_id: Optional[str], input: Any) -> Any:
        pass

    async def close(self) -> None:
        pass
