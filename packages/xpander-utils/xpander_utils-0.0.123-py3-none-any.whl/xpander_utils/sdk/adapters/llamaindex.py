import json
from typing import Dict, Optional, Callable, Union, List, Any
from xpander_sdk import ToolCall, ToolCallType, LLMTokens, Tokens
from .base import SDKAdapter, AGENT_FINISH_TOOL_ID
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import AgentRunner
from llama_index.core.prompts import PromptTemplate
from llama_index.core.memory.types import ChatMessage
from llama_index.core.llms import MessageRole
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks.pythonically_printing_base_handler import (
    PythonicallyPrintingBaseHandler,
)
from llama_index.core.callbacks.schema import CBEventType, EventPayload

from ...generic import generate_tool_call_id

class LlamaIndexAdapter(SDKAdapter):
    """
    Adapter for integrating LlamaIndex with xpander.ai.

    This class extends SDKAdapter to provide LlamaIndex-compatible methods 
    for managing tools, system prompts, and memory synchronization.

    Attributes:
        agent (Agent): The xpander.ai agent instance.
    """

    def __init__(self, api_key: str, agent_id: str, base_url: Optional[str] = None, organization_id: Optional[str] = None, with_metrics_report: Optional[bool] = False):
        """
        Initialize the LlamaIndexAdapter.

        Args:
            api_key (str): The API key for authentication with xpander.ai.
            agent_id (str): The ID of the xpander.ai agent.
            base_url (Optional[str], optional): The base URL for the xpander.ai API. Defaults to None.
            organization_id (Optional[str], optional): The organization ID, if applicable. Defaults to None.
            with_metrics_report (Optional[bool], optional): If to auto-report metrics (llm & execution). Default to False.
        """
        super().__init__(api_key=api_key, agent_id=agent_id, base_url=base_url, organization_id=organization_id, with_metrics_report=with_metrics_report)
        self.agent.disable_agent_end_tool()  # No need since LlamaIndex handles it.
        self.callback_manager = CallbackManager([LLMHandler(xpander=self)])

    def get_tools(self, return_as_function_tool: bool = True) -> List[Union[FunctionTool, Callable]]:
        """
        Retrieve the tools available for the agent.

        Args:
            return_as_function_tool (bool, optional): Whether to return tools as FunctionTool instances.
                Defaults to True.

        Returns:
            List[Union[FunctionTool, Callable]]: A list of tool functions or FunctionTool instances.
        """
        xpander_tools = self.agent.get_tools()
        tools = []

        for tool in xpander_tools:
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

                    # Generate a tool call ID and log the tool call in memory
                    tool_call_id = generate_tool_call_id()
                    self.agent.add_messages(messages=[{
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "name": tool_name,
                            "payload": json.dumps({
                                "bodyParams": bodyParams,
                                "queryParams": queryParams,
                                "pathParams": pathParams
                            }),
                            "tool_call_id": tool_call_id
                        }]
                    }])

                    # Execute the tool
                    xpander_agent_tool_invocation = self.agent.run_tool(
                        tool=ToolCall(
                            name=tool_name,
                            type=ToolCallType.XPANDER,
                            payload={
                                "bodyParams": bodyParams,
                                "queryParams": queryParams,
                                "pathParams": pathParams
                            },
                            tool_call_id=tool_call_id
                        )
                    )

                    # Convert result to string
                    stringified_result = json.dumps(xpander_agent_tool_invocation.result)
                    
                    if not xpander_agent_tool_invocation.is_success:
                        raise Exception(f"Error running tool: {stringified_result}")

                    return stringified_result

                return runner

            fn = get_executor(tool_name=tool["function"]["name"])
            fn.__name__ = tool["function"]["name"]
            fn.__doc__ = tool["function"]["description"]
            tools.append(FunctionTool.from_defaults(fn=fn) if return_as_function_tool else fn)

        return tools

    def set_system_prompt(self, agent: AgentRunner, system_prompt: Optional[str] = None):
        """
        Set the system prompt for the given agent.

        Args:
            agent (AgentRunner): The LlamaIndex agent runner instance.
            system_prompt (Optional[str], optional): A custom system prompt. Defaults to None.
        """
        agent.update_prompts({
            "agent_worker:system_prompt": PromptTemplate(f"""
                You are designed to help with a variety of tasks, from answering questions   
                to providing summaries to other types of analyses.

                {system_prompt if system_prompt else self.get_system_prompt()}
            """)
        })

    def get_chat_history(self) -> List[ChatMessage]:
        """
        Retrieve the chat history from the xpander.ai agent.

        Returns:
            List[ChatMessage]: A list of ChatMessage objects representing past interactions.
        """
        messages = self.agent.messages
        history: List[ChatMessage] = []

        # If only system and first user message exist, return an empty history
        if len(messages) == 2:
            return []

        for message in messages:
            if message['role'] == MessageRole.USER.value:
                history.append(ChatMessage(role=MessageRole.USER, content=message['content']))
            elif message['role'] == MessageRole.ASSISTANT.value and 'content' in message and message['content']:
                history.append(ChatMessage(role=MessageRole.ASSISTANT, content=message['content']))

        return history

    def sync_memory(self, agent: AgentRunner):
        """
        Syncs the LlamaIndex memory into xpander.ai memory.

        Args:
            agent (AgentRunner): The LlamaIndex agent runner instance.
        """
        if hasattr(agent, "chat_history") and isinstance(agent.chat_history, list):
            messages_to_append = []
            xpander_messages = {(msg["role"], msg["content"]) for msg in self.agent.messages}

            for msg in agent.chat_history:
                role = msg.role.value
                content = "\n".join(block.text for block in msg.blocks if hasattr(block, "text"))

                if (role, content) not in xpander_messages:
                    messages_to_append.append({"role": role, "content": content})

            if messages_to_append:
                self.agent.add_messages(messages=messages_to_append)

class LLMHandler(PythonicallyPrintingBaseHandler):
    def __init__(self, xpander: LlamaIndexAdapter) -> None:
        super().__init__(
            event_starts_to_ignore=[], event_ends_to_ignore=[]
        )
        
        self.xpander = xpander


    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        return

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        pass

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        if self.xpander.with_metrics_report:
            if event_type == CBEventType.LLM and payload is not None:
                # calculate total tokens
                execution_id = self.xpander.agent.execution.id
                llm_response = payload['response'].raw.model_dump()
                tokens = LLMTokens(completion_tokens=llm_response['usage']['completion_tokens'],prompt_tokens=llm_response['usage']['prompt_tokens'],total_tokens=llm_response['usage']['total_tokens'])
                if not execution_id in self.xpander.execution_tokens:
                    self.xpander.execution_tokens[execution_id] = Tokens(worker=tokens)
                else:
                    self.xpander.execution_tokens[execution_id].worker.completion_tokens += tokens.completion_tokens
                    self.xpander.execution_tokens[execution_id].worker.prompt_tokens += tokens.prompt_tokens
                    self.xpander.execution_tokens[execution_id].worker.total_tokens += tokens.total_tokens
                
                # report llm usage
                self.xpander.agent.report_llm_usage(llm_response=llm_response,llm_inference_duration=0)
            elif event_type == CBEventType.AGENT_STEP and "response" in payload and payload["response"].response:
                self.xpander.update_execution_result(is_success=True,result=payload["response"].response)
                self.xpander.agent.report_execution_metrics(llm_tokens=self.xpander.execution_tokens[self.xpander.agent.execution.id],ai_model="N/A")