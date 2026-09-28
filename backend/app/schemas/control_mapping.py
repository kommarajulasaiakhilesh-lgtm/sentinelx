from pydantic import BaseModel, ConfigDict


class ControlMappingBase(BaseModel):
    framework_control_id: int
    sentinelx_control_id: int
    mapping_status: str = "PARTIALLY_IMPLEMENTED"
    rationale: str | None = None


class ControlMappingCreate(ControlMappingBase):
    pass


class ControlMappingResponse(ControlMappingBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )