from .base import BaseEntity, BaseRepository


class AgentFunction(BaseEntity):
    def __init__(
        self,
        id: str = None,
        agent_id: str = None,
        name: str = None,
        code: str = None,
        code_path: str = None,
        is_multifile: bool = False,
        language: str = "python",
        created_at: str = None,
        updated_at: str = None,
        deleted_at: str = None,
    ):
        self.id = id
        self.agent_id = agent_id
        self.name = name
        self.code = code
        self.code_path = code_path
        self.is_multifile = is_multifile
        self.language = language
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at or None


class AgentFunctionRepository(BaseRepository[AgentFunction]):
    def __init__(self, agent_id: str):
        super().__init__("agent", f"/v1/agents/{agent_id}/functions", AgentFunction)
