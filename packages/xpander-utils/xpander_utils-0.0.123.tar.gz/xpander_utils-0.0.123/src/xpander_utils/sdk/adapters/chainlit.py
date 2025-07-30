import hashlib
import json
from os import getenv
from pydantic import BaseModel
from typing import Any, Dict, Optional, List, Callable
from xpander_sdk import (
    UserDetails,
    Memory,
    XpanderClient,
    ToolCall,
    ToolCallType,
    ToolCallResult,
    LLMProvider,
    SourceNodeType,
    GraphItem,
    Agent,
    AgentGraphItemType
)
from ...generic import get_sub_agent_id_from_oas_by_name, wait, get_uuid
from .base import SDKAdapter
import chainlit as cl
from chainlit import make_async
from chainlit.data.base import BaseDataLayer
from chainlit.user import PersistedUser, User
from chainlit.types import (
    Feedback,
    PaginatedResponse,
    PageInfo,
    Pagination,
    ThreadDict,
    ThreadFilter,
)
from chainlit.step import StepDict
from chainlit.element import ElementDict
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).isoformat()

AGENT_END_TOOL = "xpfinish-agent-execution-finished"
MAX_TOOL_CALLS = 15

class ChainlitToolCallWithLLMResponse(BaseModel):
    tool_call: Any
    completion_response: Any = None

class ChainlitXpanderDataLayer(BaseDataLayer):
    """
    Data layer for handling Chainlit interactions with xpander.ai.

    Attributes:
        thread_authors_cache (dict): Cache for storing thread authors.
    """

    def __init__(self):
        self.thread_authors_cache = {}
        self.users_cache = {}

    async def get_user(self, identifier: str) -> PersistedUser:
        """
        Retrieve user information.

        Args:
            identifier (str): User identifier.

        Returns:
            PersistedUser: The user data.
        """
        pass

    async def create_user(self, user: User) -> PersistedUser:
        """
        Create a new user.

        Args:
            user (User): The user data.

        Returns:
            PersistedUser: Persisted user details.
        """
        persisted_user = PersistedUser(
            id=user.identifier,
            createdAt=user.metadata["created_at"],
            identifier=user.identifier,
            display_name=user.display_name,
            metadata=user.metadata,
        )
        
        self.users_cache[persisted_user.id] = persisted_user
        
        return persisted_user

    async def upsert_feedback(self, feedback: Feedback) -> str:
        """
        Insert or update feedback.

        Args:
            feedback (Feedback): Feedback data.

        Returns:
            str: Feedback ID.
        """
        pass

    async def delete_feedback(self, feedback_id: str) -> bool:
        """
        Delete feedback.

        Args:
            feedback_id (str): Feedback identifier.

        Returns:
            bool: True if deleted, False otherwise.
        """
        pass

    async def create_element(self, element_dict: ElementDict):
        """
        Create a new element.

        Args:
            element_dict (ElementDict): Element data.
        """
        pass

    async def get_element(self, thread_id: str, element_id: str) -> ElementDict:
        """
        Retrieve an element.

        Args:
            thread_id (str): Thread identifier.
            element_id (str): Element identifier.

        Returns:
            ElementDict: Element details.
        """
        pass

    async def delete_element(self, element_id: str):
        """
        Delete an element.

        Args:
            element_id (str): Element identifier.
        """
        pass

    async def create_step(self, step_dict: StepDict):
        """
        Create a new step.

        Args:
            step_dict (StepDict): Step data.
        """
        pass

    async def update_step(self, step_dict: StepDict):
        """
        Update an existing step.

        Args:
            step_dict (StepDict): Updated step data.
        """
        pass

    async def delete_step(self, step_id: str):
        """
        Delete a step.

        Args:
            step_id (str): Step identifier.
        """
        pass

    async def get_thread_author(self, thread_id: str) -> str:
        """
        Retrieve the author of a thread.

        Args:
            thread_id (str): Thread identifier.

        Returns:
            str: User ID of the author.
        """
        author: dict = self.thread_authors_cache.get(thread_id, "")
        return author.get("user_id", "")

    async def delete_thread(self, thread_id: str):
        """
        Delete a thread and its associated data.

        Args:
            thread_id (str): Thread identifier.

        Raises:
            Exception: If the thread author is not found.
        """
        author: dict = self.thread_authors_cache.get(thread_id, None)
        if not author:
            raise Exception("Thread author not found")

        xpander = XpanderClient(
            api_key=getenv("AGENT_CONTROLLER_API_KEY", ""),
            base_url=getenv("AGENT_CONTROLLER_URL", ""),
            organization_id=author.get("organization_id"),
        )
        Memory.delete_thread_by_id({"configuration": xpander.configuration}, thread_id=thread_id)
        self.thread_authors_cache.pop(thread_id)

    async def list_threads(self, pagination: Pagination, filters: ThreadFilter) -> PaginatedResponse[ThreadDict]:
        """
        List threads for a user.

        Args:
            pagination (Pagination): Pagination settings.
            filters (ThreadFilter): Filters for fetching threads.

        Returns:
            PaginatedResponse[ThreadDict]: List of threads.
        """
        user: PersistedUser = self.users_cache.get(filters.userId, None)
        if not user:
            raise Exception("Failed to retrieve threads user")
        
        organization_id = user.metadata['organization_id']
        agent_id = user.metadata['agent_id']
        xpander = XpanderClient(
            api_key=getenv("AGENT_CONTROLLER_API_KEY", ""),
            base_url=getenv("AGENT_CONTROLLER_URL", ""),
            organization_id=organization_id,
        )
        threads = Memory.fetch_user_threads(
            agent={"id": agent_id, "configuration": xpander.configuration, "userDetails": {"id": filters.userId}}
        )
        
        # filter to current agent only.
        threads = [thread.to_dict() for thread in threads if hasattr(thread,'metadata') and isinstance(thread.metadata,dict) and 'agentId' in thread.metadata and thread.metadata['agentId'] == agent_id]

        threads_list = []
        for thread in threads:
            self.thread_authors_cache[thread.get("id")] = {
                "user_id": filters.userId,
                "organization_id": organization_id,
            }
            threads_list.append(
                ThreadDict(
                    id=thread.get("id"),
                    createdAt=thread.get("createdAt"),
                    name=thread.get("name", "New chat"),
                )
            )

        response = PaginatedResponse(
            data=threads_list,
            pageInfo=PageInfo(hasNextPage=False, startCursor=None, endCursor=None),
        )
        return response

    async def get_thread(self, thread_id: str) -> ThreadDict:
        """
        Retrieve details of a thread.

        Args:
            thread_id (str): Thread identifier.

        Returns:
            ThreadDict: Thread details if found, else None.
        """
        user: User = cl.user_session.get("user")
        xpander = XpanderClient(
            api_key=getenv("AGENT_CONTROLLER_API_KEY", ""),
            base_url=getenv("AGENT_CONTROLLER_URL", ""),
            organization_id=user.metadata.get("organization_id"),
        )

        all_user_threads = Memory.fetch_user_threads(
            agent={"configuration": xpander.configuration, "userDetails": {"id": user.identifier}}
        )
        thread_meta = next((trd for trd in all_user_threads if trd.id == thread_id), None)
        if thread_meta:
            thread_meta = thread_meta.to_dict()

        if thread_meta:
            return ThreadDict(
                id=thread_id,
                name=thread_meta.get("name", "New chat"),
                createdAt=thread_meta.get("createdAt"),
                userId=user.identifier,
                userIdentifier=user.identifier,
            )

        return None

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Update a thread's details.

        Args:
            thread_id (str): Thread identifier.
            name (Optional[str]): New name for the thread.
            user_id (Optional[str]): User ID associated with the thread.
            metadata (Optional[Dict]): Additional metadata.
            tags (Optional[List[str]]): List of tags.
        """
        author: dict = self.thread_authors_cache.get(thread_id, None)
        if not author or author == None:
            return

        xpander = XpanderClient(
            api_key=getenv("AGENT_CONTROLLER_API_KEY", ""),
            base_url=getenv("AGENT_CONTROLLER_URL", ""),
            organization_id=author.get("organization_id"),
        )
        if name and isinstance(name, str) and len(name) != 0:
            Memory.rename_thread_by_id({"configuration": xpander.configuration}, thread_id=thread_id, name=name)

    async def delete_user_session(self, id: str) -> bool:
        """
        Delete a user session.

        Args:
            id (str): Session identifier.

        Returns:
            bool: True if deleted, False otherwise.
        """
        pass

    async def build_debug_url(self) -> str:
        """
        Build a debug URL.

        Returns:
            str: Debug URL.
        """
        pass

class ChainlitAdapter(SDKAdapter):
    """
    Adapter class for integrating Chainlit with xpander.ai.

    This class extends SDKAdapter and provides methods to interact with Chainlit while utilizing
    xpander.ai's capabilities. It manages tool calls, tasks, and thread IDs.

    Attributes:
        agent (SDKAdapter): Inherited agent instance.
    """

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: Optional[str] = None,
        organization_id: Optional[str] = None,
        user: Optional[User] = None,
        with_agent_end_tool: Optional[bool] = False,
        should_reset_cache: Optional[bool] = False,
        with_metrics_report: Optional[bool] = False,
        version: Optional[int] = None
    ):
        """
        Initialize the ChainlitAdapter.

        Args:
            api_key (str): The API key for authentication with xpander.ai.
            agent_id (str): The ID of the xpander.ai agent.
            base_url (Optional[str], optional): The base URL for the xpander.ai API. Defaults to None.
            organization_id (Optional[str], optional): The organization ID, if applicable. Defaults to None.
            with_metrics_report (Optional[bool], optional): If to auto-report metrics (llm & execution). Default to False.
        """
        super().__init__(
            api_key=api_key,
            agent_id=agent_id,
            base_url=base_url,
            organization_id=organization_id,
            should_reset_cache=should_reset_cache,
            with_metrics_report=with_metrics_report,
            version=version
        )
        
        if not with_agent_end_tool:
            self.agent.disable_agent_end_tool()  # No need since SmolAgents handles it.
        
        self.named_threads = set()
        self.execution_tool_calls: Dict[str, list[str]] = {}
        
        if user:
            self.agent.update_user_details(
                user_details=UserDetails(
                    id=user.identifier,
                    first_name=user.metadata.get("first_name", ""),
                    last_name=user.metadata.get("last_name", ""),
                    email=user.metadata.get("email", ""),
                    additional_attributes=user.metadata
                    )
                )

    def get_system_prompt(self) -> str:
        """
        Retrieve the system prompt with additional instructions for interactive chat.

        Returns:
            str: The formatted system prompt.
        """
        return super().get_system_prompt() + (
            "\nImportant: You are an assistant engaged in an interactive chat. "
            "Always communicate your reasoning, decisions, and actions to the user. "
            "When performing tool calls, clearly explain what you are doing, why you are doing it, "
            "and what results you expect. "
            "Provide insights into your thought process at each step to ensure transparency and clarity."
        )

    def get_tools(self, llm_provider: LLMProvider = LLMProvider.OPEN_AI) -> List[Any]:
        """
        Retrieve the tools available for the specified LLM provider.

        Args:
            llm_provider (LLMProvider, optional): The LLM provider. Defaults to LLMProvider.OPEN_AI.

        Returns:
            List[Any]: A list of available tools.
        """
        return self.agent.get_tools(llm_provider=llm_provider)

    def get_thread_id(self) -> Optional[str]:
        """
        Retrieve the thread ID associated with the Chainlit session.

        Returns:
            Optional[str]: The thread ID if available, otherwise None.
        """
        return cl.user_session.get("xpander_thread_id", None)

    async def add_task(
        self,
        input: Any,
        files: Optional[List[Any]] = None,
        use_worker: bool = False,
        thread_id: Optional[str] = None,
    ):
        """
        Add a task to the agent and associate it with the Chainlit thread.

        This function ensures that message editing is handled correctly by identifying
        and updating messages in the agent's memory. If an edit is detected, it updates 
        the message history accordingly before adding the new task.

        Args:
            input (Any): The input for the task.
            files (Optional[List[Any]], optional): Additional files for processing. Defaults to None.
            use_worker (bool, optional): Whether to use a worker. Defaults to False.
            thread_id (Optional[str], optional): The thread ID for association. Defaults to None.

        Returns:
            None
        """

        # Check if the task is an edit operation based on existing messages
        if self.agent.execution and self.agent.messages:
            agent_messages = self.agent.messages

            cl_user_messages = [msg for msg in cl.chat_context.get() if msg.type == "user_message"]
            agent_user_messages = [msg for msg in agent_messages if msg['role'] == "user"]

            is_edit = len(cl_user_messages) <= len(agent_user_messages)

            if is_edit:
                # If it's an edit, reconstruct the message history up to the last known user message
                updated_thread = []

                for ag_msg in agent_messages:
                    if ag_msg['role'] != "user":
                        updated_thread.append(ag_msg)
                    else:
                        matching_cl_message = next((msg for msg in cl_user_messages if msg.content == ag_msg['content']), None)
                        if matching_cl_message:
                            updated_thread.append(ag_msg)
                        else:
                            break

                self.agent.memory.update_messages(updated_thread)

        # Add the new task to the agent
        super().add_task(input=input, files=files, use_worker=use_worker, thread_id=thread_id)

        # Store the xpander.ai thread ID in the user session
        cl.user_session.set("xpander_thread_id", self.agent.execution.memory_thread_id)


    def aggregate_tool_calls_stream(
        self,
        tool_calls: Optional[Dict[int, ToolCall]] = None,
        tool_call_requests: Optional[List[Any]] = None,
        completion_response: Any = None

    ) -> Dict[int, ChainlitToolCallWithLLMResponse]:
        """
        Aggregate tool calls from tool call requests.

        Args:
            tool_calls (Optional[Dict[int, ChainlitToolCallWithLLMResponse]], optional): Existing tool calls. Defaults to None.
            tool_call_requests (Optional[List[Any]], optional): List of tool call requests. Defaults to None.

        Returns:
            Dict[int, ChainlitToolCallWithLLMResponse]: Aggregated tool calls.
        """
        if not tool_calls:
            tool_calls: Dict[int, ChainlitToolCallWithLLMResponse] = {}

        if tool_call_requests:
            for tc in tool_call_requests:
                if tc.index not in tool_calls:
                    tool_calls[tc.index] = ChainlitToolCallWithLLMResponse(
                        tool_call=ToolCall(
                            name=tc.function.name,
                            tool_call_id=tc.id,
                            type=ToolCallType.XPANDER if not tc.function.name.startswith("xpLocal") else ToolCallType.LOCAL,
                            payload="",
                        ),
                        completion_response=completion_response
                    )
                   
                else:
                    tool_calls[tc.index].tool_call.payload += tc.function.arguments
                    completion_response['choices'][0]['delta']['tool_calls'] = [{"function":{"arguments": tool_calls[tc.index].tool_call.payload}}]
                    tool_calls[tc.index].completion_response = completion_response
        
        return tool_calls

    def get_custom_graph_items(self, tool_name: str) -> GraphItem:
        random_uuid = get_uuid()
        if tool_name == "xpsleep-agent-delay":
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Sleep", type=AgentGraphItemType.TOOL)
        elif tool_name == "xpstorage-save":
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Save Item to Storage", type=AgentGraphItemType.TOOL)
        elif tool_name == "xpstorage-search":
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Search Items in Storage", type=AgentGraphItemType.TOOL)
        elif tool_name == "xpstorage-get-last-item":
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Retrieve Latest Item from Storage", type=AgentGraphItemType.TOOL)
        elif tool_name.startswith("xpkbs"):
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Search Knowledge Base", type=AgentGraphItemType.TOOL)
        elif tool_name.startswith("xpkba"):
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Adding items to Knowledge Base", type=AgentGraphItemType.TOOL)
        elif tool_name.startswith("xpcoder"):
            return GraphItem(agent=self.agent, id=random_uuid, item_id=random_uuid, name="Running Coding Agent", type=AgentGraphItemType.TOOL)
        return

    
    async def process_tool_calls(self,run_id: str, tool_calls: Dict[int, ChainlitToolCallWithLLMResponse], is_sequence_agent: bool = False, sequence_agent_graph_items:List[GraphItem] = [], reported_sequence_sub_agent_ids: set = set(), on_node_enter: Optional[Callable] = None, on_node_error: Optional[Callable] = None, has_dedicated_workers: Optional[bool] = None, agent_emoji: Optional[str] = None, agent_custom_functions: list[GraphItem] = [], local_tools: Dict[str, Callable] = None) -> str | None:
        """
        Process tool calls by formatting their payloads and executing them.

        Args:
            tool_calls (Dict[int, ChainlitToolCallWithLLMResponse]): The tool calls to process.
        """
        xpander_step = cl.Step(name="xpander-ai", type="tool", parent_id=run_id)
        await xpander_step.send()
        
        current_execution = self.agent.execution.to_dict()
        user_settings = cl.user_session.get("user_settings",{})
        is_debug_mode_active = user_settings.get("debug_mode", True)
        is_max_tool_call_reached = False
        
        is_sub_agent = True if "parentExecution" in current_execution and current_execution['parentExecution'] else False
        
        for tc_raw in tool_calls.values():
            tc = tc_raw.tool_call
            if tc.payload:
                tc.payload = json.loads(tc.payload)

        tool_calls_list: list[ToolCall] = [tc.tool_call for tc in tool_calls.values()]

        # Count tool calls per execution
        execution_id = self.agent.execution.id

        # if execution_id in self.execution_tool_calls:
            # Check max tool call count
            # if len(self.execution_tool_calls[execution_id]) >= MAX_TOOL_CALLS:
                # is_max_tool_call_reached = True
                
        self.agent.add_messages(
            messages=[
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "name": tc.name,
                            "payload": json.dumps(tc.payload),
                            "tool_call_id": tc.tool_call_id,
                        }
                        for tc in tool_calls_list
                    ],
                    "completion_response": tool_calls[0].completion_response
                }
            ]
        )
        
        def get_custom_function_graph_item(tc: ToolCall) -> GraphItem | None:
            return next((gi for gi in agent_custom_functions if gi.name == tc.name or gi.name.replace(" ","_") == tc.name),None)
        
        await xpander_step.remove()
        
        # sequence - manually add the sub agents and report to parent
        if is_sequence_agent and not self.agent.id in reported_sequence_sub_agent_ids:
            reported_sequence_sub_agent_ids.add(self.agent.id)
            sub_agent_graph_item = next((gi for gi in sequence_agent_graph_items if gi.item_id == self.agent.id),None)
            if sub_agent_graph_item and on_node_enter:
                await on_node_enter(tool_call=ToolCall(name=self.agent.name,type=ToolCallType.XPANDER),graph_item=sub_agent_graph_item)
            # sleep for animation to work
            await wait(seconds=1)
            
            agent_name = self.agent.name
            if agent_emoji:
                agent_name = f"{agent_emoji} {agent_name}"
                
            seq_sub_item= cl.Step(
                type="tool",
                parent_id=run_id,
                show_input=False,
                default_open=True,
                name=agent_name,
                id=run_id+"_"+self.agent.id
            )
            seq_sub_item.output=None
            await seq_sub_item.send()
        
        for raw_tool_call in tool_calls.values():
            tool_call = raw_tool_call.tool_call
            is_agent_end_tool = True if tool_call.name == AGENT_END_TOOL else False
            
            current_step = cl.Step(type="tool", parent_id=run_id)
            
            # current_step.parent_id = parent_message_id
            current_step.fail_on_persist_error = True # stop in case of repeating error
            current_step.start = current_step.created_at = utc_now()
            
            if not is_debug_mode_active:
                current_step.name = "xpander-ai"
                current_step.show_input = False
            
            graph_item = self.agent.graph.find_node_by_item_id(item_id=tool_call.name) or self.agent.graph.find_node_by_name(name=tool_call.name) or get_custom_function_graph_item(tc=tool_call) or self.get_custom_graph_items(tool_name=tool_call.name)
            tool_name = graph_item.name if graph_item else tool_call.name
            
            is_sub_agent_root = False
            should_send_step = True
            
            tool_agent_id = get_sub_agent_id_from_oas_by_name(agent_name=tool_call.name,oas=self.agent.oas)
            is_sub_agent_execution = False
            if tool_agent_id:
                sub_agent_node = self.agent.graph.find_node_by_item_id(item_id=tool_agent_id)
                if sub_agent_node:
                    is_sub_agent_execution = True
                    if not graph_item:
                        graph_item = sub_agent_node
                    
                    if on_node_enter:
                        await on_node_enter(tool_call=tool_call,graph_item=sub_agent_node)
                    tool_name = sub_agent_node.name
                    
                    if agent_emoji:
                        tool_name = f"{agent_emoji} {tool_name}"
                    
                    current_step.id = run_id+"_"+sub_agent_node.item_id
                    is_sub_agent_root = True
            else:
                # report to parent window
                graph_item = self.agent.graph.find_node_by_item_id(item_id=tool_call.name) or self.agent.graph.find_node_by_name(name=tool_call.name) or get_custom_function_graph_item(tc=tool_call)
                if graph_item and on_node_enter:
                    await on_node_enter(tool_call=tool_call,graph_item=graph_item)
                    
            if is_sub_agent:
                if is_agent_end_tool:
                    current_step.default_open = True
                    agent_name = self.agent.name
                    if agent_emoji:
                        agent_name = f"{agent_emoji} {agent_name}"
                            
                    tool_name = f"{agent_name} - Final Thoughts"
                    should_send_step = False
                else:
                    tool_name = graph_item.name if graph_item else tool_name
                    
            elif is_agent_end_tool:
                tool_name = f"Crafting final answer"
            
            if is_debug_mode_active:
                current_step.name = tool_name
                if is_sub_agent_execution:
                    input_task_str = ""
                    try:
                        input_task_str = tool_call.payload['bodyParams'].get("input_task", "")
                        if not input_task_str:
                            input_task_str = json.dumps(tool_call.payload)
                    except Exception:
                        input_task_str = json.dumps(tool_call.payload)
                    current_step.input = input_task_str
                else:
                    current_step.input = tool_call.payload
            
            if is_sub_agent_root:
                current_step.show_input = True
                current_step.default_open = True
                current_step.output = None
            
            
            if is_sub_agent:
                if not is_sub_agent_root:
                    current_step.parent_id = run_id+"_"+self.agent.id
            # send the step to the UI
            if should_send_step:
                await current_step.send()
            
            # handle local tools
            if tool_call.type == ToolCallType.LOCAL:
                tool_name = tool_call.name.replace("xpLocal_","")
                if not local_tools:
                    raise Exception(f"local_tools not initialized")
                
                tool_fn = local_tools[tool_name] if tool_name in local_tools else None
                if not tool_fn:
                    raise Exception(f"Tool {tool_name} implementation not found!")
                
                # run the local tool
                tool_call_result = ToolCallResult(function_name=tool_call.name,tool_call_id=tool_call.tool_call_id,payload=tool_call.payload,result="",is_success=False,is_error=False)
                try:
                    fn_result = tool_fn(**tool_call.payload)
                    tool_call_result.result = fn_result
                    tool_call_result.is_success = True
                    
                except Exception as e:
                    tool_call_result.result = str(e)
                    tool_call_result.is_error = True
                    if is_debug_mode_active:
                        current_step.is_error = True
                
                
                # report result to the memory
                await current_step.update()
                self.agent.add_tool_call_results(tool_call_results=[tool_call_result])
            else:
                # failures
                if is_max_tool_call_reached:
                    if is_max_tool_call_reached:
                        error = f"Oops! You've reached the maximum allowed tool executions ({MAX_TOOL_CALLS}). Please adjust your input or try again later."
                
                    
                    tool_call_result = ToolCallResult(function_name=tool_call.name,tool_call_id=tool_call.tool_call_id,payload=tool_call.payload,result=error,is_success=False,is_error=True)
                    self.agent.add_tool_call_results(tool_call_results=[tool_call_result])
                    self.agent.add_messages(
                        messages=[
                            {
                                "role": "system",
                                "content": error
                            }
                        ]
                    )
                    
                    current_step.show_input = False
                    current_step.default_open = True
                    current_step.output = error
                    if should_send_step:
                        await current_step.update()
                    raise Exception(error)
                else: # execute the tool
                    tool_call_result = await make_async(self.agent.run_tool)(tool=tool_call, payload_extension={"headers":{"x-xpander-source-node-type": SourceNodeType.ASSISTANT.value.lower()}})
                    
                    # check if has dedicated worker and wait for result. let the user refresh the result
                    if graph_item and graph_item.type.value == AgentGraphItemType.AGENT.value and has_dedicated_workers:
                        return "waiting_for_sub_agent_result"
                    
            
            current_step.end = utc_now()
            
            if not tool_call_result.is_success and is_debug_mode_active:
                current_step.is_error = True
                if on_node_error:
                    await on_node_error(tool_call_result=tool_call_result,graph_item=graph_item)
            
            if not execution_id in self.execution_tool_calls:
                self.execution_tool_calls[execution_id] = [tool_call_result.function_name]
            else:
                self.execution_tool_calls[execution_id].append(tool_call_result.function_name)
            
            if should_send_step:
                await current_step.update()
            if is_debug_mode_active and not is_sub_agent_root:
                if is_agent_end_tool:
                    current_step.output = tool_call_result.payload['bodyParams']['result']
                    current_step.language = "text"
                else:
                    current_step.output = tool_call_result.result
                    current_step.language = "json"
                    
                if should_send_step:
                    await current_step.update()
                if is_agent_end_tool and not is_sub_agent:
                    if should_send_step:
                        await current_step.remove()
                    tool_calls.clear()
                    return tool_call_result.payload['bodyParams']['result']

        # Reset tool calls
        tool_calls.clear()
