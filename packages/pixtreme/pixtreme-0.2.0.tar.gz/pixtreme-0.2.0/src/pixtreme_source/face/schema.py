import cupy as cp
from pydantic import BaseModel, ConfigDict, Field


class PxFace(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    bbox: cp.ndarray = Field(..., description="Bounding box in the format (x1, y1, x2, y2)")
    score: float = Field(..., description="Detection score")
    kps: cp.ndarray | None = Field(default=None, description="Keypoints in the format (x, y)")
    matrix: cp.ndarray | None = Field(default=None, description="Affine transformation matrix")
    embedding: cp.ndarray | None = Field(default=None, description="Face embedding")
    normed_embedding: cp.ndarray | None = Field(default=None, description="Normalized face embedding")
    image: cp.ndarray | None = Field(default=None, description="Face image")
