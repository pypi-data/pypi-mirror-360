from typing import Optional
from pydantic import BaseModel

class CodeGenRequest(BaseModel):
    file_contents: list[dict]
    directory_structure: str
    instruction: str
    api_key: str
    provider: str
    model_choice: str

class Files(BaseModel):
    name: str
    content: str

class CodeGenResponse(BaseModel):
    status: str
    response: Optional[dict] = None