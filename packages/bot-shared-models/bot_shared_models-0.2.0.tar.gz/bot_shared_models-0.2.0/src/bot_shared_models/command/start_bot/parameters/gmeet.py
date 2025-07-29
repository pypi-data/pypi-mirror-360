from pydantic import Field, BaseModel


class GmeetBotParameters(BaseModel):
    meeting_id: str = Field(description="The ID of the Google Meet meeting to join.")
