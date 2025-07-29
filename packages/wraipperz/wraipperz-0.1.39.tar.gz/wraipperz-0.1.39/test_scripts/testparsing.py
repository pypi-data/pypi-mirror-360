from typing import Optional, List
from pydantic import BaseModel, Field
from src.wraipperz.parsing.yaml_utils import pydantic_to_yaml_example
import yaml

class LineAnalysis(BaseModel):
    """Analysis of a single dialogue line from video."""

    action: str = Field(
        json_schema_extra={
            "example": "Character looks worried and fidgets with their hands",
            "comment": "Description of the character's actions or expressions",
        }
    )

    voice_type: str = Field(
        json_schema_extra={
            "example": "NORMAL",
            "comment": "Voice type: VO for voice over, OFF for offscreen, WHISPER for whispers, or NORMAL for normal voices",
        }
    )

    location: str = Field(
        json_schema_extra={
            "example": "Living room",
            "comment": "The location where the dialogue takes place",
        }
    )

    time_of_day: str = Field(
        json_schema_extra={
            "example": "DAY",
            "comment": "Time of day (e.g., DAY, NIGHT, MORNING, etc.)",
        }
    )

    translation: str = Field(
        json_schema_extra={
            "example": "I can't believe this is happening.",
            "comment": "High-quality English translation of the dialogue",
        }
    )

    scene_change: Optional[str] = Field(
        default="",
        json_schema_extra={
            "example": "Characters move to the kitchen to prepare dinner",
            "comment": "Brief description of scene change if any, empty if no scene change",
        },
    )

class VideoAnalysisResponse(BaseModel):
    """Complete video analysis response containing all line analyses."""

    lines: List[LineAnalysis] = Field(
        json_schema_extra={
            "comment": "Analysis for each line of dialogue in the script, in order"
        }
    )

def test_class(class_ref):
    yaml_example = pydantic_to_yaml_example(class_ref)
    print(f"\nGenerated YAML:\n{yaml_example}")
    parsed_data = yaml.safe_load(yaml_example)
    class_ref.model_validate(parsed_data)
    instance_test = class_ref(**parsed_data)
    print(f"\nInstance test:\n{instance_test}")



class BadJsonSchema(BaseModel):
    field: str = Field(json_schema_extra="not a dict")  # Will cause AttributeError

class NoneJsonSchema(BaseModel):
    field: str = Field(json_schema_extra=None)  # Might cause issues


test_class(VideoAnalysisResponse)
# test_class(BadJsonSchema)
test_class(NoneJsonSchema)