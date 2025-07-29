from enum import StrEnum


class SessionState(StrEnum):
    CREATED = "created"
    WAITING_INVITATION_CONFIRMATION = "waiting_invitation_confirmation"
    BOT_RECORDING = "bot_recording"
    FINISHED = "finished"
