from pydantic import BaseModel


class ToolActionRequest(BaseModel):
    agent_id: int
    tool_name: str
    action: str
    resource: str