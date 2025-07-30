from typing import Literal
from pydantic import BaseModel, Field
from pydantic import HttpUrl

class PikaffectsInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt describing the desired video effect.",
    )
    
    image: HttpUrl | str = Field(
        ...,
        title="Image",
        json_schema_extra={"x-sr-order": 301},
        description="URL of the image to use for video generation.",
    )
    
    pikaffect: Literal[
        "Melt", "Cake-ify", "Crumble", "Crush", "Decapitate", 
        "Deflate", "Dissolve", "Explode", "Eye-pop", "Inflate", 
        "Levitate", "Peel", "Poke", "Squish", "Ta-da", "Tear"
    ] = Field(
        default="Melt",
        json_schema_extra={"x-sr-order": 302},
        description="The effect to apply to the image."
    )
    