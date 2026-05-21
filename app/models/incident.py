from pydantic import BaseModel


class IncidentMetadata(BaseModel):

    service: str
    severity: str
    source: str


class IncidentDocument(BaseModel):

    incident: str
    metadata: IncidentMetadata