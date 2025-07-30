import random
import string
import asyncio
from uuid import uuid4

def generate_tool_call_id() -> str:
    """
    Generate a unique tool call ID.

    The ID consists of a fixed prefix "call_" followed by a randomly 
    generated alphanumeric string of length 24.

    Returns:
        str: A unique tool call ID in the format "call_<random_string>".
    """
    prefix = "call_"
    characters = string.ascii_letters + string.digits
    length = 24
    random_string = ''.join(random.choices(characters, k=length))
    
    return prefix + random_string

def get_sub_agent_id_from_oas_by_name(agent_name: str, oas: dict) -> str | None:
    return next(
        (k.lstrip('/') for k in oas.get("paths", {}) if oas["paths"][k].get("get", {}).get("operationId") == agent_name),
        None
    )

async def wait(seconds: int):
    await asyncio.sleep(seconds)

def get_uuid() -> str:
    return str(uuid4())