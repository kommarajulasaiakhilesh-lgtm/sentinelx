from pydantic import BaseModel, ConfigDict


class SentinelXControlBase(BaseModel):
    control_id: str
    name: str
    description: str | None = None
    category: str | None = None
    implementation_status: str = "IMPLEMENTED"
    enabled: bool = True


class SentinelXControlCreate(SentinelXControlBase):
    pass


class SentinelXControlResponse(SentinelXControlBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )