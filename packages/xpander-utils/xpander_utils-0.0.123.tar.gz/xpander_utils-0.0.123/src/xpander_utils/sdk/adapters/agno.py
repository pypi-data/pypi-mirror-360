import json
import time
from typing import Dict, Optional, List, Any, Callable, Tuple, Literal
from agno.tools import tool
from xpander_sdk import ToolCall, ToolCallType, UserDetails, Agent, LLMTokens, Tokens

try:
    from agno.storage.base import Storage
    from agno.storage.session import Session
    from agno.utils.log import logger
    AGNO_STORAGE_AVAILABLE = True
except ImportError:
    AGNO_STORAGE_AVAILABLE = False
    Storage = object
    Session = object

from .base import SDKAdapter


class AgnoStorage(Storage):
    """Storage adapter that syncs agno messages to xpander.ai Memory system."""

    def __init__(self, xpander_client, agent_id: str, agent_instance, user_id: Optional[str] = None):
        if not AGNO_STORAGE_AVAILABLE:
            raise ImportError("agno storage components not available. Please install agno to use AgnoStorage.")
            
        super().__init__("agent")
        self.agent: Agent = agent_instance
        self.default_user_id = user_id

    def _sync_messages_to_xpander(self, session: Session):
        """Sync session messages to xpander memory."""
        if not hasattr(session, 'memory') or not session.memory:
            return
                
        messages = session.memory.get('messages', [])
        if not messages:
            return
                
        # Set user details if provided
        user_id = getattr(session, 'user_id', self.default_user_id)
        if user_id:
            self.agent.update_user_details(
                user_details=UserDetails(id=user_id, email=f"{user_id}@example.com")
            )
        
        # Convert and filter new messages
        messages_to_append = []
        existing_messages = {(msg["role"], msg["content"]) for msg in self.agent.messages}
        
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if (role, content) not in existing_messages:
                    xpander_msg = {"role": role, "content": content}
                    if "tool_calls" in msg:
                        xpander_msg["tool_calls"] = msg["tool_calls"]
                    messages_to_append.append(xpander_msg)
        
        if messages_to_append:
            self.agent.add_messages(messages=messages_to_append)

    # Required Storage interface methods (simplified)
    def create(self) -> None: pass
    def read(self, session_id: str, user_id: Optional[str] = None) -> Optional[Session]: return None
    def get_all_session_ids(self, user_id: Optional[str] = None, entity_id: Optional[str] = None) -> List[str]: return []
    def get_all_sessions(self, user_id: Optional[str] = None, entity_id: Optional[str] = None) -> List[Session]: return []
    def get_recent_sessions(self, user_id: Optional[str] = None, entity_id: Optional[str] = None, limit: Optional[int] = 2) -> List[Session]: return []
    def delete_session(self, session_id: Optional[str] = None): pass
    def drop(self) -> None: pass
    def upgrade_schema(self) -> None: pass
    def serialize(self, data: dict) -> str: return json.dumps(data)
    def deserialize(self, data: str) -> dict: return json.loads(data)

    def upsert(self, session: Session) -> Optional[Session]:
        """Insert or update a session and sync its messages to xpander."""
        try:
            session.updated_at = int(time.time())
            if not hasattr(session, 'created_at') or not session.created_at:
                session.created_at = session.updated_at
            
            self._sync_messages_to_xpander(session)
            return session
        except Exception as e:
            logger.error(f"Error upserting session: {e}")
            return None


class AgnoAdapter(SDKAdapter):
    """Adapter for integrating Agno with xpander.ai."""

    def __init__(self, api_key: str, agent_id: str, base_url: Optional[str] = None, 
                 organization_id: Optional[str] = None, with_metrics_report: Optional[bool] = False):
        super().__init__(api_key=api_key, agent_id=agent_id, base_url=base_url, 
                         organization_id=organization_id, with_metrics_report=with_metrics_report)
        self.agent.disable_agent_end_tool()
        self.agno_responses = []

    def capture_agno_response(self, response):
        """Capture an agno agent response to extract metrics later."""
        if response and hasattr(response, 'metrics'):
            self.agno_responses.append(response)

    @property
    def storage(self) -> "AgnoStorage":
        """Get the AgnoStorage instance for this adapter."""
        return AgnoStorage(
            xpander_client=self.xpander_client,
            agent_id=self.agent.id,
            agent_instance=self.agent,
            user_id=None
        )

    def get_tools(self) -> List[Callable]:
        """
        Retrieve the tools available for the agent as agno-compatible functions.

        Returns:
            List[Callable]: A list of Agno-compatible tool functions.
        """
        xpander_tools = self.agent.get_tools()
        tools = []

        for tool_schema in xpander_tools:
            function_spec = tool_schema["function"]
            tool_name = function_spec["name"]
            tool_description = function_spec["description"]
            
            parameters = function_spec.get("parameters", {})
            properties = parameters.get("properties", {})
            required_params = parameters.get("required", [])

            agno_tool_func = self._create_agno_tool_function(
                tool_name=tool_name,
                tool_description=tool_description,
                properties=properties,
                required_params=required_params
            )

            tools.append(agno_tool_func)

        return tools

    def _create_agno_tool_function(self, tool_name: str, tool_description: str, 
                                   properties: Dict, required_params: List[str]) -> Callable:
        """Create a dynamic agno tool function from xpander tool schema."""
        
        def dynamic_tool_function(**kwargs) -> str:
            """Execute a tool by calling the xpander.ai agent's tool execution API."""
            
            body_params = {}
            query_params = {}
            path_params = {}

            if "bodyParams" in properties and "properties" in properties["bodyParams"]:
                # Nested structure (like email tool)
                body_param_props = properties["bodyParams"]["properties"]
                query_param_props = properties.get("queryParams", {}).get("properties", {})
                path_param_props = properties.get("pathParams", {}).get("properties", {})
                
                for param_name, param_value in kwargs.items():
                    if param_name in body_param_props:
                        body_params[param_name] = param_value
                    elif param_name in query_param_props:
                        query_params[param_name] = param_value
                    elif param_name in path_param_props:
                        path_params[param_name] = param_value
                    else:
                        body_params[param_name] = param_value
            else:
                # Flat parameter structure
                for param_name, param_value in kwargs.items():
                    if param_name in properties:
                        param_desc = properties[param_name].get("description", "").lower()
                        if "query" in param_desc and "path" not in param_desc:
                            query_params[param_name] = param_value
                        elif "path" in param_desc:
                            path_params[param_name] = param_value
                        else:
                            body_params[param_name] = param_value
                    else:
                        body_params[param_name] = param_value

            xpander_tool_invocation = self.agent.run_tool(
                tool=ToolCall(
                    name=tool_name,
                    type=ToolCallType.XPANDER,
                    payload={
                        "bodyParams": body_params,
                        "queryParams": query_params,
                        "pathParams": path_params
                    }
                )
            )

            if not xpander_tool_invocation.is_success:
                error_result = json.dumps(xpander_tool_invocation.result)
                raise Exception(f"Error running tool {tool_name}: {error_result}")

            # Return the raw result like regular agno tools
            return json.dumps(xpander_tool_invocation.result)

        # Set function metadata
        dynamic_tool_function.__name__ = tool_name
        dynamic_tool_function.__doc__ = tool_description

        # Create type annotations for agno
        annotations = self._build_annotations(properties, required_params)
        annotations['return'] = str
        dynamic_tool_function.__annotations__ = annotations

        # Apply the @tool decorator
        decorated_function = tool(
            name=tool_name,
            cache_results=True,
            show_result=False,
            description=tool_description
        )(dynamic_tool_function)
        
        if hasattr(decorated_function, '__name__'):
            decorated_function.__name__ = tool_name
            
        # Set parameter schema for agno
        parameter_schema = self._build_parameter_schema(properties, required_params)
        if hasattr(decorated_function, 'parameters'):
            decorated_function.parameters = parameter_schema
        
        return decorated_function

    def _collect_parameters(self, properties: Dict, required_params: List[str]) -> Tuple[Dict, List[str]]:
        """Collect all parameters from nested or flat structure."""
        if "bodyParams" in properties and "properties" in properties["bodyParams"]:
            all_param_props = {}
            all_required = []
            
            for section in ["bodyParams", "queryParams", "pathParams"]:
                if section in properties and "properties" in properties[section]:
                    section_props = properties[section].get("properties", {})
                    section_required = properties[section].get("required", [])
                    all_param_props.update(section_props)
                    all_required.extend(section_required)
            
            return all_param_props, all_required
        else:
            return properties, required_params

    def _build_annotations(self, properties: Dict, required_params: List[str]) -> Dict:
        """Build type annotations for the dynamic function."""
        all_param_props, all_required = self._collect_parameters(properties, required_params)
        annotations = {}
        
        for param_name, param_spec in all_param_props.items():
            param_type = self._get_python_type(param_spec.get("type", "string"))
            if param_name not in all_required:
                param_type = Optional[param_type]
            annotations[param_name] = param_type

        return annotations

    def _build_parameter_schema(self, properties: Dict, required_params: List[str]) -> Dict:
        """Build parameter schema for agno."""
        all_param_props, all_required = self._collect_parameters(properties, required_params)
        return {
            "type": "object",
            "properties": all_param_props,
            "required": all_required
        }

    def _get_python_type(self, json_type: str) -> type:
        """Convert JSON schema type to Python type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": List[Any],
            "object": Dict[str, Any]
        }
        return type_mapping.get(json_type, Any)

    def get_system_prompt(self) -> str:
        """Retrieve the system prompt for the agent."""
        agent_role = "\n".join(self.agent.instructions.role)
        agent_goal = "\n".join(self.agent.instructions.goal)
        return f"""Agent general instructions: "{self.agent.instructions.general}"
Agent role instructions: "{agent_role}"
Agent goal instructions: "{agent_goal}\"""" 

    def complete_execution(self, agno_agent=None, result: str = "Agno conversation completed"):
        """Complete the xpander execution to create a thread."""
        if not hasattr(self.agent, 'execution') or not self.agent.execution:
            return None

        # Sync messages from agno agent if provided
        if agno_agent:
            synced_messages = self._sync_agno_messages(agno_agent)
            if synced_messages:
                # Use last assistant message as result
                for msg in reversed(synced_messages):
                    if msg.get("role") == "assistant":
                        result = msg.get("content", result)
                        break

        try:
            # Complete execution
            self.agent.stop_execution(is_success=True, result=result)
            
            # Report metrics
            self._report_metrics(agno_agent)
            
            # Finalize and get thread ID
            final_result = self.agent.retrieve_execution_result()
            if hasattr(final_result, 'memory_thread_id'):
                return final_result.memory_thread_id
            
        except Exception as e:
            logger.error(f"Error completing execution: {e}")
        
        return None

    def _sync_agno_messages(self, agno_agent) -> List[Dict]:
        """Extract and sync messages from agno agent to xpander."""
        messages = []
        
        # Try multiple methods to get messages
        if hasattr(agno_agent, 'memory') and agno_agent.memory:
            try:
                if hasattr(agno_agent.memory, 'get_messages_for_session') and hasattr(agno_agent, 'session_id'):
                    messages = agno_agent.memory.get_messages_for_session(agno_agent.session_id) or []
                elif hasattr(agno_agent.memory, 'get_messages_from_last_n_runs'):
                    messages = agno_agent.memory.get_messages_from_last_n_runs(10) or []
            except:
                pass
                
        if not messages and hasattr(agno_agent, 'run_messages'):
            messages = agno_agent.run_messages or []

        # Convert to xpander format
        messages_to_sync = []
        existing_messages = {(msg["role"], msg["content"]) for msg in self.agent.messages}
        
        for msg in messages:
            xpander_msg = None
            
            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                xpander_msg = {"role": msg.role, "content": msg.content}
            elif isinstance(msg, dict):
                xpander_msg = {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                }
                if "tool_calls" in msg:
                    xpander_msg["tool_calls"] = msg["tool_calls"]
            elif isinstance(msg, str):
                xpander_msg = {"role": "user", "content": msg}
            
            if xpander_msg and (xpander_msg["role"], xpander_msg["content"]) not in existing_messages:
                messages_to_sync.append(xpander_msg)
        
        if messages_to_sync:
            self.agent.add_messages(messages=messages_to_sync)
            
        return messages_to_sync

    def _report_metrics(self, agno_agent):
        """Report token metrics to xpander."""
        try:
            if self.agno_responses:
                # Use real agno metrics
                total_completion_tokens = sum(sum(r.metrics.get('completion_tokens', [0])) for r in self.agno_responses if hasattr(r, 'metrics') and r.metrics)
                total_prompt_tokens = sum(sum(r.metrics.get('prompt_tokens', [0])) for r in self.agno_responses if hasattr(r, 'metrics') and r.metrics)
                total_tokens = sum(sum(r.metrics.get('total_tokens', [0])) for r in self.agno_responses if hasattr(r, 'metrics') and r.metrics)
                
                ai_model = next((r.model for r in self.agno_responses if hasattr(r, 'model')), "agno-agent")
            else:
                # Estimate tokens
                total_chars = sum(len(msg.get("content", "")) for msg in self.agent.messages)
                total_tokens = max(100, total_chars // 4)
                total_completion_tokens = total_tokens // 2
                total_prompt_tokens = total_tokens // 2
                
                ai_model = "agno-agent"
                if agno_agent and hasattr(agno_agent, 'model'):
                    if hasattr(agno_agent.model, 'id'):
                        ai_model = agno_agent.model.id
                    elif isinstance(agno_agent.model, str):
                        ai_model = agno_agent.model

            llm_tokens = Tokens(
                worker=LLMTokens(
                    completion_tokens=total_completion_tokens,
                    prompt_tokens=total_prompt_tokens,
                    total_tokens=total_tokens
                )
            )
            
            self.agent.report_execution_metrics(
                llm_tokens=llm_tokens,
                ai_model=ai_model,
                source_node_type="agno"
            )
        except Exception as e:
            logger.error(f"Error reporting metrics: {e}") 