from __future__ import annotations

from pydantic import Field, BaseModel, ConfigDict


class AdataInfo(BaseModel):
    """Input schema for the adata tool."""

    sampleid: str | None = Field(default=None, description="adata sampleid")
    adtype: str = Field(
        default="exp",
        description="The input adata.X data type for preprocess/analysis/plotting",
    )

    model_config = ConfigDict(extra="ignore")
