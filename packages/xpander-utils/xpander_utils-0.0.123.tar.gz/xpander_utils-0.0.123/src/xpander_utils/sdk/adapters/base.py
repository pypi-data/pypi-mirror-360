from typing import Any, Dict, List, Optional
from xpander_sdk import ExecutionStatus, Tokens, XpanderClient, Agent

AGENT_FINISH_TOOL_ID = 'xpfinish-agent-execution-finished';

class SDKAdapter:
    """
    Adapter class for interacting with xpander.ai SDK.

    This class provides an interface to manage an xpander.ai agent, 
    including handling tasks, execution results, and memory.

    Attributes:
        agent (Agent): The xpander.ai agent instance.
        xpander_client (XpanderClient): The xpander.ai client instance.
    """

    agent: Agent

    def __init__(self, api_key: str, agent_id: str, base_url: Optional[str] = None, organization_id: Optional[str] = None, should_reset_cache: Optional[bool] = False, with_metrics_report: Optional[bool] = False, version: Optional[int] = None):
        """
        Initialize the SDKAdapter with the provided API key and agent ID.

        Args:
            api_key (str): The API key for authentication with xpander.ai.
            agent_id (str): The ID of the agent to interact with.
            base_url (Optional[str], optional): The base URL for the xpander.ai API. Defaults to None.
            organization_id (Optional[str], optional): The organization ID, if applicable. Defaults to None.
            with_metrics_report (Optional[bool], optional): If to auto-report metrics (llm & execution). Default to False
        """
        self.xpander_client = XpanderClient(api_key=api_key, base_url=base_url, organization_id=organization_id,should_reset_cache=should_reset_cache)
        self.agent = self.xpander_client.agents.get(agent_id=agent_id, version=version)
        self.with_metrics_report = with_metrics_report
        self.execution_tokens: Dict[str, Tokens] = {}

    def get_system_prompt(self) -> str:
        """
        Retrieve the system prompt for the agent.

        Returns:
            str: The formatted system prompt.
        """
        agent_role = "\n".join(self.agent.instructions.role)
        agent_goal = "\n".join(self.agent.instructions.goal)
        return f"""
            Agent general instructions: "{self.agent.instructions.general}"\n
            Agent role instructions: "{agent_role}"\n
            Agent goal instructions: "{agent_goal}"
        """

    def get_tools(self) -> List[Any]:
        """
        Retrieve the tools available for the agent.

        Raises:
            NotImplementedError: This method is not implemented.

        Returns:
            List[Any]: A list of tools.
        """
        raise NotImplementedError('method "get_tools" not implemented')

    def init_memory(self, agent: Any):
        """
        Initialize memory for the given agent.

        Args:
            agent (Any): The agent instance.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError('method "init_memory" not implemented')

    def set_system_prompt(self, agent: Any):
        """
        Set the system prompt for the given agent.

        Args:
            agent (Any): The agent instance.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError('method "set_system_prompt" not implemented')

    def add_task(self, input: str, files: Optional[List[str]] = None, use_worker: Optional[bool] = False, thread_id: Optional[str] = None):
        """
        Add a task to the agent and initialize memory with the input and instructions.

        Args:
            input (str): The task input.
            files (Optional[List[str]], optional): A list of file paths associated with the task. Defaults to None.
            use_worker (Optional[bool], optional): Whether to use a worker for execution. Defaults to False.
            thread_id (Optional[str], optional): The thread ID for task execution. Defaults to None.
        """
        files = files or []
        self.agent.add_task(input=input, files=files, use_worker=use_worker, thread_id=thread_id)
        
        instructions = self.agent.instructions
        instructions.general += """
            **Important:** If an error occurs repeatedly, **STOP execution immediately**. Do not retry the same function endlessly. Instead:  
            1. **Log the issue clearly**, including the error message, input parameters, and last successful step.  
            2. **Analyze the failure pattern**—if the same error occurs more than twice, assume it is persistent.  
            3. **Provide a concise error report**, including possible causes and suggested resolutions, before terminating execution.  
            4. **Avoid redundant operations**—if the same function is invoked multiple times without a meaningful result, halt further attempts.  
        """
        
        self.agent.memory.init_messages(input=self.agent.execution.input_message, instructions=self.agent.instructions)

    def update_execution_result(self, is_success: bool, result: str):
        """
        Update the execution result of the agent.

        Args:
            is_success (bool): Whether the execution was successful.
            result (str): The execution result.
        """
        self.agent.execution.update(
            agent=self.agent,
            execution_id=self.agent.execution.id,
            delta={
                "status": ExecutionStatus.COMPLETED if is_success else ExecutionStatus.ERROR,
                "result": result
            }
        )
        self.agent.execution.status = ExecutionStatus.COMPLETED if is_success else ExecutionStatus.ERROR
        self.agent.execution.result = result

    def sync_memory(self, agent: Any):
        """
        Synchronize memory for the given agent.

        Args:
            agent (Any): The agent instance.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError('method "sync_memory" not implemented')
