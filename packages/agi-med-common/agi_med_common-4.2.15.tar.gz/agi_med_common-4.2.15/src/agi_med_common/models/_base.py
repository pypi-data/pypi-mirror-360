from pydantic import ConfigDict, BaseModel


class _Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
