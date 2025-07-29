from pydantic import BaseModel, Field
from .session_state import SessionState


class StateMessage(BaseModel):
    state: SessionState = Field(
        description="The new state of the session.",
    )
