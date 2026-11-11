from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False)

    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_password_byte_length(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return password
