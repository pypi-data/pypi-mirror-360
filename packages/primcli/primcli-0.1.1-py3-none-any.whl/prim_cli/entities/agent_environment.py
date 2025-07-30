from .base import BaseEntity, BaseRepository


class AgentEnvironment(BaseEntity):
    def __init__(
        self,
        id: str = None,
        agent_id: str = None,
        name: str = None,
        function_id: str = None,
        phone_number: str = None,
        stt_model: str = "nova-3",
        stt_endpointing: int = 300,
        stt_language: str = "en",
        stt_prompt: str = "",
        recording_enabled: bool = False,
        redaction_enabled: bool = False,
        created_at: str = None,
        updated_at: str = None,
        deleted_at: str = None,
    ):
        self.id = id
        self.agent_id = agent_id
        self.name = name
        self.function_id = function_id
        self.phone_number = phone_number
        self.stt_model = stt_model
        self.stt_endpointing = stt_endpointing
        self.stt_language = stt_language
        self.stt_prompt = stt_prompt
        self.recording_enabled = recording_enabled
        self.redaction_enabled = redaction_enabled
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at or None


class AgentEnvironmentRepository(BaseRepository[AgentEnvironment]):
    def __init__(self, agent_id: str):
        super().__init__(
            "agent", f"/v1/agents/{agent_id}/environments", AgentEnvironment
        )
