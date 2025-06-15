from typing import List
from pydantic import BaseModel, Field

class KeywordSuggestion(BaseModel):
    section: str = Field(..., description="Resume section title")
    subsection: str = Field(..., description="Resume subsection title")
    category: str = Field(..., description="e.g. Technical Skills, Tools & Technologies")
    keywords: List[str] = Field(..., description="List of extracted keywords")
    suggestions: List[str] = Field(..., description="Actionable bullet-point suggestions")

class ResumeMatchOutput(BaseModel):
    existing: List[KeywordSuggestion] = Field(..., description="Already present keywords with emphasis suggestions")
    missing: List[KeywordSuggestion] = Field(..., description="Absent or under-emphasized keywords with rewrite suggestions")

