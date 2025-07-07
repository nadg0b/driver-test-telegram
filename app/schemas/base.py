from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BaseAPISchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime