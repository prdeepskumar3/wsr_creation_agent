from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    """Convert a snake_case Python field name to a camelCase API field name."""
    parts = value.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


class ApiDTO(BaseModel):
    """Base DTO for public API contracts.

    Python code uses snake_case attributes. JSON payloads use camelCase aliases.
    Extra fields are rejected so API contracts stay predictable.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )
