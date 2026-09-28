from pydantic import BaseModel, ConfigDict


class FrameworkBase(BaseModel):
    name: str
    version: str | None = None
    description: str | None = None
    enabled: bool = True


class FrameworkCreate(FrameworkBase):
    pass


class FrameworkResponse(FrameworkBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class FrameworkControlBase(BaseModel):
    control_id: str
    title: str
    description: str | None = None
    function: str | None = None
    category: str | None = None
    reference: str | None = None
    enabled: bool = True


class FrameworkControlCreate(FrameworkControlBase):
    pass


class FrameworkControlResponse(FrameworkControlBase):
    id: int
    framework_id: int

    model_config = ConfigDict(
        from_attributes=True
    )