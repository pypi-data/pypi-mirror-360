import json
from pydantic import BaseModel
from typing import Dict, Optional, List, Union
from smolagents import Tool, ActionStep, MultiStepAgent, TaskStep, SystemPromptStep, ToolCall as SmolAgentsToolCall
from xpander_sdk import LLMTokens, ToolCall, ToolCallType, ToolCallResult, Tokens, ExecutionStatus
from .base import SDKAdapter

class SmolAgentsMemory(BaseModel):
    """
    Represents the memory structure for SmolAgents.

    Attributes:
        steps (List[Union[TaskStep, ActionStep]]): A list of steps in the memory.
        system_prompt (SystemPromptStep): The system prompt step.
    """

    steps: List[Union[TaskStep, ActionStep]]
    system_prompt: SystemPromptStep

    class Config:
        arbitrary_types_allowed = True

class SmolAgentsAdapter(SDKAdapter):
    """
    Adapter for integrating SmolAgents with xpander.ai.

    This class extends SDKAdapter to provide SmolAgents-compatible methods 
    for managing tools, system prompts, and memory synchronization.

    Attributes:
        agent (Agent): The xpander.ai agent instance.
    """

    def __init__(self, api_key: str, agent_id: str, base_url: Optional[str] = None, organization_id: Optional[str] = None, with_metrics_report: Optional[bool] = False):
        """
        Initialize the SmolAgentsAdapter.

        Args:
            api_key (str): The API key for authentication with xpander.ai.
            agent_id (str): The ID of the xpander.ai agent.
            base_url (Optional[str], optional): The base URL for the xpander.ai API. Defaults to None.
            organization_id (Optional[str], optional): The organization ID, if applicable. Defaults to None.
            with_metrics_report (Optional[bool], optional): If to auto-report metrics (llm & execution). Default to False.
        """
        super().__init__(api_key=api_key, agent_id=agent_id, base_url=base_url, organization_id=organization_id, with_metrics_report=with_metrics_report)
        self.agent.disable_agent_end_tool()  # No need since SmolAgents handles it.

    def get_tools(self) -> List[Tool]:
        """
        Retrieve the tools available for the agent.

        Returns:
            List[Tool]: A list of SmolAgents-compatible tools.
        """
        xpander_tools = self.agent.get_tools()
        tools = []

        for tool in xpander_tools:
            smolagent_tool = Tool()
            smolagent_tool.name = tool["function"]["name"]
            smolagent_tool.description = tool["function"]["description"]
            smolagent_tool.inputs = {}

            # Build input schema
            if tool["function"].get("parameters", {}).get("type") == "object":
                for property_name, property_spec in tool["function"]["parameters"].get("properties", {}).items():
                    smolagent_tool.inputs[property_name] = property_spec

            smolagent_tool.output_type = "string"

            def get_executor(tool_name: str):
                def runner(
                    bodyParams: Optional[Dict] = None,
                    queryParams: Optional[Dict] = None,
                    pathParams: Optional[Dict] = None
                ):
                    """
                    Execute a tool by calling the xpander.ai agent's tool execution API.

                    Args:
                        bodyParams (Optional[Dict], optional): Body parameters for the tool call. Defaults to None.
                        queryParams (Optional[Dict], optional): Query parameters for the tool call. Defaults to None.
                        pathParams (Optional[Dict], optional): Path parameters for the tool call. Defaults to None.

                    Returns:
                        str: The JSON stringified result of the tool execution.

                    Raises:
                        Exception: If the tool execution fails.
                    """
                    bodyParams = bodyParams or {}
                    queryParams = queryParams or {}
                    pathParams = pathParams or {}

                    xpander_agent_tool_invocation = self.agent.run_tool(
                        tool=ToolCall(
                            name=tool_name,
                            type=ToolCallType.XPANDER,
                            payload={
                                "bodyParams": bodyParams,
                                "queryParams": queryParams,
                                "pathParams": pathParams
                            }
                        )
                    )

                    stringified_result = json.dumps(xpander_agent_tool_invocation.result)

                    if not xpander_agent_tool_invocation.is_success:
                        raise Exception(f"Error running tool: {stringified_result}")

                    return stringified_result

                return runner

            smolagent_tool.forward = get_executor(tool_name=smolagent_tool.name)
            smolagent_tool.is_initialized = True
            tools.append(smolagent_tool)

        return tools

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

    def step_callback(self):
        """
        Returns a callback function to synchronize SmolAgents memory into xpander.ai memory.

        Returns:
            Callable: A callback function.
        """
        def callback(memory_step: ActionStep, agent: MultiStepAgent):
            # Sync SmolAgents steps into xpander.ai memory
            llm_response = memory_step.model_output_message.raw.model_dump()
            self.agent.add_messages(messages=llm_response)
            
            if self.agent.execution.status == ExecutionStatus.PENDING:
                self.agent.execution.update(agent=self.agent,execution_id=self.agent.execution.id,delta={"status": ExecutionStatus.EXECUTING.value.lower()})
            
            if self.with_metrics_report:
                # calculate total tokens
                execution_id = self.agent.execution.id
                tokens = LLMTokens(completion_tokens=llm_response['usage']['completion_tokens'],prompt_tokens=llm_response['usage']['prompt_tokens'],total_tokens=llm_response['usage']['total_tokens'])
                if not execution_id in self.execution_tokens:
                    self.execution_tokens[execution_id] = Tokens(worker=tokens)
                else:
                    self.execution_tokens[execution_id].worker.completion_tokens += tokens.completion_tokens
                    self.execution_tokens[execution_id].worker.prompt_tokens += tokens.prompt_tokens
                    self.execution_tokens[execution_id].worker.total_tokens += tokens.total_tokens
                
                # report llm usage
                self.agent.report_llm_usage(llm_response=llm_response,llm_inference_duration=memory_step.duration)

            tool_call_results = []
            if memory_step.tool_calls:
                for tc in memory_step.tool_calls:
                    result = memory_step.observations or memory_step.action_output or ""
                    is_error = "Error running tool" in result

                    tool_call_result = ToolCallResult(
                        tc.name, tool_call_id=tc.id, payload=tc.arguments,
                        result=result, is_success=not is_error, is_error=is_error
                    )
                    tool_call_results.append(tool_call_result)

                    if tc.name == "final_answer":
                        self.update_execution_result(is_success=not is_error, result=result)
                        # report execution
                        if self.with_metrics_report: # refetch and update metrics
                            self.agent.report_execution_metrics(llm_tokens=self.execution_tokens[self.agent.execution.id],ai_model=agent.model.model_id)

                self.agent.add_tool_call_results(tool_call_results=tool_call_results)

        return callback

    def init_memory(self, agent: MultiStepAgent):
        """
        Initialize the memory for the SmolAgents agent.

        Args:
            agent (MultiStepAgent): The SmolAgents agent instance.
        """
        memory = SmolAgentsMemory(steps=[], system_prompt=SystemPromptStep(system_prompt=self.get_system_prompt()))
        messages = self.agent.messages

        if len(messages) <= 2:
            # Initial run: Append only the input message as a task step
            memory.steps.append(TaskStep(task=self.agent.execution.input_message.content))
        else:
            steps = []
            for message in messages[1:]:
                if message['role'] == "user":
                    steps.append(TaskStep(task=message['content']))
                elif message['role'] == 'assistant':
                    has_tool_calls = "tool_calls" in message and message["tool_calls"]
                    if has_tool_calls:
                        step = ActionStep()
                        step_tool_calls = []
                        step_result = ""

                        for tc in message['tool_calls']:
                            tool_call = SmolAgentsToolCall(
                                name=tc['function']['name'],
                                arguments=tc['function']['arguments'],
                                id=tc['id']
                            )

                            tool_call_result = next(
                                (msg for msg in messages if msg['role'] == "tool" and msg.get('tool_call_id') == tool_call.id),
                                None
                            )

                            step_tool_calls.append(tool_call)
                            if tool_call_result:
                                step_result += tool_call_result['content']

                        step.tool_calls = step_tool_calls
                        is_final = any(tc for tc in step.tool_calls if tc.name == "final_answer")

                        if is_final:
                            step.action_output = step_result
                        else:
                            step.observations = step_result

                        steps.append(step)

            memory.steps.extend(steps)

        agent.memory.steps = memory.steps
        agent.memory.system_prompt = memory.system_prompt
