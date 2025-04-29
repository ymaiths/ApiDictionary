from enum import Enum
from pydantic import BaseModel, Field
from typing import List


class PartOfSpeech(Enum):
    NOUN = "คำนาม"
    VERB = "คำกริยา"
    ADJECTIVE = "คำคุณศัพท์"
    ADVERB = "คำวิเศษณ์"


class SlangDefinition(BaseModel):
    word: str = Field(description="คำสแลงที่ต้องการค้นหา")
    part_of_speech: PartOfSpeech = Field(
        description="หน้าที่ของคำสแลงนี้")
    meaning: str = Field(description="ความหมายของคำสแลงนี้")
    examples: str = Field(description="ตัวอย่างการใช้คำสแลงนี้")
