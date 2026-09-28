from pydantic import BaseModel, ConfigDict


class EvidenceBase(BaseModel):
    sentinelx_control_id: int
    evidence_type: str
    source: str
    description: str | None = None
    reference: str | None = None
    evidence_status: str = "AVAILABLE"


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceResponse(EvidenceBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )