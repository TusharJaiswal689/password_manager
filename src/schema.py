from pydantic import BaseModel, Field

class CreatePasswordSchema(BaseModel):
    website: str = Field(
        ..., 
        description="The name of the website or service (e.g., Netflix, GitHub)."
    )
    username: str = Field(
        ..., 
        description="The username or email address for the account."
    )
    length: int = Field(
        default=16, 
        ge=8,  # Greater than or equal to 8
        le=64, # Less than or equal to 64
        description="Total length of the password. Must be between 8 and 64."
    )
    symbols: int = Field(
        default=2, 
        ge=0, 
        description="Number of special characters."
    )
    digits: int = Field(
        default=4, 
        ge=0, 
        description="Number of numeric digits."
    )

class GetPasswordSchema(BaseModel):
    website: str = Field(..., description="The name of the website.")
    username: str = Field(..., description="The username or email address.")